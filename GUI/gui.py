import os
import platform
import stat
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog

from prompt_toolkit.completion import Completer, WordCompleter, PathCompleter, CompleteEvent
from prompt_toolkit.document import Document
from prompt_toolkit.history import InMemoryHistory

from shell_core import ShellCore  # for executing shell commands (non-AI)

# --- COLORS & STYLES ---
BG = "#0d0d0d"
PANEL = "#1e1e1e"
OUT_BG = "#0b0b0b"
FG = "#ffffff"

BUTTON_BG = "#007bff"
BUTTON_FG = "#ffffff"
BUTTON_FONT = ("Helvetica", 11, "bold")
ENTRY_FONT = ("Consolas", 13)
OUTPUT_FONT = ("Consolas", 13)

RUN_BG = "#d9534f"
RUN_HOVER = "#c9302c"
RUN_FG = "#ffffff"

SIDEBAR_BG = "#121212"
SIDEBAR_BTN_BG = "#88929d"
SIDEBAR_BTN_FG = "#154c7e"
LOGO_ACCENT = "#00ffcc"

SUGGEST_BG = "#1a1a1a"
SUGGEST_FG = "#00ff80"
SUGGEST_HL_BG = "#333333"
SUGGEST_HL_FG = "#ffffff"

SNIPPETS = ["ls -la", "git status", "docker ps", "python3 -m http.server"]

# --- Prompt Toolkit Completer ---
class PTCompleter(Completer):
    def __init__(self, commands=None, history_lines=None):
        self.commands = sorted(set(commands or []))
        self.word_completer = WordCompleter(self.commands, ignore_case=True, sentence=True)
        self.path_completer = PathCompleter(expanduser=True)
        self.history = InMemoryHistory()
        if history_lines:
            for h in history_lines:
                self.history.append_string(h)

    def update_commands(self, commands):
        self.commands = sorted(set(commands))
        self.word_completer = WordCompleter(self.commands, ignore_case=True, sentence=True)

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        last = text.split()[-1] if text.split() else ""
        if last.startswith(("/", "./", "../", "~")) or ("/" in last and not last.isspace()):
            yield from self.path_completer.get_completions(document, complete_event)
        else:
            yield from self.word_completer.get_completions(document, complete_event)


def build_dynamic_commands(history_lines=None, include_compgen=True):
    cmds = set()
    for pdir in os.environ.get("PATH", "").split(os.pathsep):
        try:
            for name in os.listdir(pdir):
                full = os.path.join(pdir, name)
                try:
                    mode = os.stat(full).st_mode
                    if stat.S_ISREG(mode) and os.access(full, os.X_OK):
                        cmds.add(name)
                except Exception:
                    continue
        except Exception:
            continue
    if include_compgen and shutil.which("bash"):
        try:
            out = subprocess.check_output(["bash", "-lc", "compgen -c"], stderr=subprocess.DEVNULL, text=True)
            for l in out.splitlines():
                if l.strip():
                    cmds.add(l.strip())
        except Exception:
            pass
    cmds.update(SNIPPETS)
    if history_lines:
        for h in history_lines:
            h = h.strip()
            if not h:
                continue
            cmds.add(h)
            t = h.split()[0]
            if t:
                cmds.add(t)
    return sorted(cmds)


