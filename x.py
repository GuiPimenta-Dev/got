import click
import prompt_toolkit
from got.commit import CommitHandler
from got.git import Git
from got.printer import Printer
from blessed import Terminal

git = Git()
m = "gpt-4-turbo"
commit_handler = CommitHandler(m)
a = False
printer = Printer()
p = False
if a:
    git.add_files_to_stage()

term = Terminal()

print(term.enter_fullscreen)
print(term.clear)


commits = commit_handler.get_commit_message_suggestion()

for commit in commits:
    commit_message = printer.select_commit_message(commit["messages"], commit["changes"])


    if commit_message == "Retry":
        while True:
            messages = commit_handler.retry_commit_message_suggestion(commit["changes"])
            commit_message = printer.select_commit_message(messages, commit["changes"])

            if commit_message != "Retry":
                break

    if commit_message == "Skip":
        printer.print("Skipping commit...", "yellow", 1, 1)
        continue

    if commit_message == "Abort":
        printer.print("Aborted!", "red", 1, 1)
        exit()

    if commit_message == "Manual":
        printer.br()
        commit_message = prompt_toolkit.prompt("Enter a commit message: ")

    else:
        commit_message = printer.edit_commit_message(commit_message, commit["changes"])

    git.add_commit({"files_to_commit": commit["files"], "message": commit_message})

if not git.commits:
    printer.print("Nothing to commit...", "white", 1, 1)
    exit()

confirmed = printer.confirm_commits(git.commits)
if confirmed:
  git.commit()

if p:
    git.push()
