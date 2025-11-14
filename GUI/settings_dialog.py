# settings_dialog.py
"""
Settings dialog for MagicShell GUI with color customization
"""

import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
from color_themes import ColorTheme

class SettingsDialog:
    """Settings dialog with color theme customization"""
    
    def __init__(self, parent, theme_manager: ColorTheme, apply_callback=None):
        self.parent = parent
        self.theme_manager = theme_manager
        self.apply_callback = apply_callback
        self.preview_colors = self.theme_manager.get_current_theme()
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Settings - Color Themes")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        self._create_ui()
        
    def _create_ui(self):
        """Create the settings dialog UI"""
        # Main container
        main_frame = tk.Frame(self.dialog, bg="#2e2e2e", padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = tk.Label(main_frame, text="🎨 Color Theme Settings", 
                        font=("Helvetica", 16, "bold"), 
                        bg="#2e2e2e", fg="#ffffff")
        title.pack(pady=(0, 20))
        
        # Notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Predefined themes tab
        themes_frame = tk.Frame(notebook, bg="#2e2e2e")
        notebook.add(themes_frame, text="Predefined Themes")
        self._create_themes_tab(themes_frame)
        
        # Custom colors tab
        custom_frame = tk.Frame(notebook, bg="#2e2e2e")
        notebook.add(custom_frame, text="Custom Colors")
        self._create_custom_tab(custom_frame)
        
        # Preview tab
        preview_frame = tk.Frame(notebook, bg="#2e2e2e")
        notebook.add(preview_frame, text="Preview")
        self._create_preview_tab(preview_frame)
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg="#2e2e2e")
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # OK button (Apply and Close)
        tk.Button(button_frame, text="OK", command=self._ok_changes,
                 bg="#007bff", fg="white", font=("Helvetica", 11, "bold"),
                 padx=25, pady=5).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Apply button (Apply without closing)
        tk.Button(button_frame, text="Apply", command=self._apply_changes,
                 bg="#28a745", fg="white", font=("Helvetica", 11, "bold"),
                 padx=20, pady=5).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Cancel button
        tk.Button(button_frame, text="Cancel", command=self.dialog.destroy,
                 bg="#6c757d", fg="white", font=("Helvetica", 11, "bold"),
                 padx=20, pady=5).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Reset to Default button
        tk.Button(button_frame, text="Reset to Default", command=self._reset_to_default,
                 bg="#ffc107", fg="black", font=("Helvetica", 11, "bold"),
                 padx=20, pady=5).pack(side=tk.LEFT)
    
    def _create_themes_tab(self, parent):
        """Create predefined themes selection tab"""
        # Instructions
        info = tk.Label(parent, text="Choose from predefined color themes:",
                       bg="#2e2e2e", fg="#ffffff", font=("Helvetica", 12))
        info.pack(pady=(10, 15))
        
        # Live preview notice
        notice = tk.Label(parent, text="💡 Click 'Preview' to see changes instantly, 'OK' to apply and close",
                         bg="#2e2e2e", fg="#ffc107", font=("Helvetica", 10, "italic"))
        notice.pack(pady=(0, 10))
        
        # Theme selection frame
        themes_container = tk.Frame(parent, bg="#2e2e2e")
        themes_container.pack(fill=tk.BOTH, expand=True, padx=20)
        
        self.theme_var = tk.StringVar(value="Dark Blue")
        
        # Create theme preview cards
        themes = self.theme_manager.get_theme_names()
        for i, theme_name in enumerate(themes):
            row = i // 2
            col = i % 2
            
            # Theme card frame
            card_frame = tk.Frame(themes_container, bg="#3e3e3e", relief="raised", bd=2)
            card_frame.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
            
            # Theme name radio button
            radio = tk.Radiobutton(card_frame, text=theme_name, variable=self.theme_var,
                                  value=theme_name, bg="#3e3e3e", fg="#ffffff",
                                  font=("Helvetica", 11, "bold"), 
                                  command=lambda: self._on_theme_select_with_preview(theme_name))
            radio.pack(anchor="w", padx=10, pady=(10, 5))
            
            # Quick preview button for each theme
            preview_btn = tk.Button(card_frame, text="👁 Preview", 
                                  command=lambda t=theme_name: self._preview_theme(t),
                                  bg="#17a2b8", fg="white", font=("Helvetica", 8),
                                  padx=5, pady=2)
            preview_btn.pack(anchor="w", padx=10, pady=(0, 5))
            
            # Color preview strip
            color_strip = tk.Frame(card_frame, height=30)
            color_strip.pack(fill=tk.X, padx=10, pady=(0, 10))
            
            theme_colors = self.theme_manager.THEMES[theme_name]
            preview_colors = ["BG", "PANEL", "BUTTON_BG", "RUN_BG", "SIDEBAR_BG"]
            
            for j, color_key in enumerate(preview_colors):
                color_box = tk.Frame(color_strip, bg=theme_colors[color_key], width=50, height=30)
                color_box.pack(side=tk.LEFT, padx=2)
                color_box.pack_propagate(False)
        
        # Configure grid weights
        for i in range((len(themes) + 1) // 2):
            themes_container.grid_rowconfigure(i, weight=1)
        themes_container.grid_columnconfigure(0, weight=1)
        themes_container.grid_columnconfigure(1, weight=1)
    
    def _create_custom_tab(self, parent):
        """Create custom color configuration tab"""
        # Instructions
        info = tk.Label(parent, text="Customize individual colors:",
                       bg="#2e2e2e", fg="#ffffff", font=("Helvetica", 12))
        info.pack(pady=(10, 15))
        
        # Instructions for custom colors
        custom_info = tk.Label(parent, text="✨ Use 'Pick' for color chooser, 'Preview' for instant changes, or type hex codes",
                             bg="#2e2e2e", fg="#17a2b8", font=("Helvetica", 10, "italic"))
        custom_info.pack(pady=(0, 10))
        
        # Scrollable frame for color options
        canvas = tk.Canvas(parent, bg="#2e2e2e", highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#2e2e2e")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20)
        scrollbar.pack(side="right", fill="y")
        
        # Color configuration options
        self.color_vars = {}
        color_descriptions = {
            "BG": "Main Background",
            "PANEL": "Panel Background",
            "OUT_BG": "Output Background",
            "FG": "Text Color",
            "BUTTON_BG": "Button Background",
            "BUTTON_FG": "Button Text",
            "RUN_BG": "Run Button Background",
            "RUN_HOVER": "Run Button Hover",
            "RUN_FG": "Run Button Text",
            "SIDEBAR_BG": "Sidebar Background",
            "SIDEBAR_BTN_BG": "Sidebar Button Background",
            "SIDEBAR_BTN_FG": "Sidebar Button Text",
            "LOGO_ACCENT": "Logo Accent Color",
            "SUGGEST_BG": "Suggestion Background",
            "SUGGEST_FG": "Suggestion Text",
            "SUGGEST_HL_BG": "Suggestion Highlight Background",
            "SUGGEST_HL_FG": "Suggestion Highlight Text",
            "CWD_FG": "Directory Path Color",
            "OS_INFO_FG": "OS Info Color"
        }
        
        for i, (color_key, description) in enumerate(color_descriptions.items()):
            row_frame = tk.Frame(scrollable_frame, bg="#2e2e2e")
            row_frame.pack(fill=tk.X, pady=5, padx=10)
            
            # Color description
            desc_label = tk.Label(row_frame, text=description, bg="#2e2e2e", fg="#ffffff",
                                 font=("Helvetica", 10), width=25, anchor="w")
            desc_label.pack(side=tk.LEFT, padx=(0, 10))
            
            # Color preview
            current_color = self.preview_colors[color_key]
            self.color_vars[color_key] = tk.StringVar(value=current_color)
            
            color_preview = tk.Frame(row_frame, bg=current_color, width=40, height=25, 
                                   relief="solid", bd=1)
            color_preview.pack(side=tk.LEFT, padx=(0, 10))
            color_preview.pack_propagate(False)
            
            # Color value entry
            color_entry = tk.Entry(row_frame, textvariable=self.color_vars[color_key],
                                  font=("Consolas", 9), width=10)
            color_entry.pack(side=tk.LEFT, padx=(0, 10))
            
            # Color picker button
            pick_btn = tk.Button(row_frame, text="Pick", 
                               command=lambda k=color_key, p=color_preview: self._pick_color(k, p),
                               bg="#007bff", fg="white", font=("Helvetica", 9))
            pick_btn.pack(side=tk.LEFT)
            
            # Preview button to apply this color instantly
            preview_btn = tk.Button(row_frame, text="Preview", 
                                  command=lambda k=color_key: self._preview_single_color(k),
                                  bg="#17a2b8", fg="white", font=("Helvetica", 8))
            preview_btn.pack(side=tk.LEFT, padx=(5, 0))
            
            # Update preview when entry changes
            color_entry.bind("<KeyRelease>", lambda e, k=color_key, p=color_preview: self._update_color_preview(k, p))
            color_entry.bind("<FocusOut>", lambda e, k=color_key: self._preview_single_color(k))
    
    def _create_preview_tab(self, parent):
        """Create theme preview tab"""
        # Instructions
        info = tk.Label(parent, text="Preview of current theme selection:",
                       bg="#2e2e2e", fg="#ffffff", font=("Helvetica", 12))
        info.pack(pady=(10, 20))
        
        # Preview container
        self.preview_container = tk.Frame(parent, bg="#2e2e2e")
        self.preview_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self._update_preview()
    
    def _update_preview(self):
        """Update the theme preview"""
        # Clear existing preview
        for widget in self.preview_container.winfo_children():
            widget.destroy()
        
        # Mini GUI preview
        preview_bg = self.preview_colors["BG"]
        preview_frame = tk.Frame(self.preview_container, bg=preview_bg, relief="solid", bd=2)
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # Mini sidebar
        mini_sidebar = tk.Frame(preview_frame, bg=self.preview_colors["SIDEBAR_BG"], width=100)
        mini_sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        mini_sidebar.pack_propagate(False)
        
        tk.Label(mini_sidebar, text="🌀 MAGIC", bg=self.preview_colors["SIDEBAR_BG"],
                fg=self.preview_colors["LOGO_ACCENT"], font=("Helvetica", 8, "bold")).pack(pady=5)
        
        mini_btn = tk.Label(mini_sidebar, text="Settings", bg=self.preview_colors["SIDEBAR_BTN_BG"],
                           fg=self.preview_colors["SIDEBAR_BTN_FG"], font=("Helvetica", 7),
                           padx=10, pady=2)
        mini_btn.pack(fill=tk.X, padx=3, pady=2)
        
        # Mini main area
        mini_main = tk.Frame(preview_frame, bg=preview_bg)
        mini_main.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Mini command area
        cmd_frame = tk.Frame(mini_main, bg=preview_bg)
        cmd_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(cmd_frame, text="CWD:", bg=preview_bg, fg=self.preview_colors["FG"],
                font=("Helvetica", 8)).pack(side=tk.LEFT)
        
        mini_entry = tk.Frame(cmd_frame, bg=self.preview_colors["PANEL"], height=20)
        mini_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        mini_entry.pack_propagate(False)
        
        mini_run = tk.Label(cmd_frame, text="Run", bg=self.preview_colors["RUN_BG"],
                           fg=self.preview_colors["RUN_FG"], font=("Helvetica", 7, "bold"),
                           padx=8, pady=2)
        mini_run.pack(side=tk.LEFT)
        
        # Mini output area
        mini_output = tk.Frame(mini_main, bg=self.preview_colors["OUT_BG"], height=100, relief="solid", bd=1)
        mini_output.pack(fill=tk.BOTH, expand=True, pady=5)
        mini_output.pack_propagate(False)
        
        tk.Label(mini_output, text="> ls -la", bg=self.preview_colors["OUT_BG"],
                fg="#7fff7f", font=("Consolas", 8), anchor="w").pack(fill=tk.X, padx=5, pady=2)
        tk.Label(mini_output, text="drwxr-xr-x user group 4096 Oct 11 file.py", 
                bg=self.preview_colors["OUT_BG"], fg=self.preview_colors["FG"],
                font=("Consolas", 7), anchor="w").pack(fill=tk.X, padx=5)
    
    def _on_theme_select(self):
        """Handle predefined theme selection"""
        selected_theme = self.theme_var.get()
        self.preview_colors = self.theme_manager.THEMES[selected_theme].copy()
        
        # Update custom color variables
        for color_key, color_value in self.preview_colors.items():
            if color_key in self.color_vars:
                self.color_vars[color_key].set(color_value)
        
        self._update_preview()
        self._update_all_color_previews()
    
    def _on_theme_select_with_preview(self, theme_name):
        """Handle theme selection with instant preview"""
        self.theme_var.set(theme_name)
        self._on_theme_select()
        self._preview_theme(theme_name)
    
    def _preview_theme(self, theme_name):
        """Preview a theme instantly in the main GUI"""
        try:
            if theme_name in self.theme_manager.THEMES:
                # Temporarily apply the theme
                temp_colors = self.theme_manager.THEMES[theme_name].copy()
                self.theme_manager.set_custom_theme(temp_colors)
                
                # Apply to main GUI
                if self.apply_callback:
                    self.apply_callback()
                
                # Update dialog preview
                self.preview_colors = temp_colors.copy()
                self._update_preview()
                
        except Exception as e:
            pass  # Ignore preview errors
    
    def _pick_color(self, color_key, preview_frame):
        """Open color picker for specific color"""
        current_color = self.color_vars[color_key].get()
        color = colorchooser.askcolor(color=current_color, title=f"Choose {color_key} Color")
        
        if color[1]:  # If user didn't cancel
            self.color_vars[color_key].set(color[1])
            self.preview_colors[color_key] = color[1]
            preview_frame.configure(bg=color[1])
            self._update_preview()
    
    def _update_color_preview(self, color_key, preview_frame):
        """Update color preview when entry changes"""
        try:
            color_value = self.color_vars[color_key].get()
            if color_value.startswith('#') and len(color_value) == 7:
                preview_frame.configure(bg=color_value)
                self.preview_colors[color_key] = color_value
                self._update_preview()
        except tk.TclError:
            pass  # Invalid color format
    
    def _update_all_color_previews(self):
        """Update all color preview boxes in custom tab"""
        # This would update all color preview frames - implementation depends on storing references
        pass
    
    def _apply_changes(self):
        """Apply the selected theme without closing dialog"""
        try:
            # Set the custom theme (which includes any modifications)
            self.theme_manager.set_custom_theme(self.preview_colors)
            
            # Call the callback to refresh the main GUI
            if self.apply_callback:
                self.apply_callback()
            
            # Show success message in the dialog title temporarily
            original_title = self.dialog.title()
            self.dialog.title("✅ Theme Applied Successfully!")
            self.dialog.after(2000, lambda: self.dialog.title(original_title))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply theme: {str(e)}")
    
    def _ok_changes(self):
        """Apply the selected theme and close dialog"""
        try:
            # Set the custom theme (which includes any modifications)
            self.theme_manager.set_custom_theme(self.preview_colors)
            
            # Call the callback to refresh the main GUI
            if self.apply_callback:
                self.apply_callback()
            
            # Close the dialog
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply theme: {str(e)}")
    
    def _preview_single_color(self, color_key):
        """Preview a single color change instantly"""
        try:
            color_value = self.color_vars[color_key].get().strip()
            if color_value.startswith('#') and len(color_value) == 7:
                # Update preview colors
                self.preview_colors[color_key] = color_value
                
                # Update the mini preview
                self._update_preview()
                
                # Temporarily apply to main GUI if callback exists
                if self.apply_callback:
                    temp_theme = self.preview_colors.copy()
                    self.theme_manager.set_custom_theme(temp_theme)
                    self.apply_callback()
                    
        except Exception as e:
            pass  # Ignore invalid colors during typing
    
    def _reset_to_default(self):
        """Reset to default theme"""
        if messagebox.askyesno("Confirm Reset", "Reset to default Dark Blue theme?"):
            self.theme_var.set("Dark Blue")
            self._on_theme_select()