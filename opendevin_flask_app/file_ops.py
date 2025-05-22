import os

WORKSPACE_DIR = "workspace" # Relative to opendevin_flask_app directory

def _ensure_workspace_exists():
    # Ensure the path is relative to this file's location if file_ops.py is in opendevin_flask_app
    # Or, make WORKSPACE_DIR an absolute path or relative to a known root.
    # For now, assuming it's a subdirectory of where app.py is.
    if not os.path.exists(WORKSPACE_DIR):
        os.makedirs(WORKSPACE_DIR)
    # Also ensure it's treated as a directory
    if not os.path.isdir(WORKSPACE_DIR):
        # This case should ideally not happen if makedirs worked or it existed as a dir
        raise NotADirectoryError(f"Workspace path '{WORKSPACE_DIR}' exists but is not a directory.")


def create_file(filename: str, content: str = "") -> tuple[bool, str]:
    '''
    Creates a file in the workspace directory.
    If content is provided, it writes the content to the file.
    Returns a tuple (success: bool, message: str).
    '''
    _ensure_workspace_exists()
    filepath = os.path.join(WORKSPACE_DIR, filename)
    try:
        # Prevent directory traversal
        if not os.path.abspath(filepath).startswith(os.path.abspath(WORKSPACE_DIR)):
            return False, f"Error: Invalid filename '{filename}' (directory traversal attempt)."
        
        # Create subdirectories if they don't exist in the filename path
        file_dir = os.path.dirname(filepath)
        if file_dir and not os.path.exists(file_dir): # Check if file_dir is not empty string
            os.makedirs(file_dir)

        with open(filepath, 'w') as f:
            f.write(content)
        return True, f"File '{filename}' created successfully in workspace."
    except Exception as e:
        return False, f"Error creating file '{filename}': {e}"

def write_content_to_file(filename: str, content: str) -> tuple[bool, str]:
    '''
    Writes (or overwrites) content to an existing file in the workspace.
    This is distinct from create_file which is for initial creation.
    However, for simplicity, this can also create if not exists, like 'w' mode.
    Returns a tuple (success: bool, message: str).
    '''
    _ensure_workspace_exists()
    filepath = os.path.join(WORKSPACE_DIR, filename)
    try:
        if not os.path.abspath(filepath).startswith(os.path.abspath(WORKSPACE_DIR)):
            return False, f"Error: Invalid filename '{filename}' (directory traversal attempt)."

        file_dir = os.path.dirname(filepath)
        if file_dir and not os.path.exists(file_dir):
             os.makedirs(file_dir)
             
        with open(filepath, 'w') as f: # 'w' will create or overwrite
            f.write(content)
        return True, f"Content written to file '{filename}' successfully."
    except Exception as e:
        return False, f"Error writing to file '{filename}': {e}"

def read_file(filename: str) -> tuple[bool, str]:
    '''
    Reads the content of a file from the workspace.
    Returns a tuple (success: bool, content_or_error_message: str).
    '''
    _ensure_workspace_exists() # Technically not needed for read if file must exist, but good for consistency
    filepath = os.path.join(WORKSPACE_DIR, filename)
    try:
        if not os.path.abspath(filepath).startswith(os.path.abspath(WORKSPACE_DIR)):
            return False, f"Error: Invalid filename '{filename}' (directory traversal attempt)."
        if not os.path.exists(filepath):
            return False, f"Error: File '{filename}' not found in workspace."
        if not os.path.isfile(filepath):
            return False, f"Error: '{filename}' is not a file."
            
        with open(filepath, 'r') as f:
            content = f.read()
        return True, content
    except Exception as e:
        return False, f"Error reading file '{filename}': {e}"

def list_files(path_param: str = ".") -> tuple[bool, list[str] | str]:
    '''
    Lists files and directories in the specified path within the workspace.
    Returns a tuple (success: bool, list_of_items_or_error_message: str | list).
    '''
    _ensure_workspace_exists()
    
    # Sanitize path_param to stay within WORKSPACE_DIR
    # Normalize path to prevent '..' from going above WORKSPACE_DIR
    target_path = os.path.join(WORKSPACE_DIR, path_param)
    abs_target_path = os.path.abspath(target_path)
    abs_workspace_path = os.path.abspath(WORKSPACE_DIR)

    if not abs_target_path.startswith(abs_workspace_path):
        return False, f"Error: Invalid path '{path_param}' (attempt to access outside workspace)."

    try:
        if not os.path.exists(abs_target_path):
            return False, f"Error: Path '{path_param}' does not exist in workspace."
        if not os.path.isdir(abs_target_path):
            return False, f"Error: Path '{path_param}' is not a directory."
            
        items = os.listdir(abs_target_path)
        return True, items
    except Exception as e:
        return False, f"Error listing files in '{path_param}': {e}"

if __name__ == '__main__':
    # Test functions
    print("Testing file operations...")
    
    # Ensure workspace is clean for testing if needed, or use unique filenames.
    # For this example, we'll just run operations.
    # A more robust test would clean up created files/dirs.

    print(create_file("test.txt", "Hello world!"))
    print(create_file("subdir/test_subdir.txt", "Hello from subdir!"))
    print(write_content_to_file("test.txt", "Hello world updated!"))
    print(write_content_to_file("new_test.txt", "Newly created by write_content_to_file"))
    
    success, content = read_file("test.txt")
    if success:
        print(f"Read test.txt: {content}")
    else:
        print(content)

    success, content_subdir = read_file("subdir/test_subdir.txt")
    if success:
        print(f"Read subdir/test_subdir.txt: {content_subdir}")
    else:
        print(content_subdir)

    success, files = list_files(".")
    if success:
        print(f"Files in workspace root: {files}")
    else:
        print(files)

    success, files_subdir = list_files("subdir")
    if success:
        print(f"Files in subdir: {files_subdir}")
    else:
        print(files_subdir)

    # Test error cases
    print(create_file("../outside.txt", "Trying to escape")) # Should fail due to path traversal
    print(read_file("nonexistent.txt"))
    print(list_files("nonexistent_dir"))
