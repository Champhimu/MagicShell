# gui.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from shell_core import ShellCore

# --- UI COLORS AND STYLE ---
BG = "#0d0d0d"
PANEL = "#1e1e1e"
OUT_BG = "#0b0b0b"
FG = "#dcdcdc"

BUTTON_BG = "#efefef"
BUTTON_FG = "#111111"
BUTTON_FONT = ("Helvetica", 11, "bold")
ENTRY_FONT = ("Consolas", 13)
OUTPUT_FONT = ("Consolas", 13)

RUN_BG = "#d9534f"      # red button background
RUN_HOVER = "#c9302c"
RUN_FG = "#ffffff"

class ShellGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Magic Shell GUI")
        self.geometry("980x620")
        self.configure(bg=BG)

        # Try to use a cross-platform theme so colors are more controllable on macOS
        try:
            style = ttk.Style(self)
            # 'clam' is a non-native theme that respects widget background colors better
            style.theme_use("clam")
        except Exception:
            pass

        self.core = ShellCore(self)
        self._build_ui()

    def _build_ui(self):
        # Top: CWD + small utility buttons
        top_frame = tk.Frame(self, bg=BG)
        top_frame.pack(fill=tk.X, padx=10, pady=8)

        tk.Label(top_frame, text="CWD:", fg=FG, bg=BG, font=("Helvetica", 12, "bold")).pack(side=tk.LEFT, padx=(0, 6))

        self.cwd_var = tk.StringVar(value=self.core.cwd)
        self.cwd_entry = tk.Entry(
            top_frame, textvariable=self.cwd_var, width=62,
            bg=PANEL, fg="#7fffd4", insertbackground="#ffffff",
            font=ENTRY_FONT, relief="solid", bd=2
        )
        self.cwd_entry.pack(side=tk.LEFT, padx=(0, 10))

        # Small helper to create visible buttons
        def make_button(parent, text, cmd, bg=BUTTON_BG, fg=BUTTON_FG, width=10):
            b = tk.Button(parent, text=text, command=cmd,
                          bg=bg, fg=fg, font=BUTTON_FONT,
                          padx=8, pady=3, bd=2, relief="raised", width=width)
            return b

        make_button(top_frame, "Set", self.set_cwd).pack(side=tk.LEFT, padx=4)
        make_button(top_frame, "Browse", self.browse_folder).pack(side=tk.LEFT, padx=4)
        make_button(top_frame, "Clear", self.clear_output).pack(side=tk.RIGHT, padx=4)
        make_button(top_frame, "Stop", self.stop_command, bg="#f0ad4e", fg="#ffffff", width=8).pack(side=tk.RIGHT, padx=4)

        # Scrollable quick-command bar (horizontal)
        quick_outer = tk.Frame(self, bg=BG)
        quick_outer.pack(fill=tk.X, padx=10)

        canvas = tk.Canvas(quick_outer, height=48, bg=BG, highlightthickness=0)
        hbar = tk.Scrollbar(quick_outer, orient=tk.HORIZONTAL, command=canvas.xview)
        canvas.configure(xscrollcommand=hbar.set)
        hbar.pack(side=tk.BOTTOM, fill=tk.X)
        canvas.pack(side=tk.LEFT, fill=tk.X, expand=True)

        quick_frame = tk.Frame(canvas, bg=BG)
        canvas.create_window((0, 0), window=quick_frame, anchor="nw")

        def on_config(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        quick_frame.bind("<Configure>", on_config)

        quick_cmds = [
            ("ls", "ls -la"), ("pwd", "pwd"), ("whoami", "whoami"),
            ("date", "date"), ("uptime", "uptime"), ("ps", "ps aux"),
            ("df", "df -h"), ("du", "du -sh ."), ("git status", "git status"),
            ("python", "python3 --version"), ("pip", "pip3 --version"),
        ]
        for label, cmd in quick_cmds:
            btn = tk.Button(quick_frame, text=label, command=lambda c=cmd: self.run_quick(c),
                            bg=BUTTON_BG, fg=BUTTON_FG, font=BUTTON_FONT,
                            padx=8, pady=2, width=12, relief="raised", bd=2)
            btn.pack(side=tk.LEFT, padx=(4, 2), pady=6)

        # Command entry area
        cmd_frame = tk.Frame(self, bg=BG)
        cmd_frame.pack(fill=tk.X, padx=10, pady=(6, 8))

        self.cmd_var = tk.StringVar()
        self.cmd_entry = tk.Entry(cmd_frame, textvariable=self.cmd_var, font=ENTRY_FONT,
                                  bg=PANEL, fg=FG, insertbackground="#ffffff", relief="solid", bd=2)
        self.cmd_entry.pack(fill=tk.X, side=tk.LEFT, expand=True, padx=(0, 8))
        self.cmd_entry.bind("<Return>", lambda e: self.run_command())

        # --- Custom red Run button implemented as a Label so color is respected on macOS ---
        run_btn = tk.Label(cmd_frame, text="Run", bg=RUN_BG, fg=RUN_FG,
                           font=("Helvetica", 12, "bold"), padx=20, pady=6,
                           relief="raised", bd=3, cursor="hand2")
        run_btn.pack(side=tk.LEFT)

        # Bind click + hover to make it feel like a button
        run_btn.bind("<Button-1>", lambda e: self.run_command())
        run_btn.bind("<Enter>", lambda e: run_btn.config(bg=RUN_HOVER))
        run_btn.bind("<Leave>", lambda e: run_btn.config(bg=RUN_BG))

        # Output terminal
        self.output_text = scrolledtext.ScrolledText(self, width=140, height=28,
                                                     bg=OUT_BG, fg=FG, insertbackground="#ffffff",
                                                     font=OUTPUT_FONT, relief="solid", bd=2)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self._setup_tags()
        self.insert_text(f"Current directory: {self.core.cwd}", "success")

    def _setup_tags(self):
        self.output_text.tag_config("command", foreground="#7fff7f", font=("Consolas", 13, "bold"))
        self.output_text.tag_config("stdout", foreground="#cccccc", font=("Consolas", 13))
        self.output_text.tag_config("stderr", foreground="#ffb86b", font=("Consolas", 13, "bold"))
        self.output_text.tag_config("success", foreground="#9ae6b4", font=("Consolas", 13, "bold"))
        self.output_text.tag_config("error", foreground="#ff6b6b", font=("Consolas", 13, "bold"))

    # Utility methods
    def insert_text(self, text, tag=None):
        self.output_text.configure(state=tk.NORMAL)
        if tag:
            self.output_text.insert(tk.END, text + "\n", tag)
        else:
            self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)
        self.output_text.configure(state=tk.DISABLED)

    def clear_output(self):
        self.output_text.configure(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.configure(state=tk.DISABLED)

    def set_cwd(self):
        new_dir = self.cwd_var.get().strip()
        if new_dir:
            ok = self.core.set_cwd(new_dir)
            tag = "success" if ok else "error"
            msg = f"Changed directory to: {self.core.cwd}" if ok else f"Directory not found: {new_dir}"
            self.insert_text(msg, tag)

    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.core.cwd)
        if folder:
            self.cwd_var.set(folder)
            self.core.set_cwd(folder)
            self.insert_text(f"Changed directory to: {self.core.cwd}", "success")

    # Execution methods
    def run_command(self):
        cmd = self.cmd_var.get().strip()
        if not cmd:
            return

        # Dangerous command check (simple heuristics)
        dangerous_keywords = ["rm", "mv", "rmdir", "chmod", "chown", "shutdown", "reboot", "kill", "dd", ":(){:|:&};:"]
        # Check if command starts with a dangerous keyword or contains it as a standalone token
        cmd_lower = cmd.lower()
        is_dangerous = False
        for d in dangerous_keywords:
            if cmd_lower.startswith(d) or f" {d} " in cmd_lower:
                is_dangerous = True
                break

        if is_dangerous:
            warn = f"⚠️ This command may be dangerous:\n\n{cmd}\n\nAre you sure you want to execute it?"
            if not messagebox.askyesno("Confirm Dangerous Command", warn):
                self.insert_text(f"Command '{cmd}' cancelled by user.", "error")
                return

        self.insert_text(f"> {cmd}", "command")
        self.core.run_command(cmd)

    def stop_command(self):
        stopped = self.core.stop_running()
        msg = "Stopped running command." if stopped else "No process running."
        self.insert_text(msg, "error")

    def run_quick(self, cmd):
        self.cmd_var.set(cmd)
        self.run_command()
