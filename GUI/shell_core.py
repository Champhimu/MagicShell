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

    # directory
    def set_cwd(self, path):
        abs_path = os.path.abspath(path)
        if os.path.isdir(abs_path):
            self.cwd = abs_path
            return True
        return False

    # validation
    def validate_command(self, command):
        parts = command.strip().split()
        if not parts:
            return False, "Empty command"
        cmd = parts[0]
        builtins = ["cd", "echo", "pwd", "clear", "exit"]
        if cmd in builtins:
            return True, "builtin"
        if shutil.which(cmd) is not None:
            return True, "external"
        return False, f"'{cmd}' not found in PATH"

    # run
    def run_command(self, command):
        command = command.strip()
        if not command:
            return

        valid, msg = self.validate_command(command)
        if not valid:
            self.gui.insert_text(f"Invalid command: {msg}", "error")
            return

        parts = command.split()
        if parts[0] == "cd":
            self._handle_cd(parts)
            return
        if parts[0] == "clear":
            self.gui.clear_output()
            return
        if parts[0] == "exit":
            try:
                self.gui.quit()
            except Exception:
                pass
            return

        t = threading.Thread(target=self._execute_command, args=(command,), daemon=True)
        t.start()

    def _handle_cd(self, parts):
        if len(parts) == 1:
            new_dir = os.path.expanduser("~")
        else:
            new_dir = parts[1]
        new_path = os.path.abspath(os.path.join(self.cwd, new_dir))
        if os.path.isdir(new_path):
            self.cwd = new_path
            try:
                self.gui.cwd_var.set(self.cwd)
            except Exception:
                pass
            self.gui.insert_text(f"Changed directory to: {self.cwd}", "success")
        else:
            self.gui.insert_text("Directory not found", "error")

    def _execute_command(self, command):
        try:
            with self.lock:
                # start process in its own process group so we can kill group
                self.proc = subprocess.Popen(
                    command,
                    shell=True,
                    cwd=self.cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    preexec_fn=os.setsid if hasattr(os, "setsid") else None
                )

            # stream stdout
            for line in iter(self.proc.stdout.readline, ""):
                if line:
                    self.gui.insert_text(line.rstrip(), "stdout")
            # stream stderr
            for line in iter(self.proc.stderr.readline, ""):
                if line:
                    self.gui.insert_text(line.rstrip(), "stderr")

            self.proc.wait()
            rc = self.proc.returncode
            if rc == 0:
                self.gui.insert_text("Command finished successfully.", "success")
            else:
                self.gui.insert_text(f"Command exited with code {rc}", "error")

        except Exception as e:
            self.gui.insert_text(f"Execution error: {e}", "error")
        finally:
            with self.lock:
                self.proc = None

    def stop_running(self):
        with self.lock:
            if self.proc and self.proc.poll() is None:
                try:
                    os.killpg(os.getpgid(self.proc.pid), signal.SIGTERM)
                except Exception:
                    try:
                        self.proc.terminate()
                    except Exception:
                        pass
                return True
        return False
