import os
import subprocess
import json
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

def create_file(filepath: str, content: str = ""):
    """
    Creates a new file at the specified filepath.

    If content is provided, it writes the content to the file.
    Creates directories if they don't exist in the filepath.

    Args:
        filepath (str): The path to the file to be created.
        content (str, optional): The content to write to the file. Defaults to "".
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        f.write(content)

def run_shell(command: str) -> tuple[str, str, int]:
    """
    Executes a shell command and captures its output.

    Args:
        command (str): The shell command to execute.

    Returns:
        tuple[str, str, int]: A tuple containing stdout, stderr, and the exit code.
    """
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout.decode(), stderr.decode(), process.returncode

def patch_file(filepath: str, patch_content: str):
    """
    Opens a file in write mode (overwrite) and writes the patch_content into it.

    If the file does not exist, it creates it.

    Args:
        filepath (str): The path to the file to be patched.
        patch_content (str): The content to write to the file.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        f.write(patch_content)

class OpenDevinAgent:
    def __init__(self, task: str, api_key: str = None):
        """
        Initializes the OpenDevin agent with a task and optionally an API key.

        Args:
            task (str): The task description for the agent.
            api_key (str, optional): Mistral AI API key. Defaults to None.
        """
        self.task = task
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        self.client = None

        if self.api_key:
            self.client = MistralClient(api_key=self.api_key)
        else:
            print("[WARNING]: Mistral AI API key not found. Plan generation will be skipped. Set MISTRAL_API_KEY environment variable.")

    def generate_plan(self, task_string: str) -> list[dict]:
        """
        Generates a plan based on the provided task string using Mistral AI.

        Args:
            task_string (str): The description of the task.

        Returns:
            list[dict]: A list of action dictionaries representing the plan.
        """
        if not self.client or not self.api_key:
            error_msg = "Mistral AI API key not configured or client not initialized."
            print(f"[ERROR]: {error_msg}")
            return [{"action": "error", "args": {"message": error_msg}}]

        SYSTEM_PROMPT = """You are a helpful assistant that generates execution plans for a software development agent called OpenDevin.
The user will provide a task. Your goal is to break this task down into a series of actionable steps for the agent.
The output MUST be a valid JSON array of objects. Each object represents an action and should have two keys:
1. "action": A string representing the type of action. Supported actions are "create_file", "patch_file", "shell", "echo".
2. "args": An object containing the arguments for that action.
    - For "create_file": {"filepath": "path/to/file.ext", "content": "file content here (can be empty)"}
    - For "patch_file": {"filepath": "path/to/file.ext", "patch_content": "new file content here"}
    - For "shell": {"command": "shell command to execute"}
    - For "echo": {"message": "message to print to console"}

Ensure the JSON is well-formed. Do not add any explanations outside the JSON array.
If the task is too complex or vague, try to create a simple plan that reflects the user's request or ask for clarification via an 'echo' action."""

        user_prompt = f"Generate a plan for the following task: {task_string}"

        try:
            chat_response = self.client.chat(
                model="mistral-small-latest",
                messages=[
                    ChatMessage(role="system", content=SYSTEM_PROMPT),
                    ChatMessage(role="user", content=user_prompt)
                ]
            )
            ai_response_content = chat_response.choices[0].message.content

            try:
                plan = json.loads(ai_response_content)
                return plan
            except json.JSONDecodeError as e:
                error_msg = f"Failed to parse AI response as JSON: {e}. Response: {ai_response_content}"
                print(f"[ERROR]: {error_msg}")
                return [{"action": "error", "args": {"message": error_msg}}]
        except Exception as e:
            error_msg = f"Error during Mistral AI API call: {e}"
            print(f"[ERROR]: {error_msg}")
            return [{"action": "error", "args": {"message": error_msg}}]

    def execute_plan(self, plan: list[dict]):
        """
        Executes a given plan.

        Args:
            plan (list[dict]): A list of action dictionaries.
        """
        for action_item in plan:
            action_type = action_item.get("action")
            args = action_item.get("args", {})

            if action_type == "create_file":
                filepath = args.get("filepath")
                content = args.get("content", "")
                if filepath:
                    create_file(filepath, content)
                    print(f"[CREATED]: {filepath}")
                else:
                    print("[ERROR]: Missing filepath for create_file action.")
            elif action_type == "patch_file":
                filepath = args.get("filepath")
                patch_content = args.get("patch_content")
                if filepath and patch_content is not None:
                    patch_file(filepath, patch_content)
                    print(f"[PATCHED]: {filepath} with content: {patch_content[:50]}{'...' if len(patch_content) > 50 else ''}")
                else:
                    print("[ERROR]: Missing filepath or patch_content for patch_file action.")
            elif action_type == "shell":
                command = args.get("command")
                if command:
                    print(f"[SHELL]: {command}")
                    stdout, stderr, rc = run_shell(command)
                    print(f"Stdout: {stdout.strip()}")
                    print(f"Stderr: {stderr.strip()}")
                    print(f"Return Code: {rc}")
                    if rc != 0 or stderr:
                        print("[DEBUGGING]: Error detected during shell execution.")
                else:
                    print("[ERROR]: Missing command for shell action.")
            elif action_type == "echo":
                message = args.get("message")
                if message:
                    print(f"[ECHO]: {message}")
                else:
                    print("[ERROR]: Missing message for echo action.")
            elif action_type == "error":
                message = args.get("message")
                if message:
                    print(f"[EXECUTION ERROR]: {message}")
                else:
                    print("[EXECUTION ERROR]: Unknown error from plan.")
            else:
                print(f"[WARNING]: Unknown action type: {action_type}")

    def run_task(self):
        """
        Runs the task assigned to the agent.
        It generates a plan and then executes it.
        """
        print(f"Starting task: {self.task}")
        plan = self.generate_plan(self.task)
        print("Generated Plan:")
        for i, step in enumerate(plan):
            print(f"  Step {i+1}: {step['action']} - {step['args']}")
        
        print("\nExecuting Plan:")
        self.execute_plan(plan)
        print("\nTask finished.")

