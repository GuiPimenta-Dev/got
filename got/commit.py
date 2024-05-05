import os

from got.ai.factory import AIFactory
from got.git import Git
from got.printer import Printer


class CommitHandler(Git):

    def __init__(self, model, max_tokens):
        self.model = model
        self.max_tokens = max_tokens

    def get_commit_message_suggestion(self):
        commited_changes = {}
        ai = AIFactory().create_ai(self.model, self.max_tokens)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt = open(current_dir + "/prompts/prompt.txt", "r").read()
        prompt += ai.commit_suffix
        staged_files = self.get_staged_files()
        ai.add_message(prompt)
        for file in staged_files:
            try:
                f = open(file, "r")
                commit = f.read()
            except FileNotFoundError:
                commit = "File Deleted!"
            except:
                printer = Printer()
                printer.print(f"An error occurred while trying to read the file {file}", "red", 1, 1)
                exit()

            previous_commit = self.get_previous_commit(file)
            diff = self.get_diff(file)
            ai.add_message(
                {
                    "file_path": file,
                    "diff": diff,
                }
            )
            commited_changes[file] = {
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
        ai = AIFactory().create_ai(self.model, self.max_tokens)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt = open(current_dir + "/prompts/prompt.txt", "r").read()
        prompt += ai.retry_suffix
        ai.add_message(prompt)
        ai.add_message(changes)
        response = ai.prompt()
        return response["messages"]
