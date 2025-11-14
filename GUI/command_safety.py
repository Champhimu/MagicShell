"""
Command Safety Module for MagicShell
Provides comprehensive warnings and safety checks for dangerous commands
"""

import re
import tkinter as tk
from tkinter import messagebox
from typing import Tuple, List, Dict

class CommandSafety:
    """Handles dangerous command detection and warnings"""
    
    # Categorized dangerous commands with specific warnings
    DANGEROUS_COMMANDS = {
        "destructive_file_ops": {
            "commands": ["rm", "rmdir", "del", "erase", "shred", "wipe"],
            "description": "File/Directory Deletion",
            "warning": "This command will permanently DELETE files or directories!",
            "icon": "🗑️",
            "color": "#dc3545"
        },
        "permission_changes": {
            "commands": ["chmod", "chown", "chgrp", "icacls", "takeown"],
            "description": "Permission Changes",
            "warning": "This command will change file/directory permissions or ownership!",
            "icon": "🔒",
            "color": "#fd7e14"
        },
        "system_control": {
            "commands": ["shutdown", "reboot", "restart", "halt", "poweroff", "init"],
            "description": "System Control",
            "warning": "This command will affect system power state or restart!",
            "icon": "⚡",
            "color": "#dc3545"
        },
        "process_control": {
            "commands": ["kill", "killall", "pkill", "taskkill"],
            "description": "Process Termination",
            "warning": "This command will terminate running processes!",
            "icon": "💀",
            "color": "#6f42c1"
        },
        "disk_operations": {
            "commands": ["dd", "fdisk", "mkfs", "format", "diskpart"],
            "description": "Disk Operations",
            "warning": "This command can destroy disk data or partitions!",
            "icon": "💽",
            "color": "#dc3545"
        },
        "file_movement": {
            "commands": ["mv", "move", "cut"],
            "description": "File Movement",
            "warning": "This command will move/rename files (potential data loss)!",
            "icon": "📦",
            "color": "#ffc107"
        },
        "network_changes": {
            "commands": ["iptables", "netsh", "ifconfig", "ip"],
            "description": "Network Configuration",
            "warning": "This command will change network settings!",
            "icon": "🌐",
            "color": "#17a2b8"
        },
        "shell_bombs": {
            "commands": [":(){:|:&};:", ":(){ :|:& };:", "fork()", ".bat"],
            "description": "Fork Bombs/Malicious",
            "warning": "This appears to be a FORK BOMB or malicious script!",
            "icon": "💣",
            "color": "#dc3545"
        }
    }
    
    # Dangerous flags and options
    DANGEROUS_FLAGS = {
        "-r": "Recursive operation",
        "-R": "Recursive operation",
        "-f": "Force operation (bypass confirmations)",
        "--force": "Force operation (bypass confirmations)",
        "-rf": "Recursive force deletion",
        "-Rf": "Recursive force deletion",
        "--recursive": "Recursive operation",
        "--no-preserve-root": "Allows deletion of root directory",
        "/S": "Recursive (Windows)",
        "/Q": "Quiet mode (Windows)",
        "/F": "Force (Windows)",
        "*": "Wildcard - affects multiple files",
        "*.": "Dangerous wildcard pattern"
    }
    
    # Paths that should trigger extra warnings
    CRITICAL_PATHS = [
        "/", "C:\\", "D:\\",  # Root directories
        "/etc", "/usr", "/var", "/bin", "/sbin", "/lib",  # System directories
        "/home", "/Users",  # User directories
        "~", "$HOME",  # Home directory
        "C:\\Windows", "C:\\Program Files", "C:\\Users"  # Windows system dirs
    ]
    
    def __init__(self, parent_window=None):
        self.parent = parent_window
    
    def analyze_command(self, command: str) -> Tuple[bool, Dict]:
        """
        Analyze a command for potential dangers
        Returns: (is_dangerous, analysis_result)
        """
        if not command or not command.strip():
            return False, {}
            
        cmd_lower = command.lower().strip()
        cmd_parts = command.split()
        
        analysis = {
            "is_dangerous": False,
            "risk_level": "low",  # low, medium, high, critical
            "categories": [],
            "warnings": [],
            "dangerous_flags": [],
            "critical_paths": [],
            "command": command,
            "suggestions": []
        }
        
        # Check for dangerous command categories
        for category, info in self.DANGEROUS_COMMANDS.items():
            for dangerous_cmd in info["commands"]:
                if self._command_matches(cmd_lower, dangerous_cmd):
                    analysis["is_dangerous"] = True
                    analysis["categories"].append(category)
                    analysis["warnings"].append({
                        "category": category,
                        "description": info["description"],
                        "warning": info["warning"],
                        "icon": info["icon"],
                        "color": info["color"]
                    })
        
        # Check for dangerous flags
        for flag, description in self.DANGEROUS_FLAGS.items():
            if flag.lower() in cmd_lower:
                analysis["dangerous_flags"].append({
                    "flag": flag,
                    "description": description
                })
                if flag in ["-rf", "-Rf", "--no-preserve-root"]:
                    analysis["risk_level"] = "critical"
                else:
                    analysis["risk_level"] = "high" if analysis["risk_level"] != "critical" else "critical"
        
        # Check for critical paths
        for path in self.CRITICAL_PATHS:
            if path in command:
                analysis["critical_paths"].append(path)
                analysis["risk_level"] = "critical"
        
        # Set overall risk level
        if analysis["is_dangerous"]:
            if analysis["risk_level"] == "low":
                # Check categories for risk level
                critical_categories = ["destructive_file_ops", "disk_operations", "shell_bombs"]
                high_categories = ["system_control", "process_control"]
                
                for category in analysis["categories"]:
                    if category in critical_categories:
                        analysis["risk_level"] = "critical"
                        break
                    elif category in high_categories:
                        analysis["risk_level"] = "high"
                    else:
                        analysis["risk_level"] = "medium"
        
        # Add safety suggestions
        analysis["suggestions"] = self._get_safety_suggestions(analysis)
        
        return analysis["is_dangerous"], analysis
    
    def _command_matches(self, cmd_lower: str, dangerous_cmd: str) -> bool:
        """Check if command matches dangerous pattern"""
        # Exact match at start
        if cmd_lower.startswith(dangerous_cmd.lower()):
            return True
        # Match as standalone command
        if f" {dangerous_cmd.lower()} " in f" {cmd_lower} ":
            return True
        # Match with common prefixes
        prefixes = ["sudo ", "doas ", "su -c ", "runas "]
        for prefix in prefixes:
            if cmd_lower.startswith(prefix) and dangerous_cmd.lower() in cmd_lower[len(prefix):]:
                return True
        return False
    
    def _get_safety_suggestions(self, analysis: Dict) -> List[str]:
        """Generate safety suggestions based on analysis"""
        suggestions = []
        
        if "destructive_file_ops" in analysis["categories"]:
            suggestions.extend([
                "Consider using 'ls' to list files first",
                "Use '-i' flag for interactive confirmation",
                "Create a backup before deletion",
                "Use trash/recycle bin instead of permanent deletion"
            ])
        
        if "permission_changes" in analysis["categories"]:
            suggestions.extend([
                "Verify current permissions with 'ls -l'",
                "Use specific numeric permissions instead of wildcards",
                "Test on a single file first"
            ])
        
        if "system_control" in analysis["categories"]:
            suggestions.extend([
                "Save your work before proceeding",
                "Ensure no critical processes are running",
                "Consider using 'systemctl' for service management"
            ])
        
        if analysis["dangerous_flags"]:
            suggestions.append("Remove force (-f) flags to enable safety prompts")
        
        if analysis["critical_paths"]:
            suggestions.append("Double-check the target path - this affects system directories")
        
        return suggestions
    
    def show_warning_dialog(self, analysis: Dict) -> bool:
        """
        Show comprehensive warning dialog
        Returns: True if user confirms, False if cancelled
        """
        if not analysis["is_dangerous"]:
            return True
            
        # Create custom warning dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("⚠️ Dangerous Command Warning")
        dialog.geometry("550x600")
        dialog.transient(self.parent)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (550 // 2)
        y = (dialog.winfo_screenheight() // 2) - (600 // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Color scheme based on risk level
        risk_colors = {
            "low": {"bg": "#fff3cd", "fg": "#856404", "accent": "#ffc107"},
            "medium": {"bg": "#f8d7da", "fg": "#721c24", "accent": "#fd7e14"},
            "high": {"bg": "#f5c6cb", "fg": "#721c24", "accent": "#dc3545"},
            "critical": {"bg": "#f1c0c7", "fg": "#721c24", "accent": "#dc3545"}
        }
        
        colors = risk_colors.get(analysis["risk_level"], risk_colors["medium"])
        dialog.configure(bg=colors["bg"])
        
        result = {"confirmed": False}
        
        # Title and icon
        title_frame = tk.Frame(dialog, bg=colors["bg"], pady=20)
        title_frame.pack(fill=tk.X)
        
        risk_icons = {"low": "⚠️", "medium": "🚨", "high": "🛑", "critical": "💥"}
        icon = risk_icons.get(analysis["risk_level"], "⚠️")
        
        tk.Label(title_frame, text=f"{icon} DANGEROUS COMMAND WARNING", 
                font=("Helvetica", 16, "bold"), bg=colors["bg"], fg=colors["accent"]).pack()
        
        tk.Label(title_frame, text=f"Risk Level: {analysis['risk_level'].upper()}", 
                font=("Helvetica", 12, "bold"), bg=colors["bg"], fg=colors["fg"]).pack()
        
        # Command display
        cmd_frame = tk.Frame(dialog, bg=colors["bg"], pady=10)
        cmd_frame.pack(fill=tk.X, padx=20)
        
        tk.Label(cmd_frame, text="Command:", font=("Helvetica", 11, "bold"), 
                bg=colors["bg"], fg=colors["fg"]).pack(anchor="w")
        
        cmd_text = tk.Text(cmd_frame, height=2, width=60, font=("Consolas", 10), 
                          bg="#2e2e2e", fg="#ffffff", relief="solid", bd=1)
        cmd_text.pack(fill=tk.X, pady=5)
        cmd_text.insert("1.0", analysis["command"])
        cmd_text.configure(state="disabled")
        
        # Warnings
        if analysis["warnings"]:
            warn_frame = tk.Frame(dialog, bg=colors["bg"], pady=10)
            warn_frame.pack(fill=tk.BOTH, expand=True, padx=20)
            
            tk.Label(warn_frame, text="⚠️ Detected Dangers:", font=("Helvetica", 11, "bold"), 
                    bg=colors["bg"], fg=colors["fg"]).pack(anchor="w")
            
            for warning in analysis["warnings"]:
                w_frame = tk.Frame(warn_frame, bg=colors["bg"])
                w_frame.pack(fill=tk.X, pady=2)
                
                tk.Label(w_frame, text=f"{warning['icon']} {warning['description']}: {warning['warning']}", 
                        font=("Helvetica", 10), bg=colors["bg"], fg=colors["fg"], 
                        wraplength=500, justify="left").pack(anchor="w")
        
        # Dangerous flags
        if analysis["dangerous_flags"]:
            flag_frame = tk.Frame(dialog, bg=colors["bg"], pady=5)
            flag_frame.pack(fill=tk.X, padx=20)
            
            tk.Label(flag_frame, text="🚩 Dangerous Flags/Options:", font=("Helvetica", 11, "bold"), 
                    bg=colors["bg"], fg=colors["fg"]).pack(anchor="w")
            
            for flag_info in analysis["dangerous_flags"]:
                tk.Label(flag_frame, text=f"  • {flag_info['flag']}: {flag_info['description']}", 
                        font=("Helvetica", 10), bg=colors["bg"], fg=colors["fg"]).pack(anchor="w")
        
        # Critical paths
        if analysis["critical_paths"]:
            path_frame = tk.Frame(dialog, bg=colors["bg"], pady=5)
            path_frame.pack(fill=tk.X, padx=20)
            
            tk.Label(path_frame, text="📂 Critical Paths Detected:", font=("Helvetica", 11, "bold"), 
                    bg=colors["bg"], fg=colors["fg"]).pack(anchor="w")
            
            for path in analysis["critical_paths"]:
                tk.Label(path_frame, text=f"  • {path}", font=("Consolas", 10), 
                        bg=colors["bg"], fg=colors["accent"]).pack(anchor="w")
        
        # Safety suggestions
        if analysis["suggestions"]:
            sug_frame = tk.Frame(dialog, bg=colors["bg"], pady=10)
            sug_frame.pack(fill=tk.X, padx=20)
            
            tk.Label(sug_frame, text="💡 Safety Suggestions:", font=("Helvetica", 11, "bold"), 
                    bg=colors["bg"], fg=colors["fg"]).pack(anchor="w")
            
            for suggestion in analysis["suggestions"][:4]:  # Show max 4 suggestions
                tk.Label(sug_frame, text=f"  • {suggestion}", font=("Helvetica", 9), 
                        bg=colors["bg"], fg=colors["fg"], wraplength=500, justify="left").pack(anchor="w")
        
        # Buttons
        btn_frame = tk.Frame(dialog, bg=colors["bg"], pady=20)
        btn_frame.pack(fill=tk.X, padx=20)
        
        def on_cancel():
            result["confirmed"] = False
            dialog.destroy()
        
        def on_confirm():
            result["confirmed"] = True
            dialog.destroy()
        
        # High-risk commands require typing confirmation
        if analysis["risk_level"] in ["high", "critical"]:
            tk.Label(btn_frame, text="⚠️ Type 'YES I UNDERSTAND' to confirm:", 
                    font=("Helvetica", 10, "bold"), bg=colors["bg"], fg=colors["accent"]).pack()
            
            confirm_entry = tk.Entry(btn_frame, font=("Helvetica", 10), width=30)
            confirm_entry.pack(pady=5)
            confirm_entry.focus_set()
            
            def check_confirmation():
                if confirm_entry.get().strip().upper() == "YES I UNDERSTAND":
                    on_confirm()
                else:
                    tk.Label(btn_frame, text="❌ Incorrect confirmation text", 
                            font=("Helvetica", 9), bg=colors["bg"], fg="#dc3545").pack()
            
            tk.Button(btn_frame, text="Execute Command", command=check_confirmation,
                     bg="#dc3545", fg="white", font=("Helvetica", 10, "bold"), pady=5).pack(side=tk.RIGHT, padx=5)
        else:
            tk.Button(btn_frame, text="Execute Command", command=on_confirm,
                     bg=colors["accent"], fg="white", font=("Helvetica", 10, "bold"), pady=5).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(btn_frame, text="Cancel", command=on_cancel,
                 bg="#6c757d", fg="white", font=("Helvetica", 10, "bold"), pady=5).pack(side=tk.RIGHT, padx=5)
        
        # Wait for dialog result
        dialog.wait_window()
        return result["confirmed"]