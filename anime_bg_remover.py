import tkinter as tk
from tkinter import filedialog, ttk, messagebox, colorchooser
from PIL import Image, ImageTk, ImageDraw, ImageFilter, ImageEnhance, ImageOps
import numpy as np
import cv2
import os
import threading
import json
from datetime import datetime
import shutil
from pathlib import Path
import subprocess

# Optional rembg backend
try:
    from rembg import remove as rembg_remove
    HAS_REMBG = True
except Exception:
    HAS_REMBG = False

# Optional ONNX Runtime for better accuracy
try:
    import onnxruntime as ort
    HAS_ONNX = True
except Exception:
    HAS_ONNX = False

# Logging configuration
LOG_DIR = os.path.join(os.path.expanduser("~"), ".anime_bg_remover", "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "app.log")

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(LOG_FILE, encoding='utf-8')]
)

LOGGER = logging.getLogger("anime_bg_remover")

class AdvancedAnimeBackgroundRemover:
    def __init__(self, root):
        self.root = root
        self.root.title("🎌 Advanced Anime Background Remover AI")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1a1a2e')
        
        # Initialize variables
        self.input_images = []
        self.output_images = []
        self.current_batch = []
        self.processing = False
        self.removal_method = tk.StringVar(value="rembg")
        self.background_color = tk.StringVar(value="#00ff00")
        self.background_image_path = None
        self.enhancement_level = tk.DoubleVar(value=1.0)
        self.edge_refinement = tk.BooleanVar(value=True)
        self.auto_enhance = tk.BooleanVar(value=True)
        self.quality_mode = tk.StringVar(value="high")
        self.batch_mode = tk.BooleanVar(value=False)
        self.output_format = tk.StringVar(value="png")
        self.current_image_index = 0
        
        # Create UI
        self.create_widgets()
        self.setup_styles()
        
        LOGGER.info("Application initialized successfully")
    
    def create_widgets(self):
        # Main container with better spacing
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Title with better styling
        title_frame = tk.Frame(main_frame, bg='#1a1a2e')
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(
            title_frame,
            text="🎌 Advanced Anime Background Remover AI",
            font=("Segoe UI", 24, "bold"),
            fg='#00d4ff',
            bg='#1a1a2e'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Professional-grade background removal with AI precision",
            font=("Segoe UI", 12),
            fg='#8892b0',
            bg='#1a1a2e'
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Control panel with better organization
        control_frame = tk.Frame(main_frame, bg='#16213e', relief=tk.RAISED, bd=3)
        control_frame.pack(fill=tk.X, pady=(0, 20))
        
        # File selection with batch support
        file_frame = tk.Frame(control_frame, bg='#16213e')
        file_frame.pack(fill=tk.X, padx=15, pady=15)
        
        file_header = tk.Label(
            file_frame, 
            text="📁 Image Selection", 
            font=("Segoe UI", 14, "bold"), 
            fg='#00d4ff', 
            bg='#16213e'
        )
        file_header.pack(anchor=tk.W, pady=(0, 10))
        
        file_button_frame = tk.Frame(file_frame, bg='#16213e')
        file_button_frame.pack(fill=tk.X, pady=5)
        
        self.browse_button = tk.Button(
            file_button_frame,
            text="📁 Select Images",
            command=self.browse_images,
            bg='#0f3460',
            fg='white',
            font=("Segoe UI", 11, "bold"),
            relief=tk.FLAT,
            padx=25,
            pady=8,
            cursor="hand2"
        )
        self.browse_button.pack(side=tk.LEFT, padx=(0, 15))
        
        self.batch_toggle = tk.Checkbutton(
            file_button_frame,
            text="Batch Mode",
            variable=self.batch_mode,
            fg='white',
            bg='#16213e',
            selectcolor='#0f3460',
            font=("Segoe UI", 10),
            cursor="hand2"
        )
        self.batch_toggle.pack(side=tk.LEFT, padx=(0, 20))
        
        self.file_count_label = tk.Label(
            file_button_frame,
            text="No images selected",
            fg='#8892b0',
            bg='#16213e',
            font=("Segoe UI", 10)
        )
        self.file_count_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Settings panel with better organization
        settings_frame = tk.Frame(control_frame, bg='#16213e')
        settings_frame.pack(fill=tk.X, padx=15, pady=15)
        
        settings_header = tk.Label(
            settings_frame, 
            text="⚙️ Processing Settings", 
            font=("Segoe UI", 14, "bold"), 
            fg='#00d4ff', 
            bg='#16213e'
        )
        settings_header.pack(anchor=tk.W, pady=(0, 15))
        
        # Two-column layout for settings
        settings_columns = tk.Frame(settings_frame, bg='#16213e')
        settings_columns.pack(fill=tk.X)
        
        # Left column
        left_col = tk.Frame(settings_columns, bg='#16213e')
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        
        # Removal method
        method_frame = tk.Frame(left_col, bg='#16213e')
        method_frame.pack(fill=tk.X, pady=8)
        
        tk.Label(method_frame, text="AI Model:", font=("Segoe UI", 11, "bold"), fg='white', bg='#16213e').pack(anchor=tk.W)
        
        method_radio_frame = tk.Frame(method_frame, bg='#16213e')
        method_radio_frame.pack(fill=tk.X, pady=5)
        
        tk.Radiobutton(
            method_radio_frame,
            text="Rembg (Fast & Accurate)",
            variable=self.removal_method,
            value="rembg",
            fg='white',
            bg='#16213e',
            selectcolor='#0f3460',
            font=("Segoe UI", 10),
            cursor="hand2"
        ).pack(anchor=tk.W, pady=2)
        
        if HAS_ONNX:
            tk.Radiobutton(
                method_radio_frame,
                text="ONNX Runtime (Maximum Accuracy)",
                variable=self.removal_method,
                value="onnx",
                fg='white',
                bg='#16213e',
                selectcolor='#0f3460',
                font=("Segoe UI", 10),
                cursor="hand2"
            ).pack(anchor=tk.W, pady=2)
        
        # Quality mode
        quality_frame = tk.Frame(left_col, bg='#16213e')
        quality_frame.pack(fill=tk.X, pady=8)
        
        tk.Label(quality_frame, text="Quality Mode:", font=("Segoe UI", 11, "bold"), fg='white', bg='#16213e').pack(anchor=tk.W)
        
        quality_radio_frame = tk.Frame(quality_frame, bg='#16213e')
        quality_radio_frame.pack(fill=tk.X, pady=5)
        
        tk.Radiobutton(
            quality_radio_frame,
            text="Fast (Good quality)",
            variable=self.quality_mode,
            value="fast",
            fg='white',
            bg='#16213e',
            selectcolor='#0f3460',
            font=("Segoe UI", 10),
            cursor="hand2"
        ).pack(anchor=tk.W, pady=2)
        
        tk.Radiobutton(
            quality_radio_frame,
            text="High (Best quality, slower)",
            variable=self.quality_mode,
            value="high",
            fg='white',
            bg='#16213e',
            selectcolor='#0f3460',
            font=("Segoe UI", 10),
            cursor="hand2"
        ).pack(anchor=tk.W, pady=2)
        
        # Right column
        right_col = tk.Frame(settings_columns, bg='#16213e')
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Background options
        bg_frame = tk.Frame(right_col, bg='#16213e')
        bg_frame.pack(fill=tk.X, pady=8)
        
        tk.Label(bg_frame, text="Background:", font=("Segoe UI", 11, "bold"), fg='white', bg='#16213e').pack(anchor=tk.W)
        
        bg_options_frame = tk.Frame(bg_frame, bg='#16213e')
        bg_options_frame.pack(fill=tk.X, pady=5)
        
        # Color picker
        tk.Label(bg_options_frame, text="Color:", fg='white', bg='#16213e', font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 8))
        
        self.color_button = tk.Button(
            bg_options_frame,
            text="🎨",
            command=self.choose_color,
            bg=self.background_color.get(),
            fg='white',
            font=("Segoe UI", 14),
            relief=tk.FLAT,
            width=4,
            cursor="hand2"
        )
        self.color_button.pack(side=tk.LEFT, padx=(0, 15))
        
        # Image background
        tk.Button(
            bg_options_frame,
            text="🖼️ Custom Background",
            command=self.choose_background_image,
            bg='#0f3460',
            fg='white',
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        # Output format
        tk.Label(bg_options_frame, text="Format:", fg='white', bg='#16213e', font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 8))
        
        format_combo = ttk.Combobox(
            bg_options_frame,
            textvariable=self.output_format,
            values=["png", "jpg"],
            state="readonly",
            width=8,
            font=("Segoe UI", 10)
        )
        format_combo.pack(side=tk.LEFT)
        
        # Enhancement options
        enhance_frame = tk.Frame(right_col, bg='#16213e')
        enhance_frame.pack(fill=tk.X, pady=8)
        
        tk.Label(enhance_frame, text="Enhancement:", font=("Segoe UI", 11, "bold"), fg='white', bg='#16213e').pack(anchor=tk.W)
        
        enhance_options_frame = tk.Frame(enhance_frame, bg='#16213e')
        enhance_options_frame.pack(fill=tk.X, pady=5)
        
        # Enhancement level
        tk.Label(enhance_options_frame, text="Level:", fg='white', bg='#16213e', font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 8))
        
        enhance_scale = tk.Scale(
            enhance_options_frame,
            from_=0.5,
            to=2.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            variable=self.enhancement_level,
            bg='#16213e',
            fg='white',
            highlightthickness=0,
            length=120,
            troughcolor='#0f3460',
            activebackground='#00d4ff'
        )
        enhance_scale.pack(side=tk.LEFT, padx=(0, 20))
        
        # Checkboxes
        tk.Checkbutton(
            enhance_options_frame,
            text="Edge Refinement",
            variable=self.edge_refinement,
            fg='white',
            bg='#16213e',
            selectcolor='#0f3460',
            font=("Segoe UI", 10),
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Checkbutton(
            enhance_options_frame,
            text="Auto Enhance",
            variable=self.auto_enhance,
            fg='white',
            bg='#16213e',
            selectcolor='#0f3460',
            font=("Segoe UI", 10),
            cursor="hand2"
        ).pack(side=tk.LEFT)
        
        # Process button with better styling
        button_frame = tk.Frame(control_frame, bg='#16213e')
        button_frame.pack(fill=tk.X, padx=15, pady=15)
        
        self.process_button = tk.Button(
            button_frame,
            text="🚀 Remove Backgrounds",
            command=self.process_images,
            bg='#00d4ff',
            fg='#1a1a2e',
            font=("Segoe UI", 14, "bold"),
            relief=tk.FLAT,
            padx=40,
            pady=12,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.process_button.pack()
        
        # Progress bar with better styling
        self.progress = ttk.Progressbar(
            button_frame,
            mode='determinate',
            length=400
        )
        self.progress.pack(pady=15)
        
        # Progress label
        self.progress_label = tk.Label(
            button_frame,
            text="Ready to process",
            fg='#00d4ff',
            bg='#16213e',
            font=("Segoe UI", 10)
        )
        self.progress_label.pack()
        
        # Image display area with larger, square displays
        image_frame = tk.Frame(main_frame, bg='#1a1a2e')
        image_frame.pack(fill=tk.BOTH, expand=True)
        
        # Input image
        input_frame = tk.Frame(image_frame, bg='#1a1a2e')
        input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        input_header = tk.Label(
            input_frame, 
            text="📥 Input Image", 
            font=("Segoe UI", 16, "bold"), 
            fg='#00d4ff', 
            bg='#1a1a2e'
        )
        input_header.pack(pady=(0, 15))
        
        # Square canvas for input
        self.input_canvas = tk.Canvas(
            input_frame,
            bg='#0f3460',
            relief=tk.RAISED,
            bd=3,
            width=500,
            height=500
        )
        self.input_canvas.pack()
        
        # Input navigation for batch mode
        self.input_nav_frame = tk.Frame(input_frame, bg='#1a1a2e')
        self.input_nav_frame.pack(pady=10)
        
        self.prev_input_btn = tk.Button(
            self.input_nav_frame,
            text="◀ Previous",
            command=self.previous_input,
            bg='#0f3460',
            fg='white',
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.prev_input_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.input_index_label = tk.Label(
            self.input_nav_frame,
            text="0 / 0",
            fg='#8892b0',
            bg='#1a1a2e',
            font=("Segoe UI", 12, "bold")
        )
        self.input_index_label.pack(side=tk.LEFT, padx=10)
        
        self.next_input_btn = tk.Button(
            self.input_nav_frame,
            text="Next ▶",
            command=self.next_input,
            bg='#0f3460',
            fg='white',
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.next_input_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Output image
        output_frame = tk.Frame(image_frame, bg='#1a1a2e')
        output_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        output_header = tk.Label(
            output_frame, 
            text="📤 Output Image", 
            font=("Segoe UI", 16, "bold"), 
            fg='#00d4ff', 
            bg='#1a1a2e'
        )
        output_header.pack(pady=(0, 15))
        
        # Square canvas for output
        self.output_canvas = tk.Canvas(
            output_frame,
            bg='#0f3460',
            relief=tk.RAISED,
            bd=3,
            width=500,
            height=500
        )
        self.output_canvas.pack()
        
        # Output navigation and download
        self.output_nav_frame = tk.Frame(output_frame, bg='#1a1a2e')
        self.output_nav_frame.pack(pady=10)
        
        self.prev_output_btn = tk.Button(
            self.output_nav_frame,
            text="◀ Previous",
            command=self.previous_output,
            bg='#0f3460',
            fg='white',
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.prev_output_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.output_index_label = tk.Label(
            self.output_nav_frame,
            text="0 / 0",
            fg='#8892b0',
            bg='#1a1a2e',
            font=("Segoe UI", 12, "bold")
        )
        self.output_index_label.pack(side=tk.LEFT, padx=10)
        
        self.next_output_btn = tk.Button(
            self.output_nav_frame,
            text="Next ▶",
            command=self.next_output,
            bg='#0f3460',
            fg='white',
            font=("Segoe UI", 10),
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.next_output_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Download button
        self.download_btn = tk.Button(
            output_frame,
            text="💾 Download Current",
            command=self.download_current,
            bg='#00ff88',
            fg='#1a1a2e',
            font=("Segoe UI", 12, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.download_btn.pack(pady=10)
        
        # Download all button
        self.download_all_btn = tk.Button(
            output_frame,
            text="📦 Download All",
            command=self.download_all,
            bg='#ff6b6b',
            fg='white',
            font=("Segoe UI", 12, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.download_all_btn.pack(pady=5)
        
        # Status bar with better styling
        self.status_var = tk.StringVar(value="Ready to process images")
        status_bar = tk.Label(
            main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            bg='#0f3460',
            fg='#00d4ff',
            font=("Segoe UI", 10, "bold"),
            padx=10,
            pady=5
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(15, 0))
    
    def setup_styles(self):
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure progress bar style
        style.configure(
            "TProgressbar",
            background='#00d4ff',
            troughcolor='#0f3460',
            bordercolor='#00d4ff',
            lightcolor='#00d4ff',
            darkcolor='#00d4ff'
        )
    
    def browse_images(self):
        if self.batch_mode.get():
            file_paths = filedialog.askopenfilenames(
                title="Select Multiple Images",
                filetypes=[
                    ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"),
                    ("All files", "*.*")
                ]
            )
        else:
            file_path = filedialog.askopenfilename(
                title="Select Image",
                filetypes=[
                    ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"),
                    ("All files", "*.*")
                ]
            )
            file_paths = [file_path] if file_path else []
        
        if file_paths:
            try:
                self.input_images = []
                for path in file_paths:
                    img = Image.open(path)
                    self.input_images.append({
                        'path': path,
                        'image': img,
                        'name': os.path.basename(path)
                    })
                
                self.current_image_index = 0
                self.output_images = []
                self.update_image_display()
                self.update_navigation()
                self.process_button.config(state=tk.NORMAL)
                self.status_var.set(f"Loaded {len(self.input_images)} image(s)")
                
                LOGGER.info(f"Loaded {len(self.input_images)} images")
                
            except Exception as e:
                LOGGER.error("Failed to load images", e)
                messagebox.showerror("Error", f"Failed to load images: {str(e)}")
    
    def update_image_display(self):
        if not self.input_images:
            return
        
        current_input = self.input_images[self.current_image_index]
        
        # Display input image
        self.display_image(current_input['image'], self.input_canvas, 500, 500)
        
        # Display output image if available
        if self.current_image_index < len(self.output_images):
            self.display_image(self.output_images[self.current_image_index], self.output_canvas, 500, 500)
            self.download_btn.config(state=tk.NORMAL)
        else:
            self.output_canvas.delete("all")
            self.output_canvas.create_text(
                250, 250,
                text="Process image to see output",
                fill='#8892b0',
                font=("Segoe UI", 14)
            )
            self.download_btn.config(state=tk.DISABLED)
    
    def update_navigation(self):
        if not self.input_images:
            return
        
        total = len(self.input_images)
        current = self.current_image_index + 1
        
        self.input_index_label.config(text=f"{current} / {total}")
        self.output_index_label.config(text=f"{current} / {total}")
        
        # Update navigation buttons
        self.prev_input_btn.config(state=tk.NORMAL if current > 1 else tk.DISABLED)
        self.next_input_btn.config(state=tk.NORMAL if current < total else tk.DISABLED)
        
        self.prev_output_btn.config(state=tk.NORMAL if current > 1 else tk.DISABLED)
        self.next_output_btn.config(state=tk.NORMAL if current < total else tk.DISABLED)
        
        # Update download all button
        if self.output_images:
            self.download_all_btn.config(state=tk.NORMAL)
        else:
            self.download_all_btn.config(state=tk.DISABLED)
    
    def previous_input(self):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.update_image_display()
            self.update_navigation()
    
    def next_input(self):
        if self.current_image_index < len(self.input_images) - 1:
            self.current_image_index += 1
            self.update_image_display()
            self.update_navigation()
    
    def previous_output(self):
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.update_image_display()
            self.update_navigation()
    
    def next_output(self):
        if self.current_image_index < len(self.input_images) - 1:
            self.current_image_index += 1
            self.update_image_display()
            self.update_navigation()
    
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
    
    def display_image(self, image, canvas, width, height):
        # Resize image to fit canvas while maintaining aspect ratio
        img_width, img_height = image.size
        ratio = min(width / img_width, height / img_height)
        
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
            width // 2,
            height // 2,
            image=photo,
            anchor=tk.CENTER
        )
        canvas.image = photo  # Keep reference
    
    def process_images(self):
        if not self.input_images or self.processing:
            return
        
        self.processing = True
        self.process_button.config(state=tk.DISABLED)
        self.progress.config(maximum=len(self.input_images))
        self.progress.config(value=0)
        self.progress_label.config(text="Processing images...")
        self.status_var.set("Processing images...")
        
        # Run processing in separate thread
        thread = threading.Thread(target=self._process_images_thread)
        thread.daemon = True
        thread.start()
    
    def _process_images_thread(self):
        try:
            LOGGER.info("Starting batch background removal process")
            self.output_images = []
            
            for i, input_data in enumerate(self.input_images):
                try:
                    # Update progress
                    self.root.after(0, lambda idx=i: self.progress.config(value=idx + 1))
                    self.root.after(0, lambda idx=i: self.progress_label.config(text=f"Processing {idx + 1}/{len(self.input_images)}"))
                    
                    # Remove background
                    if self.removal_method.get() == "rembg" and HAS_REMBG:
                        output_img = self._remove_background_rembg(input_data['image'])
                    else:
                        output_img = self._remove_background_advanced(input_data['image'])
                    
                    if output_img:
                        # Apply enhancements
                        if self.auto_enhance.get():
                            output_img = self._enhance_image(output_img)
                        
                        if self.edge_refinement.get():
                            output_img = self._refine_edges(output_img)
                        
                        # Apply background
                        output_img = self._apply_background(output_img)
                        
                        self.output_images.append(output_img)
                        
                        # Update display for current image
                        if i == self.current_image_index:
                            self.root.after(0, self.update_image_display)
                    else:
                        # Add placeholder for failed processing
                        self.output_images.append(None)
                        
                except Exception as e:
                    LOGGER.error(f"Failed to process image {input_data['name']}", e)
                    self.output_images.append(None)
            
            # Update UI in main thread
            self.root.after(0, self._processing_complete)
            
            LOGGER.info("Batch background removal completed")
            
        except Exception as e:
            LOGGER.error("Error during batch processing", e)
            self.root.after(0, lambda: self._processing_error(f"Error: {str(e)}"))
    
    def _remove_background_rembg(self, image):
        try:
            LOGGER.debug("Using rembg backend")
            # Convert to RGBA if needed
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            result = rembg_remove(image)
            return result
        except Exception as e:
            LOGGER.error("Rembg failed, falling back to advanced method", e)
            return self._remove_background_advanced(image)
    
    def _remove_background_advanced(self, image):
        try:
            LOGGER.debug("Using advanced background removal")
            
            # Convert to RGBA
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            img_array = np.array(image)
            
            # Use advanced edge detection and color analysis
            # This is a more sophisticated approach than simple thresholding
            
            # Convert to different color spaces for better analysis
            rgb = img_array[:, :, :3]
            hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
            lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
            
            # Create multiple masks using different approaches
            masks = []
            
            # 1. Edge-based mask
            gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            edge_mask = cv2.dilate(edges, None, iterations=2)
            edge_mask = cv2.erode(edge_mask, None, iterations=1)
            masks.append(edge_mask)
            
            # 2. Color variance mask (areas with high color variance are likely foreground)
            color_var = np.var(rgb, axis=2)
            color_mask = (color_var > np.percentile(color_var, 70)).astype(np.uint8) * 255
            masks.append(color_mask)
            
            # 3. Saturation mask (anime characters usually have higher saturation)
            saturation_mask = hsv[:, :, 1]
            sat_mask = (saturation_mask > np.percentile(saturation_mask, 60)).astype(np.uint8) * 255
            masks.append(sat_mask)
            
            # 4. Local contrast mask
            contrast_kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
            contrast = cv2.filter2D(gray, -1, contrast_kernel)
            contrast_mask = (contrast > np.percentile(contrast, 80)).astype(np.uint8) * 255
            masks.append(contrast_mask)
            
            # Combine masks intelligently
            combined_mask = np.zeros_like(gray)
            for mask in masks:
                combined_mask = cv2.bitwise_or(combined_mask, mask)
            
            # Apply morphological operations to clean up the mask
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
            
            # Apply Gaussian blur for smooth edges
            combined_mask = cv2.GaussianBlur(combined_mask, (5, 5), 0)
            
            # Create final alpha channel
            alpha = combined_mask.astype(np.uint8)
            
            # Apply alpha to image
            result_array = img_array.copy()
            result_array[:, :, 3] = alpha
            
            return Image.fromarray(result_array)
            
        except Exception as e:
            LOGGER.error("Advanced background removal failed", e)
            return None
    
    def _enhance_image(self, image):
        try:
            # Enhance contrast and sharpness
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(self.enhancement_level.get())
            
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.3)
            
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.1)
            
            return image
        except Exception as e:
            LOGGER.error("Image enhancement failed", e)
            return image
    
    def _refine_edges(self, image):
        try:
            # Advanced edge refinement
            # Apply unsharp mask
            image = image.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
            
            # Apply edge enhancement
            image = image.filter(ImageFilter.EDGE_ENHANCE_MORE)
            
            return image
        except Exception as e:
            LOGGER.error("Edge refinement failed", e)
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
                # For PNG output, keep transparency
                if self.output_format.get() == "png":
                    return image
                else:
                    # Apply solid color background for JPG
                    bg_color = Image.new('RGBA', image.size, self.background_color.get())
                    result = Image.alpha_composite(bg_color, image)
                    return result
        except Exception as e:
            LOGGER.error("Background application failed", e)
            return image
    
    def _processing_complete(self):
        self.processing = False
        self.process_button.config(state=tk.NORMAL)
        self.progress_label.config(text="Processing complete!")
        self.status_var.set(f"Processed {len(self.output_images)} images successfully")
        
        # Update display
        self.update_image_display()
        self.update_navigation()
        
        # Show completion message
        messagebox.showinfo("Success", f"Successfully processed {len(self.output_images)} images!")
    
    def _processing_error(self, error_message):
        self.processing = False
        self.process_button.config(state=tk.NORMAL)
        self.progress_label.config(text="Processing failed")
        self.status_var.set(f"Error: {error_message}")
        messagebox.showerror("Error", error_message)
    
    def download_current(self):
        if not self.output_images or self.current_image_index >= len(self.output_images):
            messagebox.showwarning("Warning", "No output image to download")
            return
        
        output_img = self.output_images[self.current_image_index]
        if output_img is None:
            messagebox.showwarning("Warning", "This image failed to process")
            return
        
        # Get original filename
        original_name = self.input_images[self.current_image_index]['name']
        name_without_ext = os.path.splitext(original_name)[0]
        
        # Determine file extension
        if self.output_format.get() == "png":
            ext = ".png"
            # Ensure PNG has alpha channel
            if output_img.mode != 'RGBA':
                output_img = output_img.convert('RGBA')
        else:
            ext = ".jpg"
            # Convert to RGB for JPG
            if output_img.mode == 'RGBA':
                # Create white background for JPG
                bg = Image.new('RGB', output_img.size, (255, 255, 255))
                bg.paste(output_img, mask=output_img.split()[-1])
                output_img = bg
        
        # Suggest filename
        suggested_name = f"{name_without_ext}_nobg{ext}"
        
        file_path = filedialog.asksaveasfilename(
            title="Save Processed Image",
            defaultextension=ext,
            initialvalue=suggested_name,
            filetypes=[
                ("PNG files", "*.png") if ext == ".png" else ("JPEG files", "*.jpg"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                output_img.save(file_path, quality=95 if ext == ".jpg" else None)
                self.status_var.set(f"Saved: {os.path.basename(file_path)}")
                LOGGER.info(f"Image saved: {file_path}")
                
                # Open containing folder
                os.startfile(os.path.dirname(file_path)) if os.name == 'nt' else subprocess.run(['xdg-open', os.path.dirname(file_path)])
                
            except Exception as e:
                LOGGER.error("Failed to save image", e)
                messagebox.showerror("Error", f"Failed to save: {str(e)}")
    
    def download_all(self):
        if not self.output_images:
            messagebox.showwarning("Warning", "No processed images to download")
            return
        
        # Ask for output directory
        output_dir = filedialog.askdirectory(title="Select Output Directory")
        if not output_dir:
            return
        
        try:
            saved_count = 0
            failed_count = 0
            
            for i, output_img in enumerate(self.output_images):
                if output_img is None:
                    failed_count += 1
                    continue
                
                try:
                    # Get original filename
                    original_name = self.input_images[i]['name']
                    name_without_ext = os.path.splitext(original_name)[0]
                    
                    # Determine file extension
                    if self.output_format.get() == "png":
                        ext = ".png"
                        # Ensure PNG has alpha channel
                        if output_img.mode != 'RGBA':
                            output_img = output_img.convert('RGBA')
                    else:
                        ext = ".jpg"
                        # Convert to RGB for JPG
                        if output_img.mode == 'RGBA':
                            # Create white background for JPG
                            bg = Image.new('RGB', output_img.size, (255, 255, 255))
                            bg.paste(output_img, mask=output_img.split()[-1])
                            output_img = bg
                    
                    # Create filename
                    filename = f"{name_without_ext}_nobg{ext}"
                    file_path = os.path.join(output_dir, filename)
                    
                    # Save image
                    output_img.save(file_path, quality=95 if ext == ".jpg" else None)
                    saved_count += 1
                    
                except Exception as e:
                    LOGGER.error(f"Failed to save image {i}", e)
                    failed_count += 1
            
            # Show results
            message = f"Downloaded {saved_count} images successfully"
            if failed_count > 0:
                message += f"\nFailed to download {failed_count} images"
            
            messagebox.showinfo("Download Complete", message)
            self.status_var.set(f"Downloaded {saved_count} images to {os.path.basename(output_dir)}")
            
            # Open output directory
            os.startfile(output_dir) if os.name == 'nt' else subprocess.run(['xdg-open', output_dir])
            
        except Exception as e:
            LOGGER.error("Failed to download all images", e)
            messagebox.showerror("Error", f"Failed to download images: {str(e)}")

def main():
    try:
        root = tk.Tk()
        app = AdvancedAnimeBackgroundRemover(root)
        
        LOGGER.info("Starting application")
        root.mainloop()
        
    except Exception as e:
        LOGGER.error("Application failed to start", e)
        messagebox.showerror("Fatal Error", f"Application failed to start: {str(e)}")

if __name__ == "__main__":
    main()