#!/usr/bin/env python3
"""
Test script for MagicShell color theme functionality
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from color_themes import ColorTheme

def test_color_themes():
    """Test the color theme functionality"""
    print("🎨 Testing MagicShell Color Theme System")
    print("=" * 50)
    
    # Initialize theme manager
    theme_manager = ColorTheme()
    
    print(f"✅ Theme manager initialized")
    print(f"📁 Config directory: {theme_manager.config_dir}")
    print(f"📄 Config file: {theme_manager.config_file}")
    
    # Test available themes
    themes = theme_manager.get_theme_names()
    print(f"\n🎨 Available themes ({len(themes)}):")
    for i, theme_name in enumerate(themes, 1):
        print(f"   {i}. {theme_name}")
    
    # Test current theme
    current_theme = theme_manager.get_current_theme()
    print(f"\n🎯 Current theme colors:")
    for color_key, color_value in current_theme.items():
        print(f"   {color_key}: {color_value}")
    
    # Test theme switching
    print(f"\n🔄 Testing theme switching...")
    for theme_name in ["Purple Night", "Ocean Blue", "Light Mode"]:
        success = theme_manager.set_theme(theme_name)
        if success:
            print(f"   ✅ Successfully switched to '{theme_name}'")
            # Show a few sample colors
            bg_color = theme_manager.get_color("BG")
            fg_color = theme_manager.get_color("FG")
            button_color = theme_manager.get_color("BUTTON_BG")
            print(f"      Background: {bg_color}, Text: {fg_color}, Button: {button_color}")
        else:
            print(f"   ❌ Failed to switch to '{theme_name}'")
    
    # Test custom color update
    print(f"\n🎨 Testing custom color update...")
    original_bg = theme_manager.get_color("BG")
    success = theme_manager.update_color("BG", "#123456")
    if success:
        new_bg = theme_manager.get_color("BG")
        print(f"   Updated BG color from {original_bg} to {new_bg}")
        
        # Restore original
        theme_manager.update_color("BG", original_bg)
        print(f"    Restored BG color to {original_bg}")
    else:
        print(f"   ❌ Failed to update BG color")
    
    # Test save/load functionality
    print(f"\n💾 Testing save/load functionality...")
    save_success = theme_manager.save_theme()
    if save_success:
        print(f"    Theme saved successfully")
        
        # Create new instance to test loading
        new_theme_manager = ColorTheme()
        loaded_theme = new_theme_manager.get_current_theme()
        
        if loaded_theme == current_theme:
            print(f"   ✅ Theme loaded correctly")
        else:
            print(f"   ⚠️  Loaded theme differs from saved theme")
    else:
        print(f"   ❌ Failed to save theme")
    
    print(f"\n✨ Color theme system test completed!")
    print(f"🚀 You can now use the Settings button in the GUI to customize colors!")

if __name__ == "__main__":
    test_color_themes()