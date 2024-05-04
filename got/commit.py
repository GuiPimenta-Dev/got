from got.ai.factory import AIFactory
from got.git import Git


class CommitHandler(Git):
    
    def __init__(self, model):
        self.model = model
    
    
    def get_commit_message_suggestion(self):
        commited_changes = {}
        prompt = open("got/prompts/commit_prompt.txt", "r").read()
        staged_files = self.get_staged_files()
        ai = AIFactory().create_ai(self.model)
        ai.add_message(prompt)
        for file in staged_files:
            try:
                f = open(file, "r")
                commit = f.read()
            except FileNotFoundError:
                commit = "File Deleted!"
            previous_commit = self.get_previous_commit(file)
            diff = self.get_diff(file)
            ai.add_message(
                {
                    "file_path": file,
                    "previous_commit": previous_commit,
                    "commit": commit,
                    "diff": diff,
                }
            )
            commited_changes[file] = {
                "previous_commit": previous_commit,
                "commit": commit,
                "diff": diff,
            }

        response = ai.prompt()

        for commit in response["commits"]:
            changes = []
            for file in commit["files"]:
                content = commited_changes[file]
                changes.append({"file_path": file, **content})
            commit["changes"] = changes

        return response["commits"]

    def retry_commit_message_suggestion(self, changes):
        prompt = open("got/prompts/retry_commit_prompt.txt", "r").read()
        ai = AIFactory().create_ai(self.model)
        ai.add_message(prompt)
        ai.add_message(changes)
        response = ai.prompt()
        return response["messages"]
