import os
import platform
import subprocess
import shutil
from safety import is_dangerous_command

class ShellCommandExecutor:
    def __init__(self):
        self.current_dir = os.getcwd()

    def execute(self, command):
        command = command.strip()
        if not command:
            return ""

        parts = command.split()
        cmd = parts[0]
        args = parts[1:]

        if is_dangerous_command(cmd):
            if not self.confirm("You are about to delete a file or directory. Proceed? (Y/N)"):
                return "Aborted by user"
            
        # Built-in commands
        if cmd == "cd":
            return self.change_directory(args)
        elif cmd == "pwd":
            return self.current_dir
        elif cmd == "exit":
            return "EXIT"
        elif cmd == "clear":
            return self.clear_screen()

        # Safe wrapper for standard shell commands
        return self.run_system_command(command)

    def change_directory(self, args):
        if not args:
            return "Usage: cd <directory>"

        target = args[0]
        try:
            new_path = os.path.abspath(os.path.join(self.current_dir, target))
            os.chdir(new_path)
            self.current_dir = new_path
            return ""
        except FileNotFoundError:
            return f"No such directory: {target}"
        except Exception as e:
            return str(e)

    def clear_screen(self):
        os.system("cls" if platform.system() == "Windows" else "clear")
        return ""

    def run_system_command(self, command):
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, cwd=self.current_dir
            )
            return result.stdout + result.stderr
        except Exception as e:
            return str(e)

    def confirm(self, prompt_text):
        while True:
            ans = input(prompt_text + " ").strip().lower()
            if ans == 'y':
                return True
            elif ans == 'n':
                return False