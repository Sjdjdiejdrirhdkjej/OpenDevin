from smolagents import Task

# Assuming the utility functions create_file, patch_file, run_shell
# are defined in OpenDevin.src.agent or will be moved to a utils file and imported.
# For now, let's try to import them from .agent
# If this causes issues, we might need to rethink their location or how tasks access them.
try:
    # Attempt to import from a potential future refactoring
    from .agent_utils import create_file, patch_file, run_shell
except ImportError:
    # Fallback to importing from .agent if agent_utils doesn't exist yet
    # This assumes these functions are globally defined in agent.py
    from .agent import create_file, patch_file, run_shell


class CreateFileTask(Task):
    def __init__(self, name: str, filepath: str, content: str = ""):
        super().__init__(name)
        self.filepath = filepath
        self.content = content
        self.result_log = []

    def execute(self, agent):
        # agent parameter is part of smolagents.Task signature, might be useful later
        self.result_log = [] # Clear previous logs for this task instance
        if not self.filepath:
            message = "[ERROR]: Missing filepath for CreateFileTask."
            print(message) # For CLI
            self.result_log.append(message)
            return {"status": "failure", "log": self.result_log, "error": "Missing filepath"}
        
        try:
            create_file(self.filepath, self.content) # Call to global utility function
            message = f"[CREATED]: {self.filepath}"
            print(message) # For CLI
            self.result_log.append(message)
            return {"status": "success", "log": self.result_log, "filepath": self.filepath}
        except Exception as e:
            message = f"[ERROR] in CreateFileTask ({self.filepath}): {e}"
            print(message) # For CLI
            self.result_log.append(message)
            return {"status": "failure", "log": self.result_log, "error": str(e)}

class PatchFileTask(Task):
    def __init__(self, name: str, filepath: str, patch_content: str):
        super().__init__(name)
        self.filepath = filepath
        self.patch_content = patch_content
        self.result_log = []

    def execute(self, agent):
        self.result_log = []
        if not self.filepath or self.patch_content is None:
            message = "[ERROR]: Missing filepath or patch_content for PatchFileTask."
            print(message)
            self.result_log.append(message)
            return {"status": "failure", "log": self.result_log, "error": "Missing filepath or content"}

        try:
            patch_file(self.filepath, self.patch_content) # Call to global utility function
            message = f"[PATCHED]: {self.filepath} with content: {self.patch_content[:50]}{'...' if len(self.patch_content) > 50 else ''}"
            print(message)
            self.result_log.append(message)
            return {"status": "success", "log": self.result_log, "filepath": self.filepath}
        except Exception as e:
            message = f"[ERROR] in PatchFileTask ({self.filepath}): {e}"
            print(message)
            self.result_log.append(message)
            return {"status": "failure", "log": self.result_log, "error": str(e)}

class ShellCommandTask(Task):
    def __init__(self, name: str, command: str):
        super().__init__(name)
        self.command = command
        self.result_log = []

    def execute(self, agent):
        self.result_log = []
        if not self.command:
            message = "[ERROR]: Missing command for ShellCommandTask."
            print(message)
            self.result_log.append(message)
            return {"status": "failure", "log": self.result_log, "error": "Missing command"}

        try:
            message_cmd = f"[SHELL]: {self.command}"
            print(message_cmd)
            self.result_log.append(message_cmd)

            stdout, stderr, rc = run_shell(self.command) # Call to global utility function

            stdout_msg = f"Stdout: {stdout.strip()}"
            print(stdout_msg)
            self.result_log.append(stdout_msg)

            stderr_msg = f"Stderr: {stderr.strip()}"
            print(stderr_msg)
            self.result_log.append(stderr_msg)
            
            rc_msg = f"Return Code: {rc}"
            print(rc_msg)
            self.result_log.append(rc_msg)

            # Check for actual content in stderr after stripping
            if rc != 0 or (stderr and stderr.strip()): 
                debug_message = "[DEBUGGING]: Error detected during shell execution."
                print(debug_message)
                self.result_log.append(debug_message)
                # Return success_with_errors as the task itself executed.
                # The agent can decide if a non-zero RC or stderr constitutes a plan failure.
                return {"status": "success_with_errors", "log": self.result_log, "stdout": stdout, "stderr": stderr, "rc": rc}
            
            return {"status": "success", "log": self.result_log, "stdout": stdout, "stderr": stderr, "rc": rc}
        except Exception as e:
            message = f"[ERROR] in ShellCommandTask ('{self.command}'): {e}"
            print(message)
            self.result_log.append(message)
            return {"status": "failure", "log": self.result_log, "error": str(e)}

class EchoTask(Task):
    def __init__(self, name: str, message: str): # Parameter renamed to 'message' for clarity
        super().__init__(name)
        self.message_to_echo = message # Stored with a different attribute name
        self.result_log = []

    def execute(self, agent):
        self.result_log = []
        if self.message_to_echo is None:
            err_message = "[ERROR]: Missing message for EchoTask."
            print(err_message)
            self.result_log.append(err_message)
            return {"status": "failure", "log": self.result_log, "error": "Missing message"}
        
        try:
            echo_msg = f"[ECHO]: {self.message_to_echo}"
            print(echo_msg)
            self.result_log.append(echo_msg)
            return {"status": "success", "log": self.result_log, "message_displayed": self.message_to_echo}
        except Exception as e:
            message = f"[ERROR] in EchoTask: {e}" # Corrected error message
            print(message) 
            self.result_log.append(message)
            return {"status": "failure", "log": self.result_log, "error": str(e)}

class ErrorTask(Task):
    # A special task to represent an error that occurred during plan generation or translation.
    def __init__(self, name: str, error_message: str):
        super().__init__(name)
        self.error_message = error_message
        self.result_log = []

    def execute(self, agent):
        self.result_log = []
        message = f"[ERROR_TASK]: {self.error_message}"
        print(message) 
        self.result_log.append(message)
        # This task inherently signifies a failure in the broader process.
        return {"status": "failure", "log": self.result_log, "error_represented": self.error_message}
