def read_file(file_path):
    """Reads the content of a file safely from a whitelisted directory."""
    whitelisted_directory = '/path/to/whitelisted/directory'  # Update with actual path
    if not file_path.startswith(whitelisted_directory):
        raise ValueError("Access to this file is not allowed.")
    
    with open(file_path, 'r') as file:
        return file.read()

def list_files(directory):
    """Lists all files in a whitelisted directory."""
    whitelisted_directory = '/path/to/whitelisted/directory'  # Update with actual path
    if not directory.startswith(whitelisted_directory):
        raise ValueError("Access to this directory is not allowed.")
    
    import os
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]