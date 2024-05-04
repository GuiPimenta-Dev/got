from ai.factory import AIFactory
from git import Git

class Commit(Git):
  
  def get_commit_message_suggestion(self):
    commited_changes = {}
    prompt = open("prompts/commit_prompt.txt", "r").read()
    staged_files = self.get_staged_files()
    ai = AIFactory().create_ai()
    ai.add_message(prompt)
    for file in staged_files:
        f = open(file, "r")
        content = f.read()
        ai.add_message({"file_path": file, "content": content})
        commited_changes[file] = content

    response = ai.prompt()
    
    for commit in response["commits"]:
      changes = []
      for file in commit["files"]:
        content = commited_changes[file]
        changes.append({"file_path": file, "content": content})
      commit["changes"] = changes
      
    return response["commits"]
  
  def retry_commit_message_suggestion(self, changes):
    prompt = open("prompts/retry_commit_prompt.txt", "r").read()
    ai = AIFactory().create_ai()
    ai.add_message(prompt)
    ai.add_message(changes)
    response = ai.prompt()
    return response["messages"]

