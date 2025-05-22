import os
import subprocess

def create_file(filepath: str, content: str = ""):
    """
    Creates a new file at the specified filepath.

    If content is provided, it writes the content to the file.
    Creates directories if they don't exist in the filepath.

    Args:
        filepath (str): The path to the file to be created.
        content (str, optional): The content to write to the file. Defaults to "".
    """
    # Create parent directories only if filepath includes a directory path
    dir_name = os.path.dirname(filepath)
    if dir_name:
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
    # Create parent directories only if filepath includes a directory path
    dir_name = os.path.dirname(filepath)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    with open(filepath, "w") as f:
        f.write(patch_content)

class OpenDevinAgent:
    def __init__(self, task: str):
        """
        Initializes the OpenDevin agent with a task.

        Args:
            task (str): The task description for the agent.
        """
        self.task = task

    def generate_plan(self, task_string: str) -> list[dict]:
        """
        Generates a plan based on the provided task string.

        Args:
            task_string (str): The description of the task.

        Returns:
            list[dict]: A list of action dictionaries representing the plan.
        """
        if task_string == "build a snake game":
            return [
                {"action": "create_file", "args": {"filepath": "snake_game.py"}},
                {"action": "patch_file", "args": {"filepath": "snake_game.py", "patch_content": "# Python snake game code here..."}},
                {"action": "shell", "args": {"command": "python snake_game.py"}}
            ]
        elif task_string == "create a hello world python script and run it":
            return [
                {"action": "create_file", "args": {"filepath": "hello.py", "content": "print('Hello from OpenDevin!')"}},
                {"action": "shell", "args": {"command": "python hello.py"}}
            ]
        else:
            return [{"action": "echo", "args": {"message": f"Plan for task: {task_string}"}}]

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
    # Test case 1: Hello World
    agent1 = OpenDevinAgent(task="create a hello world python script and run it")
    agent1.run_task()
    print("-" * 20)

    # Test case 2: Snake Game (will create file and attempt to run, which might fail if python/pygame is not set up)
    agent2 = OpenDevinAgent(task="build a snake game")
    agent2.run_task()
    print("-" * 20)

    # Test case 3: Generic Task
    agent3 = OpenDevinAgent(task="analyze project requirements")
    agent3.run_task()
    print("-" * 20)

    # Test case 4: Cleanup created files (manual for now)
    # Example of using run_shell directly for cleanup if needed
    print("Cleaning up created files...")
    stdout, stderr, rc = run_shell("rm hello.py snake_game.py || true") # Use || true to avoid error if files don't exist
    print(f"Cleanup Stdout: {stdout}")
    print(f"Cleanup Stderr: {stderr}")
    print(f"Cleanup RC: {rc}")
