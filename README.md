# 🎌 Advanced Anime Background Remover AI

A powerful, user-friendly desktop application for removing backgrounds from anime and manga images using advanced AI techniques.

## ✨ Features

- **Multiple Backend Support**: Choose between fast Rembg processing or accurate ONNX Runtime inference
- **Smart Background Removal**: AI-powered algorithms specifically tuned for anime/manga artwork
- **Flexible Background Options**: 
  - Solid color backgrounds with color picker
  - Custom image backgrounds
  - Transparent output (PNG with alpha channel)
- **Image Enhancement**: 
  - Adjustable enhancement levels
  - Edge refinement for crisp results
  - Auto-enhancement for optimal quality
- **Modern Dark UI**: Beautiful, intuitive interface with anime-inspired design
- **Batch Processing**: Process multiple images efficiently
- **Real-time Preview**: See results before saving
- **Comprehensive Logging**: Detailed logs for debugging and monitoring

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Quick Install
```bash
# Clone the repository
git clone <repository-url>
cd advanced-anime-bg-remover

# Install dependencies
pip install -r requirements.txt

# Run the application
python anime_bg_remover.py
```

### Manual Installation
```bash
# Core dependencies
pip install Pillow numpy opencv-python onnxruntime

# Optional: Rembg for faster processing
pip install rembg

# Additional enhancements
pip install scikit-image
```

## 🎯 Usage

1. **Launch the Application**
   - Run `python anime_bg_remover.py`
   - The application will open with a modern dark interface

2. **Select Input Image**
   - Click "📁 Browse Image" to select your anime/manga image
   - Supported formats: PNG, JPG, JPEG, BMP, GIF, TIFF

3. **Configure Settings**
   - **Removal Method**: Choose between Rembg (fast) or ONNX Runtime (accurate)
   - **Background Options**: Select solid color or custom image background
   - **Enhancement**: Adjust enhancement level and enable edge refinement

4. **Process Image**
   - Click "🚀 Remove Background" to start processing
   - Watch the progress bar and status updates
   - Results appear in the right panel

5. **Save Results**
   - Click "💾 Save Result" to save your processed image
   - Choose format: PNG (recommended for transparency) or JPG

## 🔧 Configuration

### Logging
Logs are automatically saved to `~/.anime_bg_remover/logs/app.log`

### Performance Tuning
- **Rembg Backend**: Faster processing, good for most cases
- **ONNX Runtime**: More accurate results, slower processing
- **Edge Refinement**: Enable for crisp edges, disable for speed

## 🎨 Advanced Features

### Background Customization
- **Color Picker**: Choose any color for solid backgrounds
- **Image Backgrounds**: Use custom images as backgrounds
- **Transparency**: Export with alpha channel for compositing

### Image Enhancement
- **Contrast Adjustment**: Fine-tune image contrast (0.5x to 2.0x)
- **Sharpness Enhancement**: Improve edge definition
- **Auto-enhancement**: Automatic optimization for best results

### Processing Options
- **Edge Refinement**: Smooth and refine mask edges
- **Quality Settings**: Balance between speed and quality
- **Batch Processing**: Process multiple images sequentially

## 🐛 Troubleshooting

### Common Issues

**"Module not found" errors:**
```bash
pip install -r requirements.txt
```

**Slow processing:**
- Use Rembg backend for faster results
- Disable edge refinement
- Reduce enhancement level

**Poor quality results:**
- Enable edge refinement
- Use ONNX Runtime backend
- Increase enhancement level

**Memory issues:**
- Process smaller images
- Close other applications
- Restart the application

### Logs
Check `~/.anime_bg_remover/logs/app.log` for detailed error information.

## 🔮 Future Enhancements

- [ ] Batch processing interface
- [ ] More AI model options
- [ ] Video support
- [ ] Cloud processing integration
- [ ] Plugin system for custom backends
- [ ] Advanced masking tools
- [ ] Export to multiple formats

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

### Development Setup
```bash
# Clone and setup development environment
git clone <repository-url>
cd advanced-anime-bg-remover
pip install -r requirements.txt
pip install -r requirements-dev.txt  # if available

# Run tests
python -m pytest tests/

# Run with debug logging
python anime_bg_remover.py --debug
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Rembg**: Fast background removal library
- **ONNX Runtime**: Cross-platform inference engine
- **PIL/Pillow**: Image processing capabilities
- **OpenCV**: Computer vision algorithms
- **Tkinter**: GUI framework

## 📞 Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Wiki**: GitHub Wiki (if available)

---

**Made with ❤️ for the anime and manga community**