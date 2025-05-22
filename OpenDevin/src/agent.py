import os
import subprocess
import json
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from smolagents import Agent as SmolAgentBase
from .tasks import CreateFileTask, PatchFileTask, ShellCommandTask, EchoTask, ErrorTask

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

class OpenDevinAgent(SmolAgentBase):
    def __init__(self, task: str, api_key: str = None, agent_name: str = "OpenDevinMistralAgent"):
        """
        Initializes the OpenDevin agent with a task and optionally an API key.

        Args:
            task (str): The task description for the agent.
            api_key (str, optional): Mistral AI API key. Defaults to None.
            agent_name (str, optional): Name of the agent.
        """
        super().__init__(agent_name) # Initialize the SmolAgentBase
        self.task = task # Overall goal for the agent
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        self.client = None

        if self.api_key:
            self.client = MistralClient(api_key=self.api_key)
        else:
            # This print will go to server logs, not web UI directly.
            print(f"[WARNING] Agent {self.name}: Mistral AI API key not found. Plan generation might fail. Set MISTRAL_API_KEY.")

    def generate_plan(self, task_string: str) -> list[dict]:
        """
        Generates a plan (list of action dictionaries) based on the task_string using Mistral AI.

        Args:
            task_string (str): The description of the task. (This is now used directly)

        Returns:
            list[dict]: A list of action dictionaries representing the plan.
        """
        if not self.client or not self.api_key: # Check API key specific to this agent instance
            error_msg = "Mistral AI API key not configured for this agent instance or client not initialized."
            # Logging this error to server console.
            print(f"[ERROR_AGENT] {self.name}: {error_msg}")
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
                print(f"[ERROR_AGENT] {self.name}: {error_msg}")
                return [{"action": "error", "args": {"message": error_msg}}]
        except Exception as e:
            error_msg = f"Error during Mistral AI API call: {e}"
            print(f"[ERROR_AGENT] {self.name}: {error_msg}")
            return [{"action": "error", "args": {"message": error_msg}}]

    def translate_plan_to_tasks(self, plan_dicts: list[dict]) -> list:
        task_objects = []
        for i, action_dict in enumerate(plan_dicts):
            action_type = action_dict.get("action")
            args = action_dict.get("args", {})
            task_name = f"Task_{i+1}_{action_type}" # Example task name

            if action_type == "create_file":
                task_objects.append(CreateFileTask(name=task_name, filepath=args.get("filepath"), content=args.get("content", "")))
            elif action_type == "patch_file":
                task_objects.append(PatchFileTask(name=task_name, filepath=args.get("filepath"), patch_content=args.get("patch_content")))
            elif action_type == "shell":
                task_objects.append(ShellCommandTask(name=task_name, command=args.get("command")))
            elif action_type == "echo":
                task_objects.append(EchoTask(name=task_name, message=args.get("message")))
            elif action_type == "error": # From plan generation itself
                task_objects.append(ErrorTask(name=task_name, error_message=args.get("message", "Unknown error from plan generation")))
            else:
                print(f"[WARNING] Agent {self.name}: Unknown action type in plan dict: {action_type}. Creating an ErrorTask.")
                task_objects.append(ErrorTask(name=task_name, error_message=f"Unknown action type: {action_type}"))
        return task_objects

    def perform_smol_task(self, task) -> dict:
        # The task's execute method already prints to console.
        # Here we just call it and return its structured result.
        print(f"Agent {self.name} performing {task.name} ({task.__class__.__name__})") # Optional pre-task log from agent
        result = task.execute(self) # `task.execute` handles its own console prints and builds its log
        # Example: result = {"status": "success", "log": ["log line 1"], ...}
        print(f"Agent {self.name} finished {task.name}. Status: {result.get('status')}") # Optional post-task log
        return result

    def execute_plan(self, tasks: list) -> list[str]: # tasks is now list of Task objects
        all_logs = []
        # This initial message is for CLI. Web UI gets logs from individual tasks.
        cli_initial_message = "\nExecuting Smarter Plan (list of Task objects):"
        print(cli_initial_message) 
        all_logs.append(cli_initial_message) # For web UI to also have this marker

        for task_object in tasks:
            # perform_smol_task calls task.execute(), which prints to console.
            # The result from task.execute() contains its own log list.
            task_result = self.perform_smol_task(task_object)
            
            if task_result and isinstance(task_result.get("log"), list):
                all_logs.extend(task_result["log"]) # Aggregate logs for web UI
            else:
                # Fallback if task_result or its log is not as expected
                error_log_line = f"[AGENT_ERROR] Task {task_object.name} did not return a valid log list in its result."
                print(error_log_line) # For CLI
                all_logs.append(error_log_line)

            if task_result.get("status") == "failure":
                failure_message = f"[AGENT_INFO] Task {task_object.name} reported failure. Stopping plan execution."
                print(failure_message) # For CLI
                all_logs.append(failure_message)
                break # Stop plan on first task failure
        
        return all_logs

    def run_task(self): # This method is more for command-line usage or direct invocation
        """
        Runs the task assigned to the agent (self.task).
        It generates a plan and then executes it, printing logs to console.
        This method is not directly used by the web UI, which calls generate_plan and execute_plan separately.
        """
        print(f"Agent {self.name} starting overall task: {self.task}") # self.task is the main goal
        
        plan_dicts = self.generate_plan(task_string=self.task) # Get dict plan from Mistral
        print("\nGenerated Plan (from Mistral):")
        for i, step_dict in enumerate(plan_dicts):
            print(f"  Step {i+1}: {step_dict.get('action')} - {step_dict.get('args')}")

        task_objects = self.translate_plan_to_tasks(plan_dicts)
        # Optional: Print translated task objects for debugging
        # print("\nTranslated to Task Objects:")
        # for t_obj in task_objects:
        #     print(f"  - {t_obj.name} ({t_obj.__class__.__name__})")

        # execute_plan now takes task_objects and its internal calls print to console
        # It also returns aggregated logs, which run_task (CLI) can optionally print if needed,
        # but individual tasks already print.
        returned_logs = self.execute_plan(task_objects) 
        
        # If you want to see the aggregated logs from execute_plan in CLI (might be redundant as tasks print):
        # print("\n--- Aggregated Logs (from execute_plan return) ---")
        # for log_line in returned_logs:
        #    print(log_line)
        # print("--- End of Aggregated Logs ---")

        print(f"\nAgent {self.name} finished overall task: {self.task}")

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
# No changes needed for filepath handling in this new structure as Tasks handle their own args.
# The previous direct manipulation of filepath in execute_plan is removed.
