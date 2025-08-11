#!/usr/bin/env python3
"""
Simple test script for the Advanced Anime Background Remover
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import tkinter as tk
        print("✓ tkinter imported successfully")
    except ImportError as e:
        print(f"✗ tkinter import failed: {e}")
        return False
    
    try:
        from PIL import Image
        print("✓ PIL/Pillow imported successfully")
    except ImportError as e:
        print(f"✗ PIL import failed: {e}")
        return False
    
    try:
        import numpy as np
        print("✓ numpy imported successfully")
    except ImportError as e:
        print(f"✗ numpy import failed: {e}")
        return False
    
    try:
        import cv2
        print("✓ OpenCV imported successfully")
    except ImportError as e:
        print(f"✗ OpenCV import failed: {e}")
        return False
    
    try:
        import onnxruntime as ort
        print("✓ ONNX Runtime imported successfully")
    except ImportError as e:
        print(f"✗ ONNX Runtime import failed: {e}")
        return False
    
    # Test optional rembg
    try:
        from rembg import remove
        print("✓ rembg imported successfully")
    except ImportError:
        print("⚠ rembg not available (optional)")
    
    return True

def test_app_import():
    """Test if the main application can be imported"""
    print("\nTesting application import...")
    
    try:
        # Add current directory to path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from anime_bg_remover import AdvancedAnimeBackgroundRemover
        print("✓ Main application class imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Application import failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error during import: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality without GUI"""
    print("\nTesting basic functionality...")
    
    try:
        from anime_bg_remover import log_info, log_error, log_debug
        
        # Test logging functions
        log_info("Test info message")
        log_debug("Test debug message")
        log_error("Test error message")
        print("✓ Logging functions work correctly")
        
        return True
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🎌 Advanced Anime Background Remover - Test Suite")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Please install required dependencies:")
        print("pip install -r requirements.txt")
        return False
    
    # Test app import
    if not test_app_import():
        print("\n❌ Application import failed. Check the code for syntax errors.")
        return False
    
    # Test basic functionality
    if not test_basic_functionality():
        print("\n❌ Basic functionality test failed.")
        return False
    
    print("\n🎉 All tests passed! The application should work correctly.")
    print("\nTo run the application:")
    print("python anime_bg_remover.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)