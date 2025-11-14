# color_themes.py
"""
Color theme management system for MagicShell GUI
Provides predefined themes and custom color configuration
"""

import json
import os
from typing import Dict, Any

class ColorTheme:
    """Manages color themes for the GUI"""
    
    # Default color schemes
    THEMES = {
        "Dark Blue": {
            "BG": "#0d0d0d",
            "PANEL": "#1e1e1e",
            "OUT_BG": "#0b0b0b",
            "FG": "#ffffff",
            "BUTTON_BG": "#007bff",
            "BUTTON_FG": "#ffffff",
            "RUN_BG": "#d9534f",
            "RUN_HOVER": "#c9302c",
            "RUN_FG": "#ffffff",
            "SIDEBAR_BG": "#121212",
            "SIDEBAR_BTN_BG": "#007bff",
            "SIDEBAR_BTN_FG": "#ffffff",
            "LOGO_ACCENT": "#00ffcc",
            "SUGGEST_BG": "#1a1a1a",
            "SUGGEST_FG": "#00ff80",
            "SUGGEST_HL_BG": "#333333",
            "SUGGEST_HL_FG": "#ffffff",
            "CWD_FG": "#00ffff",
            "OS_INFO_FG": "#00ff80",
        },
        
        "Dark Green": {
            "BG": "#0a1a0a",
            "PANEL": "#1a2e1a",
            "OUT_BG": "#0b1b0b",
            "FG": "#e0ffe0",
            "BUTTON_BG": "#228B22",
            "BUTTON_FG": "#ffffff",
            "RUN_BG": "#dc3545",
            "RUN_HOVER": "#c82333",
            "RUN_FG": "#ffffff",
            "SIDEBAR_BG": "#0d1f0d",
            "SIDEBAR_BTN_BG": "#228B22",
            "SIDEBAR_BTN_FG": "#ffffff",
            "LOGO_ACCENT": "#00ff66",
            "SUGGEST_BG": "#1a2e1a",
            "SUGGEST_FG": "#90ee90",
            "SUGGEST_HL_BG": "#2e4a2e",
            "SUGGEST_HL_FG": "#ffffff",
            "CWD_FG": "#90ee90",
            "OS_INFO_FG": "#98fb98",
        },
        
        "Purple Night": {
            "BG": "#1a0a1a",
            "PANEL": "#2e1a2e",
            "OUT_BG": "#1b0b1b",
            "FG": "#f0e0ff",
            "BUTTON_BG": "#8a2be2",
            "BUTTON_FG": "#ffffff",
            "RUN_BG": "#ff4500",
            "RUN_HOVER": "#ff6347",
            "RUN_FG": "#ffffff",
            "SIDEBAR_BG": "#1f0d1f",
            "SIDEBAR_BTN_BG": "#8a2be2",
            "SIDEBAR_BTN_FG": "#ffffff",
            "LOGO_ACCENT": "#da70d6",
            "SUGGEST_BG": "#2e1a2e",
            "SUGGEST_FG": "#dda0dd",
            "SUGGEST_HL_BG": "#4a2e4a",
            "SUGGEST_HL_FG": "#ffffff",
            "CWD_FG": "#dda0dd",
            "OS_INFO_FG": "#ee82ee",
        },
        
        "Ocean Blue": {
            "BG": "#0a1a2e",
            "PANEL": "#1a2e42",
            "OUT_BG": "#0b1b2f",
            "FG": "#e0f0ff",
            "BUTTON_BG": "#4682b4",
            "BUTTON_FG": "#ffffff",
            "RUN_BG": "#ff6b35",
            "RUN_HOVER": "#ff8c42",
            "RUN_FG": "#ffffff",
            "SIDEBAR_BG": "#0d1f33",
            "SIDEBAR_BTN_BG": "#5f9ea0",
            "SIDEBAR_BTN_FG": "#ffffff",
            "LOGO_ACCENT": "#00bfff",
            "SUGGEST_BG": "#1a2e42",
            "SUGGEST_FG": "#87ceeb",
            "SUGGEST_HL_BG": "#2e4a66",
            "SUGGEST_HL_FG": "#ffffff",
            "CWD_FG": "#87ceeb",
            "OS_INFO_FG": "#87cefa",
        },
        
        "Sunset Orange": {
            "BG": "#2e1a0a",
            "PANEL": "#42301a",
            "OUT_BG": "#2f1b0b",
            "FG": "#ffe0c0",
            "BUTTON_BG": "#ff8c00",
            "BUTTON_FG": "#ffffff",
            "RUN_BG": "#dc143c",
            "RUN_HOVER": "#b91c3c",
            "RUN_FG": "#ffffff",
            "SIDEBAR_BG": "#331f0d",
            "SIDEBAR_BTN_BG": "#cc7000",
            "SIDEBAR_BTN_FG": "#ffffff",
            "LOGO_ACCENT": "#ffd700",
            "SUGGEST_BG": "#42301a",
            "SUGGEST_FG": "#ffa500",
            "SUGGEST_HL_BG": "#664a2e",
            "SUGGEST_HL_FG": "#ffffff",
            "CWD_FG": "#ffa500",
            "OS_INFO_FG": "#ffb347",
        },
        
        "Light Mode": {
            "BG": "#f8f9fa",
            "PANEL": "#ffffff",
            "OUT_BG": "#ffffff",
            "FG": "#212529",
            "BUTTON_BG": "#007bff",
            "BUTTON_FG": "#ffffff",
            "RUN_BG": "#dc3545",
            "RUN_HOVER": "#c82333",
            "RUN_FG": "#ffffff",
            "SIDEBAR_BG": "#e9ecef",
            "SIDEBAR_BTN_BG": "#6c757d",
            "SIDEBAR_BTN_FG": "#ffffff",
            "LOGO_ACCENT": "#28a745",
            "SUGGEST_BG": "#ffffff",
            "SUGGEST_FG": "#495057",
            "SUGGEST_HL_BG": "#e9ecef",
            "SUGGEST_HL_FG": "#212529",
            "CWD_FG": "#007bff",
            "OS_INFO_FG": "#28a745",
        }
    }
    
    def __init__(self, config_dir: str = None):
        """Initialize color theme manager"""
        if config_dir is None:
            config_dir = os.path.expanduser("~/.magicshell")
        
        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, "theme_config.json")
        
        # Ensure config directory exists
        os.makedirs(config_dir, exist_ok=True)
        
        # Load current theme
        self.current_theme = self.load_theme()
    
    def get_theme_names(self) -> list:
        """Get list of available theme names"""
        return list(self.THEMES.keys())
    
    def get_current_theme(self) -> Dict[str, str]:
        """Get current active theme colors"""
        return self.current_theme.copy()
    
    def set_theme(self, theme_name: str) -> bool:
        """Set theme by name"""
        if theme_name in self.THEMES:
            self.current_theme = self.THEMES[theme_name].copy()
            self.save_theme()
            return True
        return False
    
    def set_custom_theme(self, colors: Dict[str, str]) -> bool:
        """Set custom theme colors"""
        try:
            # Validate that all required colors are provided
            required_colors = set(self.THEMES["Dark Blue"].keys())
            provided_colors = set(colors.keys())
            
            if not required_colors.issubset(provided_colors):
                return False
            
            self.current_theme = colors.copy()
            self.save_theme()
            return True
        except Exception:
            return False
    
    def load_theme(self) -> Dict[str, str]:
        """Load theme from config file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('theme', self.THEMES["Dark Blue"])
            else:
                return self.THEMES["Dark Blue"].copy()
        except Exception:
            return self.THEMES["Dark Blue"].copy()
    
    def save_theme(self) -> bool:
        """Save current theme to config file"""
        try:
            config = {
                'theme': self.current_theme,
                'last_updated': __import__('time').time()
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception:
            return False
    
    def get_color(self, color_key: str) -> str:
        """Get specific color value"""
        return self.current_theme.get(color_key, "#ffffff")
    
    def update_color(self, color_key: str, color_value: str) -> bool:
        """Update a specific color in current theme"""
        if color_key in self.current_theme:
            self.current_theme[color_key] = color_value
            self.save_theme()
            return True
        return False
