#!/usr/bin/env python3
"""
Launcher script for Advanced Anime Background Remover
"""

import sys
import os
import subprocess
import tkinter as tk
from tkinter import messagebox

def check_dependencies():
    """Check if all required dependencies are available"""
    missing_deps = []
    
    try:
        import tkinter
    except ImportError:
        missing_deps.append("tkinter")
    
    try:
        from PIL import Image
    except ImportError:
        missing_deps.append("Pillow")
    
    try:
        import numpy
    except ImportError:
        missing_deps.append("numpy")
    
    try:
        import cv2
    except ImportError:
        missing_deps.append("OpenCV")
    
    try:
        import onnxruntime
    except ImportError:
        missing_deps.append("ONNX Runtime")
    
    return missing_deps

def show_dependency_error(missing_deps):
    """Show error dialog for missing dependencies"""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    error_msg = f"""Missing required dependencies:

{', '.join(missing_deps)}

Please install them using:
pip install -r requirements.txt

Or run the installation script:
python install.py"""
    
    messagebox.showerror("Missing Dependencies", error_msg)
    root.destroy()

def show_launch_error(error_msg):
    """Show error dialog for launch errors"""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    messagebox.showerror("Launch Error", error_msg)
    root.destroy()

def main():
    """Main launcher function"""
    print("🎌 Advanced Anime Background Remover - Launcher")
    print("=" * 45)
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    missing_deps = check_dependencies()
    
    if missing_deps:
        print(f"❌ Missing dependencies: {', '.join(missing_deps)}")
        show_dependency_error(missing_deps)
        print("\n💡 Please install missing dependencies and try again")
        return False
    
    print("✅ All dependencies available")
    
    # Try to launch the application
    print("🚀 Launching application...")
    
    try:
        # Import and run the main application
        from anime_bg_remover import main as app_main
        app_main()
        return True
        
    except ImportError as e:
        error_msg = f"Failed to import application: {e}"
        print(f"❌ {error_msg}")
        show_launch_error(error_msg)
        return False
        
    except Exception as e:
        error_msg = f"Failed to launch application: {e}"
        print(f"❌ {error_msg}")
        show_launch_error(error_msg)
        return False

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Application launch failed")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Launch interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during launch: {e}")
        sys.exit(1)