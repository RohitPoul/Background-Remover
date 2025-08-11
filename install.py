#!/usr/bin/env python3
"""
Installation script for Advanced Anime Background Remover
"""

import subprocess
import sys
import os
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {command}")
        print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} detected")
        print("   This application requires Python 3.8 or higher")
        print("   Please upgrade Python and try again")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def check_pip():
    """Check if pip is available"""
    print("📦 Checking pip availability...")
    
    try:
        import pip
        print("✅ pip is available")
        return True
    except ImportError:
        print("❌ pip not found")
        print("   Please install pip and try again")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("📚 Installing dependencies...")
    
    # Core dependencies
    core_deps = [
        "Pillow>=10.0.0",
        "numpy>=1.24.0",
        "opencv-python>=4.8.0",
        "onnxruntime>=1.15.0"
    ]
    
    for dep in core_deps:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            return False
    
    # Optional dependencies
    optional_deps = [
        "rembg>=2.0.0",
        "scikit-image>=0.21.0"
    ]
    
    print("\n📦 Installing optional dependencies...")
    for dep in optional_deps:
        try:
            run_command(f"pip install {dep}", f"Installing {dep}")
        except:
            print(f"⚠️  {dep} installation failed (optional)")
    
    return True

def create_directories():
    """Create necessary directories"""
    print("📁 Creating application directories...")
    
    home_dir = os.path.expanduser("~")
    app_dir = os.path.join(home_dir, ".anime_bg_remover")
    logs_dir = os.path.join(app_dir, "logs")
    
    try:
        os.makedirs(app_dir, exist_ok=True)
        os.makedirs(logs_dir, exist_ok=True)
        print("✅ Application directories created")
        return True
    except Exception as e:
        print(f"❌ Failed to create directories: {e}")
        return False

def test_installation():
    """Test if the installation was successful"""
    print("\n🧪 Testing installation...")
    
    try:
        # Test imports
        import tkinter
        print("✅ tkinter imported successfully")
        
        from PIL import Image
        print("✅ PIL/Pillow imported successfully")
        
        import numpy
        print("✅ numpy imported successfully")
        
        import cv2
        print("✅ OpenCV imported successfully")
        
        import onnxruntime
        print("✅ ONNX Runtime imported successfully")
        
        # Test optional imports
        try:
            from rembg import remove
            print("✅ rembg imported successfully")
        except ImportError:
            print("⚠️  rembg not available (optional)")
        
        return True
        
    except Exception as e:
        print(f"❌ Installation test failed: {e}")
        return False

def main():
    """Main installation process"""
    print("🎌 Advanced Anime Background Remover - Installation")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python_version():
        return False
    
    if not check_pip():
        return False
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Create directories
    if not create_directories():
        return False
    
    # Test installation
    if not test_installation():
        return False
    
    print("\n🎉 Installation completed successfully!")
    print("\n📋 Next steps:")
    print("   1. Run the test script: python test_app.py")
    print("   2. Launch the application: python anime_bg_remover.py")
    print("\n📚 For more information, see README.md")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ Installation failed. Please check the error messages above.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Installation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during installation: {e}")
        sys.exit(1)