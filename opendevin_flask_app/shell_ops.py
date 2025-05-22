import subprocess
import os

# This should match the WORKSPACE_DIR in file_ops.py for consistency
# If WORKSPACE_DIR is defined centrally, import it here.
# For now, defining it directly for simplicity, assuming it's relative to opendevin_flask_app
WORKSPACE_DIR = "workspace" 

def run_shell_command(command: str) -> tuple[str, str, int]:
    '''
    Runs a shell command in the specified workspace directory.
    Returns a tuple (stdout: str, stderr: str, return_code: int).
    '''
    # Ensure workspace exists - this logic might be redundant if other ops always ensure it,
    # but good for standalone robustness of this module.
    # However, shell_ops should probably *not* create the workspace.
    # It should operate in it if it exists, or fail if it doesn't.
    # Let's assume file_ops (e.g. @create_file) would have created the workspace.
    
    current_dir = os.getcwd() # Get current working directory
    # Construct full path to workspace directory
    # This assumes shell_ops.py is in opendevin_flask_app, and workspace is a subdir.
    # This needs to be relative to the project root, not opendevin_flask_app if shell_ops.py is inside opendevin_flask_app
    # The most robust way is to determine the path relative to this file's location.
    # Assuming opendevin_flask_app is the main app directory.
    # If app.py runs from opendevin_flask_app, then os.getcwd() when app.py runs will be opendevin_flask_app.
    # So WORKSPACE_DIR will be resolved as opendevin_flask_app/workspace.
    workspace_full_path = os.path.join(current_dir, WORKSPACE_DIR)


    if not os.path.exists(workspace_full_path) or not os.path.isdir(workspace_full_path):
        # Fallback for tests: if WORKSPACE_DIR is directly in current_dir (e.g. /app/workspace)
        # This can happen if the script is run from /app instead of /app/opendevin_flask_app
        alt_workspace_path = WORKSPACE_DIR
        if os.path.exists(alt_workspace_path) and os.path.isdir(alt_workspace_path):
            workspace_full_path = alt_workspace_path
        else:
            # If this script is run from within opendevin_flask_app, but workspace is one level up from there
            # (e.g. /app/workspace, and script is in /app/opendevin_flask_app/shell_ops.py)
            # This logic might get complicated. Standardizing WORKSPACE_DIR relative to project root is better.
            # For now, let's assume WORKSPACE_DIR is a direct subdir of the CWD where the main app starts.
            # If the main app (app.py) is in opendevin_flask_app, then CWD is opendevin_flask_app.
            # Thus, workspace_full_path = "opendevin_flask_app/workspace".
            # If file_ops.py created "workspace", it would be at "opendevin_flask_app/workspace".
            # This should be fine if shell_ops.py is called from app.py in the same directory.
            # The main script (app.py) should ensure CWD is opendevin_flask_app.
            # If running shell_ops.py directly for its __main__ tests, it will be CWD/workspace.
            # This is handled by the __main__ block's os.makedirs(WORKSPACE_DIR).
            pass # Path checking continues below, this was an attempt to find common test paths.


    # Check again with the potentially resolved path
    if not os.path.exists(workspace_full_path) or not os.path.isdir(workspace_full_path):
         # Try path relative to this script file, if opendevin_flask_app/workspace
        script_dir = os.path.dirname(os.path.abspath(__file__))
        path_from_script_dir = os.path.join(script_dir, WORKSPACE_DIR)
        if os.path.exists(path_from_script_dir) and os.path.isdir(path_from_script_dir):
            workspace_full_path = path_from_script_dir
        else:
            return "", f"Error: Workspace directory '{WORKSPACE_DIR}' not found at '{workspace_full_path}' or alternative paths.", -1


    try:
        # Ensure the command is a string
        if not isinstance(command, str):
            return "", "Error: Command must be a string.", -1

        # For security and simplicity with subprocess.run, split the command if it's simple.
        # For complex shell commands (pipes, etc.), use shell=True cautiously or parse more robustly.
        # Using shell=False is generally safer.
        # If command is simple (no shell metacharacters), split it:
        if "&&" not in command and "|" not in command and ";" not in command and ">" not in command and "<" not in command:
            cmd_args = command.split()
            shell_mode = False
        else:
            # For commands with shell metacharacters, shell=True might be needed.
            # This is a security risk if the command string comes from untrusted input.
            # The agent's generated commands should be scrutinized.
            cmd_args = command 
            shell_mode = True


        process = subprocess.run(
            cmd_args,
            cwd=workspace_full_path, # Execute in the workspace directory
            capture_output=True,
            text=True,
            shell=shell_mode, # Be cautious with shell=True
            timeout=30 # Add a timeout for safety
        )
        return process.stdout, process.stderr, process.returncode
    except subprocess.TimeoutExpired:
        return "", "Error: Command timed out.", -1
    except Exception as e:
        return "", f"Error executing command '{command}': {e}", -1

