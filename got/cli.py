import os

import click
from blessed import Terminal

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
@click.option("-p", is_flag=True, help="Also push to remote after commiting", default=False)
@click.option("-m", help="LLM model", type=click.Choice([*OPENAI_MODELS, *GROQ_MODELS]), default="gpt-4-turbo")
@click.option("-t", help="Max tokens to be used by the model", default=4096)
def commit(a, p, m, t):
    term = Terminal()
    print(term.enter_fullscreen)
    print(term.clear)
    
    git = Git()
    commit_handler = CommitHandler(m, t)

    if a:
        git.add_files_to_stage()

    commits = commit_handler.get_commit_message_suggestion()

    for commit in commits:
        commit_message = printer.select_commit_message(commit["messages"], commit["changes"])

        if commit_message == "Retry":
            while True:
                print(term.clear)
                messages = commit_handler.retry_commit_message_suggestion(commit["changes"])
                commit_message = printer.select_commit_message(messages, commit["changes"])

                if commit_message != "Retry":
                    break

        if commit_message == "Skip":
            continue

        if commit_message == "Abort":
            exit()

        if commit_message == "Manual":
            commit_message = click.edit(editor="vim", require_save=False)

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
