# shell_core.py
import os
import subprocess
import threading
import shutil
import signal

class ShellCore:
    def __init__(self, gui):
        self.gui = gui
        self.cwd = os.getcwd()
        self.proc = None
        self.lock = threading.Lock()

    # --- Directory handling ---
    def set_cwd(self, path):
        abs_path = os.path.abspath(path)
        if os.path.isdir(abs_path):
            self.cwd = abs_path
            return True
        return False

    # --- Command validation ---
    def validate_command(self, command):
        """
        Validate whether the entered command exists in system PATH or is built-in.
        """
        parts = command.strip().split()
        if not parts:
            return False, "Empty command"

        cmd = parts[0]

        # Check for built-in commands
        builtins = ["cd", "echo", "pwd"]
        if cmd in builtins:
            return True, "builtin"

        # Check if the command exists in PATH
        if shutil.which(cmd) is not None:
            return True, "external"

        return False, f"'{cmd}' not found in system PATH"

    # --- Command runner ---
    def run_command(self, command):
        valid, msg = self.validate_command(command)

        if not valid:
            self.gui.insert_text(f"Invalid command: {msg}", "error")
            return

        parts = command.strip().split()
        if parts[0] == "cd":
            self._handle_cd(parts)
            return

        thread = threading.Thread(target=self._execute_command, args=(command,), daemon=True)
        thread.start()

    def _handle_cd(self, parts):
        if len(parts) == 1:
            new_dir = os.path.expanduser("~")
        else:
            new_dir = parts[1]

        new_path = os.path.abspath(os.path.join(self.cwd, new_dir))
        if os.path.isdir(new_path):
            self.cwd = new_path
            self.gui.cwd_var.set(self.cwd)
            self.gui.insert_text(f"Changed directory to: {self.cwd}", "success")
        else:
            self.gui.insert_text("Directory not found", "error")

    # --- Execution Thread ---
    def _execute_command(self, command):
        try:
            with self.lock:
                self.proc = subprocess.Popen(
                    command,
                    shell=True,
                    cwd=self.cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

            # Stream output
            for line in self.proc.stdout:
                self.gui.insert_text(line.rstrip(), "stdout")
            for line in self.proc.stderr:
                self.gui.insert_text(line.rstrip(), "stderr")

            self.proc.wait()
            code = self.proc.returncode
            if code == 0:
                self.gui.insert_text(f"Command finished successfully.", "success")
            else:
                self.gui.insert_text(f"Command exited with code {code}", "error")

        except Exception as e:
            self.gui.insert_text(f"Error: {e}", "error")

        finally:
            with self.lock:
                self.proc = None

    # --- Stop Running Command ---
    def stop_running(self):
        with self.lock:
            if self.proc and self.proc.poll() is None:
                try:
                    os.killpg(os.getpgid(self.proc.pid), signal.SIGTERM)
                except Exception:
                    self.proc.terminate()
                return True
        return False
