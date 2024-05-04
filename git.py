import subprocess

class Git:
  
  def __init__(self):
    self.commits = []
  
  @staticmethod
  def get_staged_files():
    try:
      result = subprocess.run(
        ['git', 'diff', '--name-only', '--cached'],
        text=True,
        capture_output=True,
        check=True
      )
      staged_files = result.stdout.strip().split('\n')
      staged_files = [file for file in staged_files if file]
      
      return staged_files
    except subprocess.CalledProcessError as e:
      print(f"An error occurred while trying to get staged files: {e}")
      return []
  
  def add_commit(self, commit):
    self.commits.append(commit)
  
  def commit(self):
    for commit in self.commits:
      files = commit["files_to_commit"]
      message = commit["message"]
      try:
        subprocess.run(
          ['git', 'commit', '-m', message, *files],
          check=True
        )
      except subprocess.CalledProcessError as e:
        print(f"An error occurred while trying to commit files: {e}")
        return False
    return True