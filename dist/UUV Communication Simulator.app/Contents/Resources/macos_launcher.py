#!/usr/bin/env python3
"""
macOS Launcher for UUV Communication Simulator
Handles macOS-specific tkinter compatibility issues
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox
import platform

def setup_macos_environment():
    """Setup macOS-specific environment variables and settings"""
    # Disable problematic macOS features that can cause crashes
    os.environ['TK_SILENCE_DEPRECATION'] = '1'
    
    # Set up proper display handling
    if 'DISPLAY' not in os.environ:
        os.environ['DISPLAY'] = ':0'
    
    # Prevent automatic macOS app menu creation that causes crashes
    if platform.system() == "Darwin":
        os.environ['PYTHONPATH'] = os.getcwd()

def test_tkinter_compatibility():
    """Test if tkinter can create a basic window without crashing"""
    try:
        # Create a minimal test window
        test_root = tk.Tk()
        test_root.withdraw()  # Hide immediately
        test_root.title("Test")
        test_root.geometry("100x100")
        
        # Test basic operations that might cause crashes
        test_frame = tk.Frame(test_root)
        test_label = tk.Label(test_frame, text="Test")
        
        # Clean up
        test_root.destroy()
        return True
        
    except Exception as e:
        print(f"Tkinter compatibility test failed: {e}")
        return False

def launch_simulator():
    """Launch the UUV Communication Simulator with error handling"""
    try:
        # Import and launch the main application
        from simulation_gui import UUVSimulationGUI
        
        print("🌊 Starting UUV Communication Simulator...")
        app = UUVSimulationGUI()
        app.run()
        
    except ImportError as e:
        error_msg = f"Failed to import simulation modules: {e}"
        print(f"ERROR: {error_msg}")
        
        # Try to show error dialog if tkinter works
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Import Error", 
                               f"Failed to start UUV Simulator:\n\n{error_msg}\n\n"
                               f"Please ensure all dependencies are installed.")
            root.destroy()
        except:
            pass  # If tkinter also fails, just print error
            
    except Exception as e:
        error_msg = f"Unexpected error during startup: {e}"
        print(f"ERROR: {error_msg}")
        
        # Try to show error dialog
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Startup Error", 
                               f"UUV Simulator encountered an error:\n\n{error_msg}")
            root.destroy()
        except:
            pass

def main():
    """Main launcher function"""
    print("🚀 UUV Communication Simulator - macOS Launcher")
    print("=" * 50)
    
    # Setup macOS environment
    print("⚙️  Setting up macOS environment...")
    setup_macos_environment()
    
    # Test tkinter compatibility
    print("🧪 Testing tkinter compatibility...")
    if not test_tkinter_compatibility():
        print("❌ Tkinter compatibility test failed!")
        print("   This may indicate a problem with your Python/tkinter installation.")
        print("   Try running from terminal: python3 simulation_gui.py")
        sys.exit(1)
    
    print("✅ Tkinter compatibility test passed!")
    
    # Launch the simulator
    print("🌊 Launching UUV Communication Simulator...")
    launch_simulator()
    
    print("👋 UUV Communication Simulator closed.")

if __name__ == "__main__":
    main() 