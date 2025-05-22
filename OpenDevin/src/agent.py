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
    dir_name = os.path.dirname(filepath)
    if dir_name:  # Only call makedirs if dir_name is not an empty string
        os.makedirs(dir_name, exist_ok=True)
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
        self.task = task # Retain original task for potential other uses, but web UI will pass explicitly.
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        self.client = None

        if self.api_key:
            self.client = MistralClient(api_key=self.api_key)
        else:
            # This print will go to server logs, not web UI directly.
            # Flash messages in routes.py are for UI feedback.
            print("[WARNING]: Mistral AI API key not found for agent instance. Plan generation might fail or use fallback if UI doesn't enforce key presence.")

    def generate_plan(self, task_string: str) -> list[dict]: # task_string is now the primary source for the plan
        """
        Generates a plan based on the provided task string using Mistral AI.

        Args:
            task_string (str): The description of the task. (This is now used directly)

        Returns:
            list[dict]: A list of action dictionaries representing the plan.
        """
        if not self.client or not self.api_key: # Check API key specific to this agent instance
            error_msg = "Mistral AI API key not configured for this agent instance or client not initialized."
            # Logging this error to server console. UI will get specific error message.
            print(f"[ERROR_AGENT]: {error_msg}")
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
                print(f"[ERROR_AGENT]: {error_msg}") # Log to server console
                return [{"action": "error", "args": {"message": error_msg}}]
        except Exception as e:
            error_msg = f"Error during Mistral AI API call: {e}"
            print(f"[ERROR_AGENT]: {error_msg}") # Log to server console
            return [{"action": "error", "args": {"message": error_msg}}]

    def execute_plan(self, plan: list[dict]) -> list[str]:
        """
        Executes a given plan and returns a log of actions.

        Args:
            plan (list[dict]): A list of action dictionaries.
        
        Returns:
            list[str]: A log of execution steps.
        """
        log_output = []
        for action_item in plan:
            action_type = action_item.get("action")
            args = action_item.get("args", {})
            
            attempt_msg = f"Attempting action: {action_type} with args: {args}"
            # Not printing this one as it's more of an internal state before actual execution attempt.
            # It will be part of the log_output for the web UI.
            log_output.append(attempt_msg)

            if action_type == "create_file":
                filepath = str(args.get("filepath", "")).strip()
                content = args.get("content", "")
                if filepath:
                    try:
                        create_file(filepath, content)
                        message = f"[CREATED]: {filepath}"
                        print(message)
                        log_output.append(message)
                    except Exception as e:
                        message = f"[ERROR_CREATE]: Could not create file {filepath}. Error: {e}"
                        print(message)
                        log_output.append(message)
                else:
                    message = "[ERROR_CREATE]: Missing filepath for create_file action."
                    print(message)
                    log_output.append(message)
            elif action_type == "patch_file":
                filepath = args.get("filepath")
                patch_content = args.get("patch_content")
                if filepath and patch_content is not None:
                    try:
                        patch_file(filepath, patch_content)
                        message = f"[PATCHED]: {filepath} with content: {patch_content[:50]}{'...' if len(patch_content) > 50 else ''}"
                        print(message)
                        log_output.append(message)
                    except Exception as e:
                        message = f"[ERROR_PATCH]: Could not patch file {filepath}. Error: {e}"
                        print(message)
                        log_output.append(message)
                else:
                    message = "[ERROR_PATCH]: Missing filepath or patch_content for patch_file action."
                    print(message)
                    log_output.append(message)
            elif action_type == "shell":
                command = args.get("command")
                if command:
                    shell_cmd_msg = f"[SHELL]: {command}"
                    print(shell_cmd_msg)
                    log_output.append(shell_cmd_msg)
                    try:
                        stdout, stderr, rc = run_shell(command)
                        
                        stdout_msg = f"Stdout: {stdout.strip()}"
                        print(stdout_msg)
                        log_output.append(stdout_msg)
                        
                        stderr_msg = f"Stderr: {stderr.strip()}"
                        print(stderr_msg)
                        log_output.append(stderr_msg)
                        
                        rc_msg = f"Return Code: {rc}"
                        print(rc_msg)
                        log_output.append(rc_msg)
                        
                        if rc != 0 or (stderr and stderr.strip()):
                            debug_message = "[DEBUGGING]: Error or non-zero return code detected during shell execution."
                            print(debug_message)
                            log_output.append(debug_message)
                    except Exception as e:
                        message = f"[ERROR_SHELL]: Command '{command}' failed. Error: {e}"
                        print(message)
                        log_output.append(message)
                else:
                    message = "[ERROR_SHELL]: Missing command for shell action."
                    print(message)
                    log_output.append(message)
            elif action_type == "echo":
                message_content = args.get("message")
                if message_content:
                    message = f"[ECHO]: {message_content}"
                    print(message)
                    log_output.append(message)
                else:
                    message = "[ERROR_ECHO]: Missing message for echo action."
                    print(message)
                    log_output.append(message)
            elif action_type == "error": # Action from plan itself is an error
                error_message_content = args.get("message", "Unknown error from plan.")
                message = f"[PLANNED_ERROR]: {error_message_content}"
                print(message)
                log_output.append(message)
            else:
                message = f"[WARNING]: Unknown action type encountered: {action_type}"
                print(message)
                log_output.append(message)
        return log_output

    def run_task(self): # This method is more for command-line usage or direct invocation
        """
        Runs the task assigned to the agent (self.task).
        It generates a plan and then executes it, printing logs to console.
        This method is not directly used by the web UI, which calls generate_plan and execute_plan separately.
        """
        print(f"Starting task (from self.task): {self.task}")
        # Note: generate_plan now expects task_string as an argument.
        # For this internal run_task, we'll use self.task.
        plan = self.generate_plan(task_string=self.task) 
        
        print("Generated Plan:")
        for i, step in enumerate(plan):
            # Using json.dumps for prettier printing of args if they are complex
            args_str = json.dumps(step.get('args', {}))
            print(f"  Step {i+1}: {step['action']} - Args: {args_str}")
        
        print("\nExecuting Plan (results to console):")
        logs = self.execute_plan(plan)
        for log_entry in logs:
            print(log_entry)
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
    # This test is for the console `run_task` method.
    # The web UI will use session-based API key.
    print("Testing agent behavior without API key (for console run_task):")
    # Create a new agent instance specifically for this test, without providing an API key
    # and ensuring it doesn't pick one up from a potentially set environment variable for this test.
    agent3_no_key = OpenDevinAgent(task="this task will show API key error in plan", api_key=None) # Explicitly None
    agent3_no_key.client = None # Force client to be None
    agent3_no_key.api_key = None # Force api_key to be None
    agent3_no_key.run_task() # This will call generate_plan, which should return an error plan
    print("-" * 20)

    # Test case 4: Cleanup created files (manual for now)
    # Example of using run_shell directly for cleanup if needed
    print("Cleaning up created files (if any from __main__ tests)...")
    # Adjust rm command based on expected files from AI-generated plans or specific tests
    # Note: hello.py, snake_game.py were from older versions.
    # script_1_to_10.py, story.txt, numbers.py might be from AI tasks.
    # output.txt might be from main.py's task if run.
    cleanup_command = "rm -f hello.py snake_game.py script_1_to_10.py story.txt numbers.py output.txt || true"
    print(f"Running cleanup: {cleanup_command}")
    stdout, stderr, rc = run_shell(cleanup_command)
    print(f"Cleanup Stdout: {stdout.strip()}")
    print(f"Cleanup Stderr: {stderr.strip()}")
    print(f"Cleanup RC: {rc}")
