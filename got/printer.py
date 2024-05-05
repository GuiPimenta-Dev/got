import itertools
import sys
import threading
import time
import textwrap  

import click
from blessed import Terminal


class Printer:
    spinner = {"running": False, "legend": None}
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "gray": "\033[90m",
        "light-gray": "\033[37m",
        "rose": "\033[38;2;244;94;172m",
        "black": "\033[38;2;0;0;0m",
    }

    def start_spinner(self, legend):
        self.spinner["running"] = True
        self.spinner["legend"] = legend
        spinner_thread = threading.Thread(target=self.spinner_task)
        spinner_thread.start()

    def spinner_task(self):
        spinner_symbols = itertools.cycle(["-", "\\", "|", "/"])
        while self.spinner["running"]:
            sys.stdout.write(f"\r{next(spinner_symbols)}   {self.spinner['legend']}")
            sys.stdout.flush()
            time.sleep(0.1)

    def stop_spinner(self):
        self.spinner["running"] = False
        sys.stdout.write("\r")  # Move cursor to the beginning of the line
        sys.stdout.write(" " * (len(self.spinner["legend"]) + 4))  # Overwrite spinner and legend with spaces
        sys.stdout.flush()

    def change_spinner_legend(self, legend):
        previous_legend_length = len(self.spinner["legend"]) + 4 if self.spinner["legend"] else 0
        sys.stdout.write("\r" + " " * previous_legend_length)
        sys.stdout.flush()
        self.spinner["legend"] = legend

    def br(self, lines=1):
        for _ in range(lines):
            print()

    def print(self, message, color="white", pre_break_lines=None, post_break_lines=None):
        if pre_break_lines:
            print("\n" * pre_break_lines)

        color = self.colors[color]
        if color:
            print(color + message + "\033[0m")
        else:
            print(message)

        if post_break_lines:
            print("\n" * post_break_lines)

    @staticmethod
    def select_commit_message(commit_messages, changes):
        term = Terminal()

        print(term.enter_fullscreen)
        print(term.clear)

        # Default choices and a visual separator
        default_choices = ["Manual", "Retry", "Skip", "Abort"]
        max_length = max(len(choice) for choice in commit_messages + default_choices)
        choices = commit_messages + ["-" * max_length] + default_choices
        non_selectable = {"-" * max_length}
        selected_index = 0
        last_key = None
        half_width = term.width // 2
        scroll_offset = -2
        right_panel_width = term.width - half_width  # Width of the right panel

        files = [item["file_path"] for item in changes]

        modified_string = []
        for item in changes:
            if item is not None and item["diff"] is not None:  # Check if item is not None and has "diff" key
                modified_string.append(term.green(item["file_path"]))
                modified_string.append("")
                diff_lines = item["diff"].split("\n")
                for line in diff_lines:
                    wrapped_lines = textwrap.wrap(line, width=right_panel_width)  # Wrap lines to fit the panel width
                    modified_string.extend(wrapped_lines)
        else:
            # Handle the case where item is None or does not have a "diff" key
            modified_string.append("No diff available")
            modified_string.append("")


        with term.cbreak(), term.hidden_cursor():
            while last_key != "KEY_ENTER":
                print(term.clear)

                # Display title
                title_display = (
                    term.move_xy(0, 1)
                    + term.white_bold("Select a commit message")
                    + " ("
                    + term.green(", ".join(files))
                    + "):"
                )
                print(title_display)

                # Display options in the dropdown
                for index, choice in enumerate(choices):
                    y_position = index + 3  # Offset by 2 to account for the title and spacing
                    if choice in non_selectable:
                        print(term.move_xy(0, y_position) + term.white(choice))
                    elif index == selected_index:
                        print(term.move_xy(0, y_position) + term.color_rgb(92, 203, 223) + f"❯ {choice}" + term.normal)
                    else:
                        print(term.move_xy(0, y_position) + term.white(choice))

                # Display the right side content continuously with scrolling
                max_display_lines = term.height - 2  # Adjust based on terminal size and title spacing
                start_line = max(0, min(scroll_offset, len(modified_string) - max_display_lines))
                end_line = min(start_line + max_display_lines, len(modified_string))

                for i, line in enumerate(modified_string[start_line:end_line], start=2):
                    print(term.move_xy(half_width, i) + line)

                # Handle keyboard input
                key = term.inkey(timeout=0.1)
                if key:
                    last_key = key.name
                    if key.code == term.KEY_UP:
                        if selected_index > 0:
                            potential_index = selected_index - 1
                            while potential_index > 0 and choices[potential_index] in non_selectable:
                                potential_index -= 1
                            if potential_index >= 0:
                                selected_index = potential_index
                        scroll_offset = max(0, scroll_offset - 1)
                    elif key.code == term.KEY_DOWN:
                        if selected_index < len(choices) - 1:
                            potential_index = selected_index + 1
                            while potential_index < len(choices) and choices[potential_index] in non_selectable:
                                potential_index += 1
                            if potential_index < len(choices):
                                selected_index = potential_index
                        scroll_offset = min(len(modified_string) - max_display_lines, scroll_offset + 1)

        return choices[selected_index]

    @staticmethod
    def edit_commit_message(commit_message, changes):
        term = Terminal()

        print(term.enter_fullscreen)
        print(term.clear)

        # Default choices and a visual separator
        choices = ["No", "Yes"]
        selected_index = 0
        last_key = None
        half_width = term.width // 2
        scroll_offset = -2
        right_panel_width = term.width - half_width  # Width of the right panel

        modified_string = []
        for item in changes:
            if item is not None and item["diff"] is not None:  # Check if item is not None and has "diff" key
                modified_string.append(term.green(item["file_path"]))
                modified_string.append("")
                diff_lines = item["diff"].split("\n")
                for line in diff_lines:
                    wrapped_lines = textwrap.wrap(line, width=right_panel_width)  # Wrap lines to fit the panel width
                    modified_string.extend(wrapped_lines)
        else:
            # Handle the case where item is None or does not have a "diff" key
            modified_string.append("")

        with term.cbreak(), term.hidden_cursor():
            while last_key != "KEY_ENTER":
                # Clear the terminal area
                print(term.clear)

                # Display title
                title_display = (
                    term.move_xy(0, 1)
                    + term.white_bold("Would you like to edit the message")
                    + " ("
                    + term.green(commit_message)
                    + ") ?"
                )
                print(title_display)

                # Display options in the dropdown
                for index, choice in enumerate(choices):
                    y_position = index + 3  # Offset by 2 to account for the title and spacing
                    if index == selected_index:
                        print(term.move_xy(0, y_position) + term.color_rgb(92, 203, 223) + f"❯ {choice}" + term.normal)
                    else:
                        print(term.move_xy(0, y_position) + term.white(choice))

                # Display the right side content continuously with scrolling
                max_display_lines = term.height - 2  # Adjust based on terminal size and title spacing
                start_line = max(0, min(scroll_offset, len(modified_string) - max_display_lines))
                end_line = min(start_line + max_display_lines, len(modified_string))

                for i, line in enumerate(modified_string[start_line:end_line], start=2):
                    print(term.move_xy(half_width, i) + line)

                # Handle keyboard input
                key = term.inkey(timeout=0.1)
                if key:
                    last_key = key.name
                    if key.code == term.KEY_UP:
                        if selected_index > 0:
                            potential_index = selected_index - 1
                            if potential_index >= 0:
                                selected_index = potential_index
                        scroll_offset = max(0, scroll_offset - 1)
                    elif key.code == term.KEY_DOWN:
                        if selected_index < len(choices) - 1:
                            potential_index = selected_index + 1
                            if potential_index < len(choices):
                                selected_index = potential_index
                        scroll_offset = min(len(modified_string) - max_display_lines, scroll_offset + 1)

        choice = choices[selected_index]
        if choice == "Yes":
            commit_message = click.edit(text=commit_message, editor="vim", require_save=False)

        return commit_message

    def confirm_commits(self, commits):
        term = Terminal()
        print(term.enter_fullscreen)
        print(term.clear)

        self.print("COMMITS:", "white")
        for commit in commits:
            self.print("------------------------ + ------------------------", "gray", 1)

            self.print("Files:", "white", 1, 1)
            for file in commit["files_to_commit"]:
                self.print(f"  {file}", "green")

            self.print("Message:", "white", 1, 1)
            self.print(f"  {commit['message']}", "yellow")

        self.br(3)
        choice = click.prompt(
            "Would you like to proceed? [Y/n]",
            default="Y",
            type=click.Choice(["Y", "n"], case_sensitive=False),
            show_choices=False,
            show_default=False,
        )
        return choice.lower() == "y"
