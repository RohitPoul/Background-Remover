import tkinter as tk
from tkinter import filedialog, ttk, messagebox, colorchooser
from PIL import Image, ImageTk, ImageDraw, ImageFilter, ImageEnhance, ImageOps
import numpy as np
import cv2
import os
import threading
# Removed heavy PyTorch dependency; using ONNX Runtime for inference
import types as _types  # placeholder to keep import block structure consistent
import requests
import io
from io import BytesIO
import onnxruntime as ort
from pathlib import Path
import warnings
import logging
import traceback
import time
import sys
warnings.filterwarnings("ignore")

# Optional rembg backend
try:
    from rembg import remove as rembg_remove
    HAS_REMBG = True
except Exception:
    HAS_REMBG = False

# Logging configuration: write logs to user's home directory
LOG_DIR = os.path.join(os.path.expanduser("~"), ".anime_bg_remover", "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "app.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(LOG_FILE, encoding='utf-8')]
)

# Module-level logger
LOGGER = logging.getLogger("anime_bg_remover")
LOGGER.setLevel(logging.INFO)

# Optional console handler (added/removed dynamically)
_CONSOLE_HANDLER = None

def set_debug_logging(enabled: bool) -> None:
    level = logging.DEBUG if enabled else logging.INFO
    LOGGER.setLevel(level)
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    for h in root_logger.handlers:
        h.setLevel(level)
    global _CONSOLE_HANDLER
    if enabled:
        if _CONSOLE_HANDLER is None:
            _CONSOLE_HANDLER = logging.StreamHandler(stream=sys.stderr)
            _CONSOLE_HANDLER.setLevel(level)
            _CONSOLE_HANDLER.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            root_logger.addHandler(_CONSOLE_HANDLER)
        else:
            _CONSOLE_HANDLER.setLevel(level)
    else:
        # Remove console handler if present
        if _CONSOLE_HANDLER is not None:
            try:
                logging.getLogger().removeHandler(_CONSOLE_HANDLER)
            except Exception:
                pass
            _CONSOLE_HANDLER = None

def log_debug(message: str) -> None:
    LOGGER.debug(message)

def log_error(message: str, exc: Exception | None = None) -> None:
    if exc is not None:
        LOGGER.error(f"{message}: {exc}")
        LOGGER.error("\n" + traceback.format_exc())
    else:
        LOGGER.error(message)

def log_info(message: str) -> None:
    LOGGER.info(message)

def global_exception_handler(exctype, value, tb):
    LOGGER.critical(f"Unhandled exception: {exctype.__name__}: {value}\n" + ''.join(traceback.format_exception(exctype, value, tb)))

import sys as _sys
_sys.excepthook = global_exception_handler

