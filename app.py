import os
import platform
import sys
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion, PathCompleter, WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import Style
from shell_commands import ShellCommandExecutor

# Define built-in commands for autocomplete
COMMANDS = [
    "cd", "ls", "pwd", "mkdir", "rm", "clear", "exit"
]

class ShellCompleter(Completer):
    def __init__(self):
        self.cmd_completer = WordCompleter(COMMANDS, ignore_case=True)
        self.path_completer = PathCompleter(expanduser=True)

    def get_completions(self, document, complete_event):
        text_before_cursor = document.text_before_cursor.lstrip()
        if " " not in text_before_cursor:
            yield from self.cmd_completer.get_completions(document, complete_event)
        else:
            yield from self.path_completer.get_completions(document, complete_event)

def clear_screen():
    os.system("cls" if platform.system() == "Windows" else "clear")

# Define Banner for first time execution
def print_banner(current_path):
    print("\n" + "=" * 40)
    print("        🌟 MagicShell 🌟")
    print("=" * 40)
    print(f"Current Directory: {current_path}\n")

# Define every prompt execution
def make_prompt(path):
    return [
        ("class:star", "🌟 MagicShell 🌟 "),
        ("class:path", f"{path} "),
        ("class:arrow", "> "),
    ]

def run_shell():
    clear_screen()
    executor = ShellCommandExecutor()
    print_banner(executor.current_dir)

    style = Style.from_dict({
        "star": "ansicyan bold",
        "path": "ansigreen bold",
        "arrow": "ansiyellow bold",
    })

    session = PromptSession(
        history=InMemoryHistory(),
        completer=ShellCompleter(),
        style=style
    )

    while True:
        try:
            prompt_tokens = make_prompt(executor.current_dir)
            command = session.prompt(prompt_tokens)

            output = executor.execute(command)

            if output == "EXIT":
                break
            elif output.strip():
                print(output)

        except KeyboardInterrupt:
            continue
        except EOFError:
            break

    # Graceful exit
    print("\nExiting MagicShell. Back to your terminal.")
    print(f"{os.getcwd()} >", end=" ")

if __name__ == "__main__":
    run_shell()