#!/usr/bin/env python3
"""
🚀 UUV Simulation GUI Launcher 🚀

Quick launcher for the underwater communication simulation GUI
"""

import sys
import tkinter as tk
from tkinter import messagebox

def check_requirements():
    """Check if all requirements are available"""
    try:
        import tkinter
        from models.acoustic_config import DEFAULT_CONFIG
        from complex_simulation import run_complex_simulation
        return True, "All requirements satisfied!"
    except ImportError as e:
        return False, f"Missing requirement: {e}"

def launch_gui():
    """Launch the main GUI application"""
    try:
        from simulation_gui import UUVSimulationGUI
        print("🌊 Launching UUV Communication Simulation GUI...")
        print("📱 GUI window should appear shortly...")
        
        app = UUVSimulationGUI()
        app.run()
        
    except Exception as e:
        print(f"❌ Error launching GUI: {e}")
        
        # Show error dialog if tkinter is available
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Launch Error", f"Failed to launch GUI:\n{e}")
        except:
            pass

def main():
    """Main launcher function"""
    print("=" * 60)
    print("🌊 UUV COMMUNICATION SIMULATION GUI LAUNCHER 🌊")
    print("=" * 60)
    print()
    
    # Check requirements
    requirements_ok, message = check_requirements()
    
    if not requirements_ok:
        print(f"❌ Requirements check failed: {message}")
        print("\nPlease ensure all required modules are installed.")
        sys.exit(1)
    
    print(f"✅ {message}")
    print()
    print("🚀 Starting GUI application...")
    print("   • Main menu with simulation options")
    print("   • Interactive configuration forms")
    print("   • Real-time monitoring")
    print("   • Comprehensive results display")
    print()
    
    # Launch GUI
    launch_gui()

if __name__ == "__main__":
    main() 