# --- Main GUI ---
class ShellGUI(tk.Tk):
    def __init__(self):
        super().__init__()                        # <-- self is the Tk root now
        self.title("Magic Shell GUI")
        self.geometry("1100x680")
        self.configure(bg=BG)

        # initialize core AFTER root exists
        self.core = ShellCore(self)
        self.pt_completer = None
        self._build_ui()

    def _build_ui(self):
        container = tk.Frame(self, bg=BG)
        container.pack(fill=tk.BOTH, expand=True)

        # Sidebar
        sidebar = tk.Frame(container, bg=SIDEBAR_BG, width=180)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)

        logo_frame = tk.Frame(sidebar, bg=SIDEBAR_BG, pady=12)
        logo_frame.pack(fill=tk.X)
        tk.Label(logo_frame, text="🌀", font=("Helvetica", 22), bg=SIDEBAR_BG, fg=LOGO_ACCENT).pack(side=tk.LEFT, padx=(12, 6))
        tk.Label(logo_frame, text="MAGIC\nSHELL", font=("Helvetica", 18, "bold"), bg=SIDEBAR_BG, fg="#00ffff", justify=tk.LEFT).pack(side=tk.LEFT)

        def make_side_btn(text, cmd=None):
            b = tk.Button(sidebar, text=text, command=(cmd or (lambda: None)),
                          bg=SIDEBAR_BTN_BG, fg=SIDEBAR_BTN_FG, bd=0, relief="flat",
                          anchor="w", padx=16, pady=10, font=("Helvetica", 15, "bold"))
            b.pack(fill=tk.X, padx=10, pady=4)
            b.bind("<Enter>", lambda e, btn=b: btn.config(bg="#3399ff"))
            b.bind("<Leave>", lambda e, btn=b: btn.config(bg=SIDEBAR_BTN_BG))
            return b

        make_side_btn("Home", self._go_home)
        make_side_btn("Chat with AI", self._chat_with_AI)
        make_side_btn("History", self._show_history)
        make_side_btn("Connect GIT", self._git_connected)
        make_side_btn("Connect Docker", self._docker_connected)
        make_side_btn("Settings", self._open_settings)
        make_side_btn("Exit", self.quit)

        # Main area
        main_area = tk.Frame(container, bg=BG)
        main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Top bar (CWD)
        top_frame = tk.Frame(main_area, bg=BG)
        top_frame.pack(fill=tk.X, padx=12, pady=8)
        tk.Label(top_frame, text="CWD:", fg=FG, bg=BG, font=("Helvetica", 12, "bold")).pack(side=tk.LEFT, padx=(0, 6))
        self.cwd_var = tk.StringVar(value=self.core.cwd)
        self.cwd_entry = tk.Entry(top_frame, textvariable=self.cwd_var, width=60, bg=PANEL, fg="#00ffff",
                                  insertbackground="#ffffff", font=ENTRY_FONT, relief="solid", bd=2)
        self.cwd_entry.pack(side=tk.LEFT, padx=(0, 10))
        tk.Button(top_frame, text="Set", command=self.set_cwd, bg=BUTTON_BG, fg=BUTTON_FG, font=BUTTON_FONT).pack(side=tk.LEFT, padx=4)
        tk.Button(top_frame, text="Browse", command=self.browse_folder, bg=BUTTON_BG, fg=BUTTON_FG, font=BUTTON_FONT).pack(side=tk.LEFT, padx=4)
        tk.Button(top_frame, text="Clear", command=self.clear_output, bg=BUTTON_BG, fg=BUTTON_FG, font=BUTTON_FONT).pack(side=tk.RIGHT, padx=4)
        tk.Button(top_frame, text="Stop", command=self.stop_command, bg="#f0ad4e", fg="#ffffff", font=BUTTON_FONT).pack(side=tk.RIGHT, padx=4)
        os_info = f"{platform.system()} {platform.release()} ({platform.machine()})"
        tk.Label(top_frame, text=os_info, fg="#00ff80", bg=BG, font=("Helvetica", 10, "bold")).pack(side=tk.RIGHT, padx=(0, 10))

        # Command input above output
        cmd_frame = tk.Frame(main_area, bg=BG)
        cmd_frame.pack(fill=tk.X, padx=12, pady=(6, 4))
        self.cmd_var = tk.StringVar()
        self.cmd_entry = tk.Entry(cmd_frame, textvariable=self.cmd_var, font=ENTRY_FONT,
                                  bg=PANEL, fg=FG, insertbackground="#ffffff", relief="solid", bd=2)
        self.cmd_entry.pack(fill=tk.X, side=tk.LEFT, expand=True, padx=(0, 8))
        self.cmd_entry.bind("<Return>", lambda e: self.run_command())
        self.cmd_entry.bind("<KeyRelease>", self._on_cmd_type)
        self.cmd_entry.bind("<Tab>", self._on_tab_complete)
        self.cmd_entry.bind("<Escape>", lambda e: self._hide_suggestions())
        self.cmd_entry.bind("<FocusOut>", lambda e: self.after(120, self._hide_suggestions))

        run_btn = tk.Label(cmd_frame, text="Run", bg=RUN_BG, fg=RUN_FG, font=("Helvetica", 12, "bold"), padx=20, pady=6,
                           relief="raised", bd=3, cursor="hand2")
        run_btn.pack(side=tk.LEFT)
        run_btn.bind("<Button-1>", lambda e: self.run_command())
        run_btn.bind("<Enter>", lambda e: run_btn.config(bg=RUN_HOVER))
        run_btn.bind("<Leave>", lambda e: run_btn.config(bg=RUN_BG))

        # Suggestion box
        self.suggestion_box = tk.Listbox(self, height=8, font=("Consolas", 12), bd=1, relief="solid",
                                         bg=SUGGEST_BG, fg=SUGGEST_FG,
                                         selectbackground=SUGGEST_HL_BG, selectforeground=SUGGEST_HL_FG)
        self.suggestion_box.bind("<<ListboxSelect>>", self._on_suggestion_click)
        self.suggestion_box.bind("<FocusOut>", lambda e: self.after(120, self._hide_suggestions))
        self.suggestion_box_visible = False

        # Output terminal
        self.output_text = scrolledtext.ScrolledText(main_area, width=140, height=28,
                                                     bg=OUT_BG, fg=FG, insertbackground="#ffffff",
                                                     font=OUTPUT_FONT, relief="solid", bd=2)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=12, pady=(6, 12))
        self._setup_tags()
        self.insert_text(f"Current directory: {self.core.cwd}", "success")

        hist_lines = self._load_history()
        cmd_list = build_dynamic_commands(history_lines=hist_lines, include_compgen=(platform.system() != "Windows"))
        self.pt_completer = PTCompleter(commands=cmd_list, history_lines=hist_lines)
        self.bind_all("<Button-1>", self._global_click, add="+")

    # Tag setup
    def _setup_tags(self):
        self.output_text.tag_config("command", foreground="#7fff7f", font=("Consolas", 13, "bold"))
        self.output_text.tag_config("stdout", foreground="#cccccc", font=("Consolas", 13))
        self.output_text.tag_config("stderr", foreground="#ffb86b", font=("Consolas", 13, "bold"))
        self.output_text.tag_config("success", foreground="#9ae6b4", font=("Consolas", 13, "bold"))
        self.output_text.tag_config("error", foreground="#ff6b6b", font=("Consolas", 13, "bold"))

    # Utilities
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

    # Command execution
    def run_command(self):
        cmd = self.cmd_var.get().strip()
        if not cmd:
            return
        self.insert_text(f"> {cmd}", "command")
        self._append_history(cmd)
        self.core.run_command(cmd)

    def stop_command(self):
        stopped = self.core.stop_running()
        msg = "Stopped running command." if stopped else "No process running."
        self.insert_text(msg, "error")

    # Sidebar actions
    def _go_home(self):
        self.insert_text("Home clicked", "success")

    def _open_settings(self):
        self.insert_text("Settings clicked", "success")

    def _git_connected(self):
        self.insert_text("Git status: placeholder", "stdout")

    def _docker_connected(self):
        self.insert_text("Docker status: placeholder", "stdout")

    def _show_history(self):
        hist = self._load_history()
        self.insert_text("Command History:", "success")
        for i, c in enumerate(hist[-50:], start=1):
            self.insert_text(f"{i}. {c}", "stdout")

    def _chat_with_AI(self):
        self.insert_text("Chat with AI", "success")

    # Suggestions
    def _on_cmd_type(self, event=None):
        text = self.cmd_var.get()
        if not text:
            self._hide_suggestions()
            return
        try:
            doc = Document(text, cursor_position=len(text))
            ce = CompleteEvent()
            completions = list(self.pt_completer.get_completions(doc, ce))
        except Exception:
            completions = []
        suggestions = [comp.text for comp in completions[:50]]
        if suggestions:
            self._show_suggestions(suggestions)
        else:
            self._hide_suggestions()

    def _show_suggestions(self, suggestions):
        self.update_idletasks()
        entry_root_x = self.cmd_entry.winfo_rootx()
        entry_root_y = self.cmd_entry.winfo_rooty()
        entry_width = self.cmd_entry.winfo_width()
        entry_height = self.cmd_entry.winfo_height()
        win_root_x = self.winfo_rootx()
        win_root_y = self.winfo_rooty()
        rel_x = entry_root_x - win_root_x
        rel_y = entry_root_y - win_root_y + entry_height + 3
        self.suggestion_box.place(x=rel_x, y=rel_y, width=entry_width)
        self.suggestion_box.lift()
        self.suggestion_box_visible = True
        self.suggestion_box.delete(0, tk.END)
        for s in suggestions[:12]:
            self.suggestion_box.insert(tk.END, s)

    def _hide_suggestions(self):
        if self.suggestion_box_visible:
            self.suggestion_box.place_forget()
            self.suggestion_box_visible = False

    def _on_suggestion_click(self, event):
        sel = self.suggestion_box.curselection()
        if not sel:
            return
        cmd = self.suggestion_box.get(sel[0])
        self.cmd_var.set(cmd)
        self._hide_suggestions()
        self.cmd_entry.focus_set()

    def _on_tab_complete(self, event):
        if self.suggestion_box_visible and self.suggestion_box.size() > 0:
            cmd = self.suggestion_box.get(0)
            self.cmd_var.set(cmd)
            self._hide_suggestions()
            return "break"

    def _global_click(self, event):
        wid = event.widget
        if wid is self.suggestion_box or wid is self.cmd_entry:
            return
        self.after(80, self._hide_suggestions)

    # History management
    def _history_file(self):
        return os.path.join(self.core.cwd, ".magicshell_history")

    def _append_history(self, cmd):
        try:
            with open(self._history_file(), "a", encoding="utf-8") as f:
                f.write(cmd.replace("\n", " ") + "\n")
        except Exception:
            pass

    def _load_history(self):
        try:
            with open(self._history_file(), "r", encoding="utf-8") as f:
                return [l.strip() for l in f.readlines() if l.strip()]
        except Exception:
            return []


if __name__ == "__main__":
    app = ShellGUI()
    app.mainloop()
