# Image Watermarking Tool

A powerful Python tool for automatically adding watermarks to images.

## Features

- Add text or image watermarks to multiple images at once
- Customizable watermark positions (top-left, top-right, center, bottom-left, bottom-right, etc.)
- Adjustable opacity levels for both subtle and visible watermarks
- Configurable watermark sizes (small, medium, large, or exact pixel size)
- Text color options (named colors or hex codes like #FF0000)
- Preserves original image quality and format
- Works with various image formats (JPG, PNG, TIFF, BMP, GIF, WebP)
- Automatically uses "input" and "output" folders by default

## Requirements

- Python 3.6 or higher
- Pillow (PIL Fork) library

## Installation

1. Install Python from [python.org](https://python.org) if not already installed
2. Install Pillow library:
   ```
   pip install Pillow
   ```

## Quick Setup

1. Create "input" and "output" folders in the same directory as the script
2. Place your images in the "input" folder
3. Run the script with your desired options:
   ```
   python watermark.py --text "Your Watermark"
   ```
4. Find your watermarked images in the "output" folder

## Direct Customization

You can customize default settings by editing the values at the top of the `watermark.py` file:

```python
# Watermark settings
DEFAULT_TEXT = "@DeepakNess"             # Default text to use as watermark
DEFAULT_POSITION = "bottom-right"        # Position of the watermark
DEFAULT_OPACITY = 0.8                    # Transparency (0.0 to 1.0)
DEFAULT_SIZE = "small"                   # Relative size (small, medium, large)
DEFAULT_PIXEL_SIZE = 0                   # Fixed size in pixels (0 = use relative sizing)
DEFAULT_TEXT_COLOR = "#000000"           # Text color (name or hex code)
```

## Usage

The script uses "input" and "output" folders by default, so you only need to specify watermark options:

```bash
# Basic usage with text watermark
python watermark.py --text "Your Watermark"

# Using an image as watermark
python watermark.py --image logo.png
```

If you need to specify different folders:

```bash
python watermark.py --text "Your Watermark" --input custom_input --output custom_output
```

### Required Arguments (one of)

- `--text`, `-t`: Text to use as watermark
- `--image`, `-m`: Path to image to use as watermark

### Optional Arguments

- `--input`, `-i`: Input folder containing images to watermark (default: "input")
- `--output`, `-o`: Output folder for watermarked images (default: "output")
- `--position`, `-p`: Position of the watermark (default: bottom-right)
  - Options: top-left, top-center, top-right, center-left, center, center-right, bottom-left, bottom-center, bottom-right
- `--opacity`, `-a`: Opacity of watermark from 0.0 (invisible) to 1.0 (fully visible) (default: 0.7)
- `--size`, `-s`: Relative size of the watermark (default: medium)
  - Options: small, medium, large
- `--pixel-size`, `--px`: Fixed size in pixels (overrides --size)
- `--text-color`, `-c`: Color for text watermark (named color or hex code like #FF0000)
- `--prefix`: Prefix for output filenames (default: none)

## Examples

### Text Watermarks

```bash
# Add black text watermark (default is now black)
python watermark.py --text "Copyright 2023"

# Add white text in top-right corner
python watermark.py --text "CONFIDENTIAL" --position top-right --text-color white

# Add large red text in center with 50% opacity
python watermark.py --text "DRAFT" --position center --text-color red --opacity 0.5 --size large

# Add text with exact 24-pixel size
python watermark.py --text "Property of Company" --pixel-size 24
```

### Image Watermarks

```bash
# Add a logo to the bottom-right of all images
python watermark.py --image ./logo.png

# Add a subtle logo to the center
python watermark.py --image ./logo.png --position center --opacity 0.3 --size small
```

### Using Hex Colors

```bash
# Add blue text (#0000FF)
python watermark.py --text "Sample" --text-color "#0000FF"

# Add custom orange text (#FF8800)
python watermark.py --text "Preview" --text-color "#FF8800"
```

## Tips

- For text watermarks, the default font depends on your operating system.
- For image watermarks, transparent PNG files work best.
- Adjust the DEFAULT_SIZE_FACTORS in the source code if you want to change the relative size options.
- When using hex colors, both #RGB and #RRGGBB formats are supported. 