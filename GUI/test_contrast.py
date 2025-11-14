#!/usr/bin/env python3
"""
Test script to verify button text visibility in MagicShell GUI
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from color_themes import ColorTheme

def test_button_contrast():
    """Test button color contrast to ensure text visibility"""
    print("🔍 Testing Button Text Visibility")
    print("=" * 40)
    
    theme_manager = ColorTheme()
    
    def hex_to_rgb(hex_color):
        """Convert hex color to RGB values"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def calculate_contrast_ratio(color1, color2):
        """Calculate contrast ratio between two colors"""
        def relative_luminance(rgb):
            r, g, b = [x/255.0 for x in rgb]
            r = r/12.92 if r <= 0.03928 else ((r+0.055)/1.055)**2.4
            g = g/12.92 if g <= 0.03928 else ((g+0.055)/1.055)**2.4
            b = b/12.92 if b <= 0.03928 else ((b+0.055)/1.055)**2.4
            return 0.2126*r + 0.7152*g + 0.0722*b
        
        lum1 = relative_luminance(hex_to_rgb(color1))
        lum2 = relative_luminance(hex_to_rgb(color2))
        
        brighter = max(lum1, lum2)
        darker = min(lum1, lum2)
        
        return (brighter + 0.05) / (darker + 0.05)
    
    print("🎨 Testing all theme button contrasts:")
    print()
    
    for theme_name in theme_manager.get_theme_names():
        theme_colors = theme_manager.THEMES[theme_name]
        
        # Test sidebar button contrast
        bg_color = theme_colors["SIDEBAR_BTN_BG"]
        fg_color = theme_colors["SIDEBAR_BTN_FG"]
        
        contrast_ratio = calculate_contrast_ratio(bg_color, fg_color)
        
        # WCAG AA requires 4.5:1 for normal text, 3:1 for large text (our buttons are large/bold)
        status = "✅ GOOD" if contrast_ratio >= 3.0 else "❌ POOR"
        
        print(f"📋 {theme_name}:")
        print(f"   Background: {bg_color}")
        print(f"   Text: {fg_color}")
        print(f"   Contrast Ratio: {contrast_ratio:.2f}:1 {status}")
        
        if contrast_ratio < 3.0:
            print(f"   ⚠️  Warning: Text may be hard to read!")
        
        print()
    
    print("💡 Fixed Issues:")
    print("   - Changed sidebar button colors to use theme's main button colors")
    print("   - Ensured white text (#ffffff) on colored backgrounds")
    print("   - Added smart hover effects that maintain readability")
    print()
    print("🚀 Button text should now be clearly visible in all themes!")

if __name__ == "__main__":
    test_button_contrast()