if __name__ == '__main__':
    # This __main__ block is for testing shell_ops.py directly.
    # It will create a 'workspace' subdir in the *current directory* where shell_ops.py is run.
    # This might be different from the 'opendevin_flask_app/workspace' if you run app.py.
    
    # Determine where this script is, and assume WORKSPACE_DIR is relative to it for tests.
    # This ensures that if you run `python opendevin_flask_app/shell_ops.py`,
    # it creates and uses `opendevin_flask_app/workspace`.
    
    # However, the run_shell_command itself uses os.getcwd() to find WORKSPACE_DIR
    # for execution, which can be confusing. The path logic in run_shell_command
    # tries to find WORKSPACE_DIR relative to where the overall app (e.g. app.py) is running.
    # For standalone testing, we ensure WORKSPACE_DIR is created where this script expects it.
    
    # Let's make the test workspace relative to this script file.
    # This way, running "python opendevin_flask_app/shell_ops.py" will create
    # "opendevin_flask_app/workspace/" and test within it.
    # This is more predictable for direct module testing.
    
    # The WORKSPACE_DIR for testing will be created relative to this script's location.
    # The run_shell_command will also need to correctly find this.
    # The path logic in run_shell_command was adjusted to also check relative to script dir as a fallback.
    
    test_workspace_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), WORKSPACE_DIR)

    if not os.path.exists(test_workspace_dir):
        os.makedirs(test_workspace_dir)
        print(f"Created test workspace: {test_workspace_dir}")
    if not os.path.isdir(test_workspace_dir):
        print(f"Error: {test_workspace_dir} exists but is not a directory. Cannot run tests.")
        exit(1)
    
    # To make run_shell_command use this specific test_workspace_dir for the tests:
    # We can either:
    # 1. Change CWD for the test execution: os.chdir(os.path.dirname(os.path.abspath(__file__)))
    #    Then run_shell_command's os.path.join(os.getcwd(), WORKSPACE_DIR) would resolve correctly.
    # 2. Modify run_shell_command to accept workspace_path (cleaner but API change).
    # 3. Rely on the fallback path logic in run_shell_command that checks relative to script dir.
    # Let's rely on fallback path logic (added above).

    print(f"Testing shell operations in determined workspace: {test_workspace_dir}")

    # Test 1: Simple echo command
    stdout, stderr, ret_code = run_shell_command("echo Hello from shell")
    print(f"Echo Test: STDOUT='{stdout.strip()}', STDERR='{stderr.strip()}', RC={ret_code}")

    # Test 2: List files
    list_command = "ls -la" if os.name != "nt" else "dir"
    stdout, stderr, ret_code = run_shell_command(list_command)
    print(f"List Files Test ({list_command}): STDOUT has {len(stdout.strip())} chars, STDERR='{stderr.strip()}', RC={ret_code}")
    
    # Test 3: Python execution
    test_py_filename_relative = "test_script.py" 
    # This file will be created in test_workspace_dir by this script.
    test_py_filepath_abs = os.path.join(test_workspace_dir, test_py_filename_relative)

    with open(test_py_filepath_abs, "w") as f:
        f.write("import sys\n")
        f.write("print('Hello from Python script')\n")
        f.write("sys.stderr.write('Error message from Python script\\n')\n") # Corrected escape
        f.write("sys.exit(12)")

    # Command should be relative to workspace
    stdout, stderr, ret_code = run_shell_command(f"python {test_py_filename_relative}")
    print(f"Python Script Test: STDOUT='{stdout.strip()}', STDERR='{stderr.strip()}', RC={ret_code}")
    
    # Test 4: Command with error
    stdout, stderr, ret_code = run_shell_command("command_that_does_not_exist_gsfsfsd") # Made it more unique
    print(f"Non-existent Command Test: STDOUT='{stdout.strip()}', STDERR='{stderr.strip()}', RC={ret_code}")

    # Test 5: Python version to stderr
    stdout, stderr, ret_code = run_shell_command("python -V")
    print(f"Python Version Test: STDOUT='{stdout.strip()}', STDERR='{stderr.strip()}', RC={ret_code}")

    # Clean up the test script
    if os.path.exists(test_py_filepath_abs):
        os.remove(test_py_filepath_abs)
        print(f"Cleaned up {test_py_filepath_abs}")
    
    # Clean up test workspace directory if it was created by this test script
    # For safety, only remove if it's the specific 'workspace' subdir in this script's dir
    # and if it's empty (or decide to remove non-empty)
    # For now, let's leave it, as other tests might use it or it might pre-exist.
    # if os.path.exists(test_workspace_dir) and test_workspace_dir.endswith("workspace"):
    #     try:
    #         os.rmdir(test_workspace_dir) # Only removes if empty
    #         print(f"Cleaned up test workspace directory: {test_workspace_dir}")
    #     except OSError as e:
    #         print(f"Could not remove test workspace {test_workspace_dir} (may not be empty): {e}")
    print("Shell operations tests finished.")
