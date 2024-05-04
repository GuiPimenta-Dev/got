import subprocess

def get_file_from_previous_commit(file_path):
    try:
        # Run the git command to get the content of the file from the previous commit
        result = subprocess.run(
            ['git', 'show', f'HEAD~1:{file_path}'],
            text=True,
            capture_output=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Failed to retrieve file content from the previous commit: {e}")
        return None

# Example usage: specify the path to the file you are interested in
file_path = 'printer.py'

# Get the content of the file from the previous commit
file_content = get_file_from_previous_commit(file_path)

if file_content is not None:
    print("Content of the file from the previous commit:")
    print(file_content)
else:
    print("No content was retrieved or an error occurred.")
