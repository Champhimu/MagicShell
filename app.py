import os
import platform
import sys
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion, PathCompleter, WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.styles import Style
from shell_commands import ShellCommandExecutor
from ai_integration import AIIntegration

os.environ["GRPC_VERBOSITY"] = "ERROR"  # Suppress GRPC-related warnings

# Define built-in commands for autocomplete
COMMANDS = [
    "cd", "ls", "pwd", "mkdir", "rm", "clear", "exit"
]

class ShellCompleter(Completer):
    """
    ShellCompleter is responsible for providing command and file path completions.
    """
    def __init__(self):
        # Initialize command and path completers
        self.cmd_completer = WordCompleter(COMMANDS, ignore_case=True)
        self.path_completer = PathCompleter(expanduser=True)
    
    # Get completeion based on the user input
    def get_completions(self, document, complete_event):
        text_before_cursor = document.text_before_cursor.lstrip()
        if " " not in text_before_cursor:
            # Command completion
            yield from self.cmd_completer.get_completions(document, complete_event)
        else:
            # Path completion
            yield from self.path_completer.get_completions(document, complete_event)

# Clear Terminal screen based on os
def clear_screen():
    os.system("cls" if platform.system() == "Windows" else "clear")

# Banner for shell interface
def print_banner(current_path):
    print("\n" + "=" * 40)
    print("       MagicShell ")
    print("=" * 40)
    print(f"Current Directory: {current_path}\n")

# Custom prompt format to display
def make_prompt(path):
    return [
        ("class:star", "MagicShell > "),
        ("class:path", f"{path} "),
        ("class:arrow", "> "),
    ]

# Main function to run the MagicShell interactive terminal.
def run_shell():

    clear_screen()  # Clear the screen when starting
    executor = ShellCommandExecutor()  # Initialize the command executor
    ai_integration = AIIntegration()  # Initialize AI integration
    print_banner(executor.current_dir)  # Print the banner with the current directory

    # Define the style for the prompt using ANSI colors
    style = Style.from_dict({
        "star": "ansicyan bold",
        "path": "ansigreen bold",
        "arrow": "ansiyellow bold",
    })

    # Initialize the prompt session with history, completer, and style
    session = PromptSession(
        history=InMemoryHistory(),
        completer=ShellCompleter(),
        style=style
    )

    while True:
        try:
            cwd = os.getcwd()  # Get the current working directory
            prompt_tokens = make_prompt(executor.current_dir)  # Generate the prompt tokens
            command = session.prompt(prompt_tokens)  # Prompt the user for input
            
            if command.startswith("/ai "):  # Check if the command is an AI request
                ai_prompt = command[len("/ai "):]  # Extract the prompt after "/ai "
                print(f"AI Processing: {ai_prompt}")  # Print what AI is processing
                ai_command = ai_integration.parse_natural_language(ai_prompt)

                print(f"AI Suggested Command: {ai_command}")  # Display AI's suggestion
                if ai_command.strip():
                    output = executor.execute(ai_command)  # Execute the suggested AI command
                    if output.strip():
                        print(output)  # Print the command output
                else:
                    print("AI could not generate a valid command.")  # AI failed to generate a command
            else: 
                output = executor.execute(command)  # Execute the normal shell command
                if output == "EXIT":
                    break  # Exit if the command is "exit"
                elif output.strip():
                    print(output)  # Print the output if any

        except KeyboardInterrupt:
            continue  # Allow to continue if Ctrl+C is pressed
        except EOFError:
            break  # Exit if (Ctrl+D) is encountered

    #Exit
    print("\nExiting MagicShell. Back to your terminal.")
    print(f"{os.getcwd()} >", end=" ")

if __name__ == "__main__":
    run_shell()  # Start the shell when this script is executed directly