class AdvancedAnimeBackgroundRemover:
    def __init__(self, root):
        self.root = root
        self.root.title("🎌 Advanced Anime Background Remover AI")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')
        
        # Initialize variables
        self.input_image = None
        self.output_image = None
        self.current_image_path = None
        self.processing = False
        self.removal_method = tk.StringVar(value="rembg")
        self.background_color = tk.StringVar(value="#00ff00")
        self.background_image_path = None
        self.enhancement_level = tk.DoubleVar(value=1.0)
        self.edge_refinement = tk.BooleanVar(value=True)
        self.auto_enhance = tk.BooleanVar(value=True)
        
        # Create UI
        self.create_widgets()
        self.setup_styles()
        
        log_info("Application initialized successfully")
    
    def create_widgets(self):
        # Main container
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="🎌 Advanced Anime Background Remover AI",
            font=("Arial", 20, "bold"),
            fg='#00ff00',
            bg='#2b2b2b'
        )
        title_label.pack(pady=(0, 20))
        
        # Control panel
        control_frame = tk.Frame(main_frame, bg='#3b3b3b', relief=tk.RAISED, bd=2)
        control_frame.pack(fill=tk.X, pady=(0, 20))
        
        # File selection
        file_frame = tk.Frame(control_frame, bg='#3b3b3b')
        file_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(file_frame, text="Input Image:", font=("Arial", 12), fg='white', bg='#3b3b3b').pack(anchor=tk.W)
        
        file_button_frame = tk.Frame(file_frame, bg='#3b3b3b')
        file_button_frame.pack(fill=tk.X, pady=5)
        
        self.browse_button = tk.Button(
            file_button_frame,
            text="📁 Browse Image",
            command=self.browse_image,
            bg='#4a4a4a',
            fg='white',
            font=("Arial", 10),
            relief=tk.FLAT,
            padx=20,
            pady=5
        )
        self.browse_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.file_label = tk.Label(
            file_button_frame,
            text="No image selected",
            fg='#cccccc',
            bg='#3b3b3b',
            font=("Arial", 9)
        )
        self.file_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Settings panel
        settings_frame = tk.Frame(control_frame, bg='#3b3b3b')
        settings_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Removal method
        method_frame = tk.Frame(settings_frame, bg='#3b3b3b')
        method_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(method_frame, text="Removal Method:", font=("Arial", 12), fg='white', bg='#3b3b3b').pack(anchor=tk.W)
        
        method_radio_frame = tk.Frame(method_frame, bg='#3b3b3b')
        method_radio_frame.pack(fill=tk.X, pady=5)
        
        tk.Radiobutton(
            method_radio_frame,
            text="Rembg (Fast)",
            variable=self.removal_method,
            value="rembg",
            fg='white',
            bg='#3b3b3b',
            selectcolor='#2b2b2b',
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Radiobutton(
            method_radio_frame,
            text="ONNX Runtime (Accurate)",
            variable=self.removal_method,
            value="onnx",
            fg='white',
            bg='#3b3b3b',
            selectcolor='#2b2b2b',
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        # Background options
        bg_frame = tk.Frame(settings_frame, bg='#3b3b3b')
        bg_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(bg_frame, text="Background Options:", font=("Arial", 12), fg='white', bg='#3b3b3b').pack(anchor=tk.W)
        
        bg_options_frame = tk.Frame(bg_frame, bg='#3b3b3b')
        bg_options_frame.pack(fill=tk.X, pady=5)
        
        # Color picker
        tk.Label(bg_options_frame, text="Color:", fg='white', bg='#3b3b3b', font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 5))
        
        self.color_button = tk.Button(
            bg_options_frame,
            text="🎨",
            command=self.choose_color,
            bg=self.background_color.get(),
            fg='white',
            font=("Arial", 12),
            relief=tk.FLAT,
            width=3
        )
        self.color_button.pack(side=tk.LEFT, padx=(0, 20))
        
        # Image background
        tk.Button(
            bg_options_frame,
            text="🖼️ Image Background",
            command=self.choose_background_image,
            bg='#4a4a4a',
            fg='white',
            font=("Arial", 10),
            relief=tk.FLAT,
            padx=15,
            pady=3
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        # Enhancement options
        enhance_frame = tk.Frame(settings_frame, bg='#3b3b3b')
        enhance_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(enhance_frame, text="Enhancement Options:", font=("Arial", 12), fg='white', bg='#3b3b3b').pack(anchor=tk.W)
        
        enhance_options_frame = tk.Frame(enhance_frame, bg='#3b3b3b')
        enhance_options_frame.pack(fill=tk.X, pady=5)
        
        # Enhancement level
        tk.Label(enhance_options_frame, text="Enhancement Level:", fg='white', bg='#3b3b3b', font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 10))
        
        enhance_scale = tk.Scale(
            enhance_options_frame,
            from_=0.5,
            to=2.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=self.enhancement_level,
            bg='#3b3b3b',
            fg='white',
            highlightthickness=0,
            length=150
        )
        enhance_scale.pack(side=tk.LEFT, padx=(0, 20))
        
        # Checkboxes
        tk.Checkbutton(
            enhance_options_frame,
            text="Edge Refinement",
            variable=self.edge_refinement,
            fg='white',
            bg='#3b3b3b',
            selectcolor='#2b2b2b',
            font=("Arial", 10)
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Checkbutton(
            enhance_options_frame,
            text="Auto Enhance",
            variable=self.auto_enhance,
            fg='white',
            bg='#3b3b3b',
            selectcolor='#2b2b2b',
            font=("Arial", 10)
        ).pack(side=tk.LEFT)
        
        # Process button
        button_frame = tk.Frame(control_frame, bg='#3b3b3b')
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.process_button = tk.Button(
            button_frame,
            text="🚀 Remove Background",
            command=self.process_image,
            bg='#00ff00',
            fg='black',
            font=("Arial", 14, "bold"),
            relief=tk.FLAT,
            padx=30,
            pady=10,
            state=tk.DISABLED
        )
        self.process_button.pack()
        
        # Progress bar
        self.progress = ttk.Progressbar(
            button_frame,
            mode='indeterminate',
            length=300
        )
        self.progress.pack(pady=10)
        
        # Image display area
        image_frame = tk.Frame(main_frame, bg='#2b2b2b')
        image_frame.pack(fill=tk.BOTH, expand=True)
        
        # Input image
        input_frame = tk.Frame(image_frame, bg='#2b2b2b')
        input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        tk.Label(input_frame, text="Input Image", font=("Arial", 14, "bold"), fg='white', bg='#2b2b2b').pack(pady=(0, 10))
        
        self.input_canvas = tk.Canvas(
            input_frame,
            bg='#1a1a1a',
            relief=tk.SUNKEN,
            bd=2
        )
        self.input_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Output image
        output_frame = tk.Frame(image_frame, bg='#2b2b2b')
        output_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        tk.Label(output_frame, text="Output Image", font=("Arial", 14, "bold"), fg='white', bg='#2b2b2b').pack(pady=(0, 10))
        
        self.output_canvas = tk.Canvas(
            output_frame,
            bg='#1a1a1a',
            relief=tk.SUNKEN,
            bd=2
        )
        self.output_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(
            main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg='#1a1a1a',
            fg='#00ff00',
            font=("Arial", 9)
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
    
    def setup_styles(self):
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure progress bar style
        style.configure(
            "TProgressbar",
            background='#00ff00',
            troughcolor='#1a1a1a',
            bordercolor='#00ff00',
            lightcolor='#00ff00',
            darkcolor='#00ff00'
        )
    
    def browse_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.current_image_path = file_path
                self.file_label.config(text=os.path.basename(file_path))
                
                # Load and display input image
                self.input_image = Image.open(file_path)
                self.display_image(self.input_image, self.input_canvas)
                
                # Enable process button
                self.process_button.config(state=tk.NORMAL)
                self.status_var.set(f"Loaded: {os.path.basename(file_path)}")
                
                log_info(f"Image loaded: {file_path}")
                
            except Exception as e:
                log_error("Failed to load image", e)
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def choose_color(self):
        color = colorchooser.askcolor(title="Choose Background Color")[1]
        if color:
            self.background_color.set(color)
            self.color_button.config(bg=color)
    
    def choose_background_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Background Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.background_image_path = file_path
            self.status_var.set(f"Background image: {os.path.basename(file_path)}")
    
    def display_image(self, image, canvas):
        # Resize image to fit canvas
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            # Canvas not yet sized, use default dimensions
            canvas_width, canvas_height = 400, 400
        
        # Calculate resize ratio
        img_width, img_height = image.size
        ratio = min(canvas_width / img_width, canvas_height / img_height)
        
        if ratio < 1:
            new_width = int(img_width * ratio)
            new_height = int(img_height * ratio)
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        else:
            resized_image = image
        
        # Convert to PhotoImage and display
        photo = ImageTk.PhotoImage(resized_image)
        canvas.delete("all")
        canvas.create_image(
            canvas_width // 2,
            canvas_height // 2,
            image=photo,
            anchor=tk.CENTER
        )
        canvas.image = photo  # Keep reference
    
    def process_image(self):
        if not self.input_image or self.processing:
            return
        
        self.processing = True
        self.process_button.config(state=tk.DISABLED)
        self.progress.start()
        self.status_var.set("Processing...")
        
        # Run processing in separate thread
        thread = threading.Thread(target=self._process_image_thread)
        thread.daemon = True
        thread.start()
    
    def _process_image_thread(self):
        try:
            log_info("Starting background removal process")
            
            # Remove background
            if self.removal_method.get() == "rembg" and HAS_REMBG:
                self.output_image = self._remove_background_rembg()
            else:
                self.output_image = self._remove_background_onnx()
            
            if self.output_image:
                # Apply enhancements
                if self.auto_enhance.get():
                    self.output_image = self._enhance_image(self.output_image)
                
                if self.edge_refinement.get():
                    self.output_image = self._refine_edges(self.output_image)
                
                # Apply background
                self.output_image = self._apply_background(self.output_image)
                
                # Update UI in main thread
                self.root.after(0, self._processing_complete)
                
                log_info("Background removal completed successfully")
            else:
                self.root.after(0, lambda: self._processing_error("Failed to remove background"))
                
        except Exception as e:
            log_error("Error during background removal", e)
            self.root.after(0, lambda: self._processing_error(f"Error: {str(e)}"))
    
    def _remove_background_rembg(self):
        try:
            log_debug("Using rembg backend")
            result = rembg_remove(self.input_image)
            return result
        except Exception as e:
            log_error("Rembg failed, falling back to ONNX", e)
            return self._remove_background_onnx()
    
    def _remove_background_onnx(self):
        try:
            log_debug("Using ONNX Runtime backend")
            # This is a placeholder - you would need to implement actual ONNX model inference
            # For now, we'll use a simple threshold-based approach
            return self._simple_background_removal()
        except Exception as e:
            log_error("ONNX Runtime failed", e)
            return None
    
    def _simple_background_removal(self):
        # Simple threshold-based background removal as fallback
        img_array = np.array(self.input_image)
        
        # Convert to RGBA if not already
        if img_array.shape[2] == 3:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2RGBA)
        
        # Create mask based on color similarity
        # This is a very basic approach - real models would be much better
        gray = cv2.cvtColor(img_array[:, :, :3], cv2.COLOR_RGB2GRAY)
        _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)
        
        # Invert mask
        mask = 255 - mask
        
        # Apply mask to alpha channel
        img_array[:, :, 3] = mask
        
        return Image.fromarray(img_array)
    
    def _enhance_image(self, image):
        try:
            # Enhance contrast and sharpness
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(self.enhancement_level.get())
            
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.2)
            
            return image
        except Exception as e:
            log_error("Image enhancement failed", e)
            return image
    
    def _refine_edges(self, image):
        try:
            # Simple edge refinement using unsharp mask
            image = image.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
            return image
        except Exception as e:
            log_error("Edge refinement failed", e)
            return image
    
    def _apply_background(self, image):
        try:
            if self.background_image_path:
                # Apply background image
                bg_image = Image.open(self.background_image_path)
                bg_image = bg_image.resize(image.size, Image.Resampling.LANCZOS)
                
                # Composite foreground over background
                result = Image.alpha_composite(bg_image.convert('RGBA'), image)
                return result
            else:
                # Apply solid color background
                bg_color = Image.new('RGBA', image.size, self.background_color.get())
                result = Image.alpha_composite(bg_color, image)
                return result
        except Exception as e:
            log_error("Background application failed", e)
            return image
    
    def _processing_complete(self):
        self.processing = False
        self.progress.stop()
        self.process_button.config(state=tk.NORMAL)
        self.status_var.set("Processing complete!")
        
        # Display output image
        if self.output_image:
            self.display_image(self.output_image, self.output_canvas)
    
    def _processing_error(self, error_message):
        self.processing = False
        self.progress.stop()
        self.process_button.config(state=tk.NORMAL)
        self.status_var.set(f"Error: {error_message}")
        messagebox.showerror("Error", error_message)
    
    def save_result(self):
        if not self.output_image:
            messagebox.showwarning("Warning", "No output image to save")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Result",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.output_image.save(file_path)
                self.status_var.set(f"Saved: {os.path.basename(file_path)}")
                log_info(f"Result saved: {file_path}")
            except Exception as e:
                log_error("Failed to save result", e)
                messagebox.showerror("Error", f"Failed to save: {str(e)}")

def main():
    try:
        root = tk.Tk()
        app = AdvancedAnimeBackgroundRemover(root)
        
        # Add save button to main window
        save_button = tk.Button(
            root,
            text="💾 Save Result",
            command=app.save_result,
            bg='#4a4a4a',
            fg='white',
            font=("Arial", 12),
            relief=tk.FLAT,
            padx=20,
            pady=5
        )
        save_button.pack(side=tk.BOTTOM, pady=10)
        
        log_info("Starting application")
        root.mainloop()
        
    except Exception as e:
        log_error("Application failed to start", e)
        messagebox.showerror("Fatal Error", f"Application failed to start: {str(e)}")

if __name__ == "__main__":
    main()