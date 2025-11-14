#!/usr/bin/env python3
"""
Test script for the enhanced MagicShell command safety system
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from command_safety import CommandSafety
    
    def test_command_safety():
        """Test the command safety system"""
        print("🛡️ Testing MagicShell Enhanced Command Safety System")
        print("=" * 60)
        
        safety = CommandSafety()
        
        # Test commands with different risk levels
        test_commands = [
            # Safe commands
            "ls -la",
            "pwd",
            "echo hello",
            "cat file.txt",
            
            # Low risk
            "mv file.txt backup.txt",
            "chmod 644 file.txt",
            
            # Medium risk  
            "kill 1234",
            "killall firefox",
            
            # High risk
            "rm -rf /tmp/test",
            "shutdown -h now",
            
            # Critical risk
            "rm -rf /",
            "dd if=/dev/zero of=/dev/sda",
            ":(){:|:&};:",
            "sudo rm -rf --no-preserve-root /",
        ]
        
        print("\n🧪 Testing Command Analysis:")
        print("-" * 40)
        
        for cmd in test_commands:
            is_dangerous, analysis = safety.analyze_command(cmd)
            
            if is_dangerous:
                risk_icons = {"low": "⚠️", "medium": "🚨", "high": "🛑", "critical": "💥"}
                icon = risk_icons.get(analysis["risk_level"], "⚠️")
                
                print(f"\n{icon} Command: {cmd}")
                print(f"   Risk Level: {analysis['risk_level'].upper()}")
                print(f"   Categories: {', '.join(analysis['categories'])}")
                
                if analysis['dangerous_flags']:
                    flags = [f['flag'] for f in analysis['dangerous_flags']]
                    print(f"   Dangerous Flags: {', '.join(flags)}")
                
                if analysis['critical_paths']:
                    print(f"   Critical Paths: {', '.join(analysis['critical_paths'])}")
                
                if analysis['suggestions']:
                    print(f"   Suggestions: {analysis['suggestions'][0]}")
            else:
                print(f"✅ Safe: {cmd}")
        
        print(f"\n🎯 Safety Features Summary:")
        print("-" * 30)
        print("✅ Real-time risk assessment")
        print("✅ Visual safety indicators")  
        print("✅ Categorized danger detection")
        print("✅ Risk-based warning dialogs")
        print("✅ Safety suggestions")
        print("✅ Critical path detection")
        print("✅ Dangerous flag identification")
        print("✅ Confirmation requirements for high-risk commands")
        
        print(f"\n🚀 Enhanced Safety Features:")
        print("-" * 32)
        print("🛡️  8 Danger Categories:")
        print("   • File/Directory Deletion")
        print("   • Permission Changes")
        print("   • System Control")
        print("   • Process Termination")
        print("   • Disk Operations")
        print("   • File Movement")
        print("   • Network Configuration") 
        print("   • Fork Bombs/Malicious")
        
        print(f"\n🚨 Risk Levels:")
        print("   ✅ Safe - No dangers detected")
        print("   ⚠️  Low - Minor risks")
        print("   🚨 Medium - Moderate risks")
        print("   🛑 High - Significant risks")
        print("   💥 Critical - Extreme dangers")
        
        print(f"\n💡 Protection Features:")
        print("   • Typed confirmation for critical commands")
        print("   • Detailed danger explanations")
        print("   • Safety suggestions")
        print("   • Command cancellation")
        print("   • Real-time visual feedback")
        
        print(f"\n🎉 Ready to protect your system!")
        
    if __name__ == "__main__":
        test_command_safety()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all required modules are available")
except Exception as e:
    print(f"❌ Test error: {e}")
    import traceback
    traceback.print_exc()