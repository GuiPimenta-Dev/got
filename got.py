import click
from commit import CommitHandler
from InquirerPy import inquirer
from InquirerPy.separator import Separator
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory

from git import Git
from printer import Printer

printer = Printer()
git = Git()
commit_handler = CommitHandler()

commits = commit_handler.get_commit_message_suggestion()

for commit in commits:
    lines = max(len(string) for string in commit["messages"])
    choices = [*commit["messages"], Separator(lines * "-"), "Retry", "Skip", "Abort"]

    click.echo()
    commit_message = inquirer.select(
        message=f"Select a commit message for the following files: {commit['files']}",
        choices=choices,
    ).execute()

    if commit_message == "Retry":
        while True:
            messages = commit_handler.retry_commit_message_suggestion(commit["changes"])
            lines = max(len(string) for string in messages)
            choices = [*messages, Separator(lines * "-"), "Retry", "Skip", "Abort"]

            click.echo()
            commit_message = inquirer.select(
                message=f"Select a commit message for the following files: {commit['files']}",
                choices=choices,
            ).execute()

            if commit_message != "Retry":
                break

    if commit_message == "Skip":
        continue

    if commit_message == "Abort":
        break

    change_commit_message = inquirer.select(
        message=f"Would you like to edit the selected message?",
        choices=["No", "Yes"],
    ).execute()

    if change_commit_message == "Yes":
        history = InMemoryHistory()
        history.append_string(commit_message)
        click.echo()
        commit_message = prompt("", default=commit_message, history=history)

    git.add_commit({"files_to_commit": commit["files"], "message": commit_message})

printer.print("Commits to be made:", "blue", 1)
for commit in git.commits:
    printer.print("------------------------ + ------------------------", "gray", 1)

    printer.print("Files:", "white", 1, 1)
    for file in commit["files_to_commit"]:
        printer.print(f"  {file}", "green")

    printer.print("Message:", "white", 1, 1)
    printer.print(f"  {commit['message']}", "yellow")

click.echo()

if click.confirm("Would you like to proceed?", default="Y", abort=True):
    git.commit()
