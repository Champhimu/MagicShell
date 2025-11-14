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
from color_themes import ColorTheme
from settings_dialog import SettingsDialog
from command_safety import CommandSafety

# --- COLORS & STYLES (Dynamic, managed by ColorTheme) ---
# These will be updated from the theme manager
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

CWD_FG = "#00ffff"
OS_INFO_FG = "#00ff80"

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
        
        # Initialize theme manager and load colors
        self.theme_manager = ColorTheme()
        self._load_theme_colors()
        self.configure(bg=self.colors["BG"])

        # initialize core AFTER root exists
        self.core = ShellCore(self)
        self.pt_completer = None
        
        # Initialize safety system
        self.safety_checker = CommandSafety(self)
        
        # Store references to widgets for theme updates
        self.themed_widgets = []
        
        self._build_ui()

    def _load_theme_colors(self):
        """Load current theme colors into instance variables"""
        self.colors = self.theme_manager.get_current_theme()
        
        # Update global color variables for compatibility
        global BG, PANEL, OUT_BG, FG, BUTTON_BG, BUTTON_FG, RUN_BG, RUN_HOVER, RUN_FG
        global SIDEBAR_BG, SIDEBAR_BTN_BG, SIDEBAR_BTN_FG, LOGO_ACCENT
        global SUGGEST_BG, SUGGEST_FG, SUGGEST_HL_BG, SUGGEST_HL_FG, CWD_FG, OS_INFO_FG
        
        BG = self.colors["BG"]
        PANEL = self.colors["PANEL"]
        OUT_BG = self.colors["OUT_BG"]
        FG = self.colors["FG"]
        BUTTON_BG = self.colors["BUTTON_BG"]
        BUTTON_FG = self.colors["BUTTON_FG"]
        RUN_BG = self.colors["RUN_BG"]
        RUN_HOVER = self.colors["RUN_HOVER"]
        RUN_FG = self.colors["RUN_FG"]
        SIDEBAR_BG = self.colors["SIDEBAR_BG"]
        SIDEBAR_BTN_BG = self.colors["SIDEBAR_BTN_BG"]
        SIDEBAR_BTN_FG = self.colors["SIDEBAR_BTN_FG"]
        LOGO_ACCENT = self.colors["LOGO_ACCENT"]
        SUGGEST_BG = self.colors["SUGGEST_BG"]
        SUGGEST_FG = self.colors["SUGGEST_FG"]
        SUGGEST_HL_BG = self.colors["SUGGEST_HL_BG"]
        SUGGEST_HL_FG = self.colors["SUGGEST_HL_FG"]
        CWD_FG = self.colors["CWD_FG"]
        OS_INFO_FG = self.colors["OS_INFO_FG"]
    
    def _lighten_color(self, hex_color, factor=0.3):
        """Lighten a hex color by a given factor for hover effects"""
        try:
            # Remove # if present
            hex_color = hex_color.lstrip('#')
            
            # Convert to RGB
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            # Lighten each component
            r = min(255, int(r + (255 - r) * factor))
            g = min(255, int(g + (255 - g) * factor))
            b = min(255, int(b + (255 - b) * factor))
            
            # Convert back to hex
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            # Fallback to a safe hover color
            return "#4CAF50"

    def _build_ui(self):
        container = tk.Frame(self, bg=self.colors["BG"])
        container.pack(fill=tk.BOTH, expand=True)
        self.themed_widgets.append(("container", container, "bg"))

        # Sidebar
        self.sidebar = tk.Frame(container, bg=self.colors["SIDEBAR_BG"], width=180)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.themed_widgets.append(("sidebar", self.sidebar, "bg"))

        self.logo_frame = tk.Frame(self.sidebar, bg=self.colors["SIDEBAR_BG"], pady=12)
        self.logo_frame.pack(fill=tk.X)
        self.themed_widgets.append(("logo_frame", self.logo_frame, "bg"))
        
        self.logo_icon = tk.Label(self.logo_frame, text="🌀", font=("Helvetica", 22), 
                                 bg=self.colors["SIDEBAR_BG"], fg=self.colors["LOGO_ACCENT"])
        self.logo_icon.pack(side=tk.LEFT, padx=(12, 6))
        self.themed_widgets.append(("logo_icon", self.logo_icon, "bg"))
        self.themed_widgets.append(("logo_icon", self.logo_icon, "fg"))
        
        self.logo_text = tk.Label(self.logo_frame, text="MAGIC\nSHELL", font=("Helvetica", 18, "bold"), 
                                 bg=self.colors["SIDEBAR_BG"], fg="#00ffff", justify=tk.LEFT)
        self.logo_text.pack(side=tk.LEFT)
        self.themed_widgets.append(("logo_text", self.logo_text, "bg"))

        def make_side_btn(text, cmd=None):
            b = tk.Button(self.sidebar, text=text, command=(cmd or (lambda: None)),
                          bg=self.colors["SIDEBAR_BTN_BG"], fg=self.colors["SIDEBAR_BTN_FG"], bd=0, relief="flat",
                          anchor="w", padx=16, pady=10, font=("Helvetica", 15, "bold"))
            b.pack(fill=tk.X, padx=10, pady=4)
            # Use a lighter version of the button color for hover
            hover_color = self._lighten_color(self.colors["SIDEBAR_BTN_BG"])
            b.bind("<Enter>", lambda e, btn=b: btn.config(bg=hover_color, fg="#ffffff"))
            b.bind("<Leave>", lambda e, btn=b: btn.config(bg=self.colors["SIDEBAR_BTN_BG"], fg=self.colors["SIDEBAR_BTN_FG"]))
            self.themed_widgets.append((f"sidebar_btn_{text}", b, "bg"))
            self.themed_widgets.append((f"sidebar_btn_{text}", b, "fg"))
            return b

        self.sidebar_buttons = []
        self.sidebar_buttons.append(make_side_btn("Home", self._go_home))
        self.sidebar_buttons.append(make_side_btn("Chat with AI", self._chat_with_AI))
        self.sidebar_buttons.append(make_side_btn("History", self._show_history))
        self.sidebar_buttons.append(make_side_btn("Connect GIT", self._git_connected))
        self.sidebar_buttons.append(make_side_btn("Connect Docker", self._docker_connected))
        self.sidebar_buttons.append(make_side_btn("Settings", self._open_settings))
        self.sidebar_buttons.append(make_side_btn("Exit", self.quit))

        # Main area
        self.main_area = tk.Frame(container, bg=self.colors["BG"])
        self.main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.themed_widgets.append(("main_area", self.main_area, "bg"))

        # Top bar (CWD)
        self.top_frame = tk.Frame(self.main_area, bg=self.colors["BG"])
        self.top_frame.pack(fill=tk.X, padx=12, pady=8)
        self.themed_widgets.append(("top_frame", self.top_frame, "bg"))
        
        self.cwd_label = tk.Label(self.top_frame, text="CWD:", fg=self.colors["FG"], bg=self.colors["BG"], font=("Helvetica", 12, "bold"))
        self.cwd_label.pack(side=tk.LEFT, padx=(0, 6))
        self.themed_widgets.append(("cwd_label", self.cwd_label, "bg"))
        self.themed_widgets.append(("cwd_label", self.cwd_label, "fg"))
        
        self.cwd_var = tk.StringVar(value=self.core.cwd)
        self.cwd_entry = tk.Entry(self.top_frame, textvariable=self.cwd_var, width=60, bg=self.colors["PANEL"], fg=self.colors["CWD_FG"],
                                  insertbackground="#ffffff", font=ENTRY_FONT, relief="solid", bd=2)
        self.cwd_entry.pack(side=tk.LEFT, padx=(0, 10))
        self.themed_widgets.append(("cwd_entry", self.cwd_entry, "bg"))
        self.themed_widgets.append(("cwd_entry", self.cwd_entry, "fg"))
        
        self.set_btn = tk.Button(self.top_frame, text="Set", command=self.set_cwd, bg=self.colors["BUTTON_BG"], fg=self.colors["BUTTON_FG"], font=BUTTON_FONT)
        self.set_btn.pack(side=tk.LEFT, padx=4)
        self.themed_widgets.append(("set_btn", self.set_btn, "bg"))
        self.themed_widgets.append(("set_btn", self.set_btn, "fg"))
        
        self.browse_btn = tk.Button(self.top_frame, text="Browse", command=self.browse_folder, bg=self.colors["BUTTON_BG"], fg=self.colors["BUTTON_FG"], font=BUTTON_FONT)
        self.browse_btn.pack(side=tk.LEFT, padx=4)
        self.themed_widgets.append(("browse_btn", self.browse_btn, "bg"))
        self.themed_widgets.append(("browse_btn", self.browse_btn, "fg"))
        
        self.clear_btn = tk.Button(self.top_frame, text="Clear", command=self.clear_output, bg=self.colors["BUTTON_BG"], fg=self.colors["BUTTON_FG"], font=BUTTON_FONT)
        self.clear_btn.pack(side=tk.RIGHT, padx=4)
        self.themed_widgets.append(("clear_btn", self.clear_btn, "bg"))
        self.themed_widgets.append(("clear_btn", self.clear_btn, "fg"))
        
        self.stop_btn = tk.Button(self.top_frame, text="Stop", command=self.stop_command, bg="#f0ad4e", fg="#ffffff", font=BUTTON_FONT)
        self.stop_btn.pack(side=tk.RIGHT, padx=4)
        
        os_info = f"{platform.system()} {platform.release()} ({platform.machine()})"
        self.os_info_label = tk.Label(self.top_frame, text=os_info, fg=self.colors["OS_INFO_FG"], bg=self.colors["BG"], font=("Helvetica", 10, "bold"))
        self.os_info_label.pack(side=tk.RIGHT, padx=(0, 10))
        self.themed_widgets.append(("os_info_label", self.os_info_label, "bg"))
        self.themed_widgets.append(("os_info_label", self.os_info_label, "fg"))

        # Command input above output
        self.cmd_frame = tk.Frame(self.main_area, bg=self.colors["BG"])
        self.cmd_frame.pack(fill=tk.X, padx=12, pady=(6, 4))
        self.themed_widgets.append(("cmd_frame", self.cmd_frame, "bg"))
        
        self.cmd_var = tk.StringVar()
        self.cmd_entry = tk.Entry(self.cmd_frame, textvariable=self.cmd_var, font=ENTRY_FONT,
                                  bg=self.colors["PANEL"], fg=self.colors["FG"], insertbackground="#ffffff", relief="solid", bd=2)
        self.cmd_entry.pack(fill=tk.X, side=tk.LEFT, expand=True, padx=(0, 8))
        self.cmd_entry.bind("<Return>", lambda e: self.run_command())
        self.cmd_entry.bind("<KeyRelease>", self._on_cmd_type)
        self.cmd_entry.bind("<Tab>", self._on_tab_complete)
        self.cmd_entry.bind("<Escape>", lambda e: self._hide_suggestions())
        self.cmd_entry.bind("<FocusOut>", lambda e: self.after(120, self._hide_suggestions))
        self.themed_widgets.append(("cmd_entry", self.cmd_entry, "bg"))
        self.themed_widgets.append(("cmd_entry", self.cmd_entry, "fg"))

        self.run_btn = tk.Label(self.cmd_frame, text="Run", bg=self.colors["RUN_BG"], fg=self.colors["RUN_FG"], font=("Helvetica", 12, "bold"), padx=20, pady=6,
                           relief="raised", bd=3, cursor="hand2")
        self.run_btn.pack(side=tk.LEFT)
        self.run_btn.bind("<Button-1>", lambda e: self.run_command())
        self.run_btn.bind("<Enter>", lambda e: self.run_btn.config(bg=self.colors["RUN_HOVER"]))
        self.run_btn.bind("<Leave>", lambda e: self.run_btn.config(bg=self.colors["RUN_BG"]))
        self.themed_widgets.append(("run_btn", self.run_btn, "bg"))
        self.themed_widgets.append(("run_btn", self.run_btn, "fg"))
        
        # Safety indicator
        self.safety_indicator = tk.Label(self.cmd_frame, text="✅", font=("Helvetica", 14), 
                                        bg=self.colors["BG"], fg="#28a745", padx=5)
        self.safety_indicator.pack(side=tk.LEFT, padx=(5, 0))
        self.themed_widgets.append(("safety_indicator", self.safety_indicator, "bg"))

        # Suggestion box
        self.suggestion_box = tk.Listbox(self, height=8, font=("Consolas", 12), bd=1, relief="solid",
                                         bg=self.colors["SUGGEST_BG"], fg=self.colors["SUGGEST_FG"],
                                         selectbackground=self.colors["SUGGEST_HL_BG"], selectforeground=self.colors["SUGGEST_HL_FG"])
        self.suggestion_box.bind("<<ListboxSelect>>", self._on_suggestion_click)
        self.suggestion_box.bind("<FocusOut>", lambda e: self.after(120, self._hide_suggestions))
        self.suggestion_box_visible = False
        self.themed_widgets.append(("suggestion_box", self.suggestion_box, "bg"))
        self.themed_widgets.append(("suggestion_box", self.suggestion_box, "fg"))

        # Output terminal
        self.output_text = scrolledtext.ScrolledText(self.main_area, width=140, height=28,
                                                     bg=self.colors["OUT_BG"], fg=self.colors["FG"], insertbackground="#ffffff",
                                                     font=OUTPUT_FONT, relief="solid", bd=2)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=12, pady=(6, 12))
        self.themed_widgets.append(("output_text", self.output_text, "bg"))
        self.themed_widgets.append(("output_text", self.output_text, "fg"))
        
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
            
        # Enhanced safety check
        is_dangerous, analysis = self.safety_checker.analyze_command(cmd)
        
        if is_dangerous:
            # Show comprehensive warning dialog
            if not self.safety_checker.show_warning_dialog(analysis):
                self.insert_text(f"❌ Command cancelled by user: {cmd}", "error")
                self.insert_text(f"   Risk level: {analysis['risk_level'].upper()}", "error")
                return
            else:
                self.insert_text(f"⚠️ Executing dangerous command (user confirmed): {cmd}", "stderr")
                self.insert_text(f"   Risk level: {analysis['risk_level'].upper()}", "stderr")
        
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
        """Open the settings dialog with theme customization"""
        try:
            settings_dialog = SettingsDialog(self, self.theme_manager, self._apply_theme_callback)
        except Exception as e:
            self.insert_text(f"Error opening settings: {str(e)}", "error")

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
        
        # Update safety indicator
        self._update_safety_indicator(text)
        
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
    
    def _apply_theme_callback(self):
        """Callback function to apply new theme to GUI"""
        try:
            # Reload theme colors
            self._load_theme_colors()
            
            # Update root window background
            self.configure(bg=self.colors["BG"])
            
            # Update all themed widgets
            for widget_name, widget, prop in self.themed_widgets:
                try:
                    if prop == "bg":
                        if "sidebar_btn" in widget_name:
                            widget.configure(bg=self.colors["SIDEBAR_BTN_BG"])
                        elif widget_name == "logo_icon":
                            widget.configure(bg=self.colors["SIDEBAR_BG"])
                        elif widget_name == "logo_text":
                            widget.configure(bg=self.colors["SIDEBAR_BG"])
                        elif "btn" in widget_name and widget_name not in ["run_btn"]:
                            widget.configure(bg=self.colors["BUTTON_BG"])
                        elif widget_name == "run_btn":
                            widget.configure(bg=self.colors["RUN_BG"])
                        elif widget_name == "cwd_entry" or widget_name == "cmd_entry":
                            widget.configure(bg=self.colors["PANEL"])
                        elif widget_name == "output_text":
                            widget.configure(bg=self.colors["OUT_BG"])
                        elif widget_name == "suggestion_box":
                            widget.configure(bg=self.colors["SUGGEST_BG"])
                        elif "sidebar" in widget_name:
                            widget.configure(bg=self.colors["SIDEBAR_BG"])
                        else:
                            widget.configure(bg=self.colors["BG"])
                            
                    elif prop == "fg":
                        if "sidebar_btn" in widget_name:
                            widget.configure(fg=self.colors["SIDEBAR_BTN_FG"])
                        elif widget_name == "logo_icon":
                            widget.configure(fg=self.colors["LOGO_ACCENT"])
                        elif widget_name == "cwd_entry":
                            widget.configure(fg=self.colors["CWD_FG"])
                        elif widget_name == "cmd_entry" or widget_name == "output_text":
                            widget.configure(fg=self.colors["FG"])
                        elif widget_name == "os_info_label":
                            widget.configure(fg=self.colors["OS_INFO_FG"])
                        elif widget_name == "suggestion_box":
                            widget.configure(fg=self.colors["SUGGEST_FG"])
                        elif "btn" in widget_name and widget_name not in ["run_btn"]:
                            widget.configure(fg=self.colors["BUTTON_FG"])
                        elif widget_name == "run_btn":
                            widget.configure(fg=self.colors["RUN_FG"])
                        else:
                            widget.configure(fg=self.colors["FG"])
                            
                except tk.TclError:
                    # Widget might not support this property
                    pass
            
            # Update suggestion box selection colors
            try:
                self.suggestion_box.configure(
                    selectbackground=self.colors["SUGGEST_HL_BG"],
                    selectforeground=self.colors["SUGGEST_HL_FG"]
                )
            except:
                pass
            
            # Update hover bindings for run button
            self.run_btn.bind("<Enter>", lambda e: self.run_btn.config(bg=self.colors["RUN_HOVER"]))
            self.run_btn.bind("<Leave>", lambda e: self.run_btn.config(bg=self.colors["RUN_BG"]))
            
            # Update sidebar button hover bindings with proper colors
            for btn in self.sidebar_buttons:
                hover_color = self._lighten_color(self.colors["SIDEBAR_BTN_BG"])
                btn.bind("<Enter>", lambda e, button=btn, hc=hover_color: button.config(bg=hc, fg="#ffffff"))
                btn.bind("<Leave>", lambda e, button=btn: button.config(bg=self.colors["SIDEBAR_BTN_BG"], fg=self.colors["SIDEBAR_BTN_FG"]))
            
            # Refresh the display
            self.update_idletasks()
            
            self.insert_text("✅ Theme applied successfully! Button text should now be visible.", "success")
            
        except Exception as e:
            self.insert_text(f"❌ Error applying theme: {str(e)}", "error")
    
    def _update_safety_indicator(self, command: str):
        """Update the safety indicator based on command analysis"""
        try:
            if not command or not command.strip():
                # Safe - empty command
                self.safety_indicator.configure(text="✅", fg="#28a745")
                return
            
            is_dangerous, analysis = self.safety_checker.analyze_command(command)
            
            if not is_dangerous:
                # Safe command
                self.safety_indicator.configure(text="✅", fg="#28a745")
            else:
                # Dangerous command - update based on risk level
                risk_indicators = {
                    "low": {"icon": "⚠️", "color": "#ffc107"},
                    "medium": {"icon": "🚨", "color": "#fd7e14"},  
                    "high": {"icon": "🛑", "color": "#dc3545"},
                    "critical": {"icon": "💥", "color": "#dc3545"}
                }
                
                indicator = risk_indicators.get(analysis["risk_level"], risk_indicators["medium"])
                self.safety_indicator.configure(text=indicator["icon"], fg=indicator["color"])
                
                # Add tooltip-like functionality
                def show_warning_preview(event):
                    warnings = [w["description"] for w in analysis["warnings"]]
                    tooltip_text = f"Risk: {analysis['risk_level'].upper()}\n" + "\n".join(warnings[:3])
                    # This could be enhanced with an actual tooltip widget
                    
                self.safety_indicator.bind("<Enter>", show_warning_preview)
                
        except Exception:
            # Error in analysis - show warning
            self.safety_indicator.configure(text="❓", fg="#6c757d")


if __name__ == "__main__":
    app = ShellGUI()
    app.mainloop()
