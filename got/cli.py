import os
import click
from InquirerPy import inquirer
from InquirerPy.separator import Separator
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory

from got.commit import CommitHandler
from got.git import Git
from got.printer import Printer

printer = Printer()

@click.group()
def got():
    pass


OPENAI_MODELS = ["gpt-3.5-turbo", "gpt-4-turbo"]
GROQ_MODELS = ["gemma-7b-it", "llama2-70b-4096", "llama3-70b-8192", "llama3-8b-8192", "mixtral-8x7b-32768"]


@got.command()
@click.option("-a", is_flag=True, help="Also add to stage before committing", default=False)
@click.option("-m", help="LLM model", type=click.Choice([*OPENAI_MODELS, *GROQ_MODELS]), default="gpt-4-turbo")
def commit(a, m):
    git = Git()
    commit_handler = CommitHandler(m)

    if a:
        git.add_files_to_stage()

    commits = commit_handler.get_commit_message_suggestion()

    for commit in commits:
        lines = max(len(string) for string in commit["messages"])
        choices = [*commit["messages"], Separator(lines * "-"), "Manual", "Retry", "Skip", "Abort"]

        click.echo()
        commit_message = inquirer.select(
            message=f"Select a commit message for the following files: {commit['files']}",
            choices=choices,
        ).execute()


        if commit_message == "Retry":
            while True:
                messages = commit_handler.retry_commit_message_suggestion(commit["changes"])
                lines = max(len(string) for string in messages)
                choices = [*messages, Separator(lines * "-"), "Manual", "Retry", "Skip", "Abort"]

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

        if commit_message == "Manual":
            printer.br()
            commit_message = prompt("Enter a commit message: ")

        else:
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


@got.command()
@click.option("--restore", is_flag=True, help="Restore prompts to default", default=False)
@click.option("--set-example", is_flag=True, help="Set examples of the desired output", default=False)
def prompt(restore, set_example):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    if restore:
        os.system(f"cp {current_dir}/prompts/default_prompt.txt {current_dir}/prompts/prompt.txt")
        os.system(f"cp {current_dir}/prompts/default_examples.txt {current_dir}/prompts/examples.txt")
        printer.print("Prompts restored to default.", "green", 1, 1)
        exit()
    
    click.edit(filename=f"{current_dir}/prompts/prompt.txt")
    if set_example:
        click.edit(filename=f"{current_dir}/prompts/examples.txt")    

    printer.print("The prompt has been set.", "green", 1, 1)

if __name__ == "__main__":
    got()