if __name__ == '__main__':
    # Example Usage (optional, for testing purposes)
    # Ensure MISTRAL_API_KEY is set in your environment for this to work
    print("Attempting to run agent. Make sure MISTRAL_API_KEY is set in your environment.")

    # Test case 1: Task requiring AI plan generation
    # This task will use the Mistral AI if the API key is configured.
    agent1 = OpenDevinAgent(task="create a python script that prints numbers from 1 to 10 and then run it")
    agent1.run_task()
    print("-" * 20)

    # Test case 2: Another AI-driven task
    agent2 = OpenDevinAgent(task="write a short story about a robot learning to code to a file named story.txt")
    agent2.run_task()
    print("-" * 20)
    
    # Test case 3: Agent without API Key (to test fallback)
    # Temporarily unset api_key for this test, assuming it might have been picked from env
    print("Testing agent behavior without API key (if it was set via env, this test won't reflect true no-key scenario unless env var is also unset):")
    agent3 = OpenDevinAgent(task="this task will fail plan generation", api_key="INVALID_KEY_OR_NONE") # Force client to be None or fail
    # A bit of a hack: if it was picked from env, self.client might still be valid
    # For a true test, one would need to run this in an env without MISTRAL_API_KEY
    if os.getenv("MISTRAL_API_KEY"):
        print("NOTE: MISTRAL_API_KEY is set in environment. For a true 'no API key' test, unset it.")
    agent3.client = None # Ensure client is None for this specific test instance
    agent3.api_key = None # Ensure api_key is None
    agent3.run_task()
    print("-" * 20)

    # Test case 4: Cleanup created files (manual for now)
    # Example of using run_shell directly for cleanup if needed
    print("Cleaning up created files (if any)...")
    # Adjust rm command based on expected files from AI-generated plans
    stdout, stderr, rc = run_shell("rm hello.py snake_game.py script_1_to_10.py story.txt numbers.py || true")
    print(f"Cleanup Stdout: {stdout.strip()}")
    print(f"Cleanup Stderr: {stderr.strip()}")
    print(f"Cleanup RC: {rc}")
