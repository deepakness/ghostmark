#!/usr/bin/env python3
"""
Image Watermarking Tool

This script automatically adds watermarks to images in an input folder and
saves the watermarked images to an output folder.

Features:
- Multiple watermark positions (top-left, top-right, center, bottom-left, bottom-right, etc.)
- Adjustable opacity levels (visible or subtle)
- Configurable watermark size (small, medium, large)
- Support for text and image watermarks
- Works with various image formats (JPG, PNG, TIFF, BMP, etc.)
"""

#==============================================================================
# USER CONFIGURABLE OPTIONS
# Edit these values to quickly change common settings without command-line args
#==============================================================================

# Folders (these are also the default values if not specified on command line)
INPUT_FOLDER = "input"    # Folder containing images to watermark
OUTPUT_FOLDER = "output"  # Folder where watermarked images will be saved

# Watermark settings
DEFAULT_TEXT = "@ghostmark"          # Default text to use as watermark (if no image specified)
DEFAULT_IMAGE = ""                   # Path to image file to use as watermark (leave empty to use text)
DEFAULT_POSITION = "bottom-right"    # Options: top-left, top-center, top-right, center-left, center, 
                                     #         center-right, bottom-left, bottom-center, bottom-right
DEFAULT_OPACITY = 0.8                # Value between 0.0 (invisible) and 1.0 (fully visible)
DEFAULT_SIZE = "small"               # Options: small, medium, large
DEFAULT_PIXEL_SIZE = 0               # Fixed size in pixels (0 = use relative sizing with DEFAULT_SIZE)
DEFAULT_TEXT_COLOR = "#000000"       # Text color: white, black, red, green, blue, yellow, etc.
DEFAULT_PREFIX = ""                  # Prefix added to output filenames (leave empty for no prefix)

#==============================================================================
# END OF USER CONFIGURABLE OPTIONS
#==============================================================================

import os
import sys
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

class Watermarker:
    """Handles the watermarking process for images."""
    
    # Position mappings for easier reference
    POSITIONS = {
        "top-left": (0, 0, "left", "top"),
        "top-center": (0.5, 0, "center", "top"),
        "top-right": (1, 0, "right", "top"),
        "center-left": (0, 0.5, "left", "middle"),
        "center": (0.5, 0.5, "center", "middle"),
        "center-right": (1, 0.5, "right", "middle"),
        "bottom-left": (0, 1, "left", "bottom"),
        "bottom-center": (0.5, 1, "center", "bottom"),
        "bottom-right": (1, 1, "right", "bottom"),
    }
    
    # Size factor relative to the image's smaller dimension
    SIZE_FACTORS = {
        "small": 0.05,
        "medium": 0.1,
        "large": 0.15,
    }
    
    # Common color names to RGB values
    COLORS = {
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "blue": (0, 0, 255),
        "yellow": (255, 255, 0),
        "cyan": (0, 255, 255),
        "magenta": (255, 0, 255),
        "gray": (128, 128, 128),
        "orange": (255, 165, 0),
        "purple": (128, 0, 128),
        "pink": (255, 192, 203),
    }
    
    def __init__(self, config):
        """Initialize with configuration parameters."""
        self.config = config
        
        # Setup font for text watermarks
        try:
            if sys.platform == "win32":
                font_path = "arial.ttf"
            elif sys.platform == "darwin":  # macOS
                font_path = "/System/Library/Fonts/Helvetica.ttc"
            else:  # Linux and others
                font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
                
            if not os.path.exists(font_path):
                # Fallback to a font that comes with Pillow
                font_path = ImageFont.getdefault().path
                
            self.font = ImageFont.truetype(font_path, 20)  # Base size, will be scaled later
        except Exception:
            # Use default font if custom font loading fails
            self.font = ImageFont.load_default()

    def _calculate_size(self, image):
        """Calculate appropriate watermark size based on image dimensions or pixel size."""
        # If pixel size is specified, use that
        if hasattr(self.config, 'pixel_size') and self.config.pixel_size > 0:
            return self.config.pixel_size
        
        # Otherwise use relative sizing
        min_dimension = min(image.width, image.height)
        factor = self.SIZE_FACTORS.get(self.config.size, 0.3)  # Default to medium if invalid
        return int(min_dimension * factor)

    def _calculate_position(self, image, watermark_width, watermark_height):
        """Calculate the position for the watermark based on chosen position."""
        if self.config.position not in self.POSITIONS:
            self.config.position = "bottom-right"  # Default position
            
        x_factor, y_factor, _, _ = self.POSITIONS[self.config.position]
        
        # Calculate pixel position with increased margins for edge positions
        base_margin = min(image.width, image.height) * 0.05  # Increased from 2% to 5%
        
        # Apply different margins depending on position
        if x_factor == 0 or x_factor == 1 or y_factor == 0 or y_factor == 1:
            # Edge position (top, bottom, left, right) - use larger margin
            margin = int(base_margin)
        else:
            # Center positions - use smaller margin
            margin = int(base_margin * 0.5)
        
        x = int((image.width - watermark_width) * x_factor)
        y = int((image.height - watermark_height) * y_factor)
        
        # Apply margins to avoid edge placement
        if x_factor == 0:  # Left aligned
            x = margin
        elif x_factor == 1:  # Right aligned
            x = image.width - watermark_width - margin
            
        if y_factor == 0:  # Top aligned
            y = margin
        elif y_factor == 1:  # Bottom aligned
            y = image.height - watermark_height - margin
            
        return (x, y)

    def add_text_watermark(self, image):
        """Add text watermark to an image."""
        # Create a transparent overlay for the watermark
        overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Calculate appropriate font size
        base_size = self._calculate_size(image)
        font = self.font.font_variant(size=base_size)
        
        # Calculate text size and position
        text_width, text_height = draw.textbbox((0, 0), self.config.text, font=font)[2:4]
        position = self._calculate_position(image, text_width, text_height)
        
        # Determine text color
        color = (255, 255, 255)  # Default to white
        text_color = self.config.text_color.lower()
        
        if text_color.startswith('#') and len(text_color) in (4, 7):  # Hex color code (#RGB or #RRGGBB)
            try:
                if len(text_color) == 4:  # #RGB format, convert to #RRGGBB
                    r = int(text_color[1] + text_color[1], 16)
                    g = int(text_color[2] + text_color[2], 16)
                    b = int(text_color[3] + text_color[3], 16)
                else:  # #RRGGBB format
                    r = int(text_color[1:3], 16)
                    g = int(text_color[3:5], 16)
                    b = int(text_color[5:7], 16)
                color = (r, g, b)
            except ValueError:
                # If hex parsing fails, fall back to named color or default
                color = self.COLORS.get(text_color, (255, 255, 255))
        else:
            # Use named color if available
            color = self.COLORS.get(text_color, (255, 255, 255))
        
        # Draw text on the overlay
        draw.text(position, self.config.text, font=font, fill=(*color, int(255 * self.config.opacity)))
        
        # Convert image to RGBA if it's not already
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
            
        # Combine the overlay with the original image
        watermarked = Image.alpha_composite(image, overlay)
        return watermarked
    
    def add_image_watermark(self, image):
        """Add image watermark to an image."""
        try:
            # Open and prepare the watermark image
            watermark = Image.open(self.config.image_path).convert('RGBA')
            
            # Resize watermark to appropriate size
            base_size = self._calculate_size(image)
            original_width, original_height = watermark.size
            aspect_ratio = original_width / original_height
            
            if aspect_ratio > 1:  # Width > Height
                new_width = base_size
                new_height = int(base_size / aspect_ratio)
            else:  # Height >= Width
                new_height = base_size
                new_width = int(base_size * aspect_ratio)
                
            watermark = watermark.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Adjust opacity if needed
            if self.config.opacity < 1.0:
                watermark_array = watermark.split()[3]  # Get alpha channel
                watermark_array = ImageEnhance.Brightness(watermark_array).enhance(self.config.opacity)
                watermark.putalpha(watermark_array)
            
            # Calculate position
            position = self._calculate_position(image, new_width, new_height)
            
            # Convert image to RGBA if it's not already
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
                
            # Create a new image with the same size
            watermarked = Image.new('RGBA', image.size, (0, 0, 0, 0))
            
            # Paste original image and watermark
            watermarked.paste(image, (0, 0))
            watermarked.paste(watermark, position, watermark)
            
            return watermarked
            
        except Exception as e:
            print(f"Error applying image watermark: {e}")
            return image
    
    def process_image(self, input_path):
        """Process a single image and return the watermarked result."""
        try:
            # Open the image
            image = Image.open(input_path)
            
            # Preserve original mode for output
            original_mode = image.mode
            
            # Convert to RGBA for processing
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # Apply watermark
            if self.config.text:
                watermarked = self.add_text_watermark(image)
            elif self.config.image_path:
                watermarked = self.add_image_watermark(image)
            else:
                return image  # No watermark to apply
            
            # Convert back to original mode if it wasn't RGBA
            if original_mode != 'RGBA':
                # Handle transparency properly for non-alpha formats
                if original_mode == 'RGB':
                    background = Image.new('RGB', watermarked.size, (255, 255, 255))
                    background.paste(watermarked, mask=watermarked.split()[3])
                    watermarked = background
                elif original_mode in ('L', 'P'):
                    # For grayscale or palette, we convert differently
                    watermarked = watermarked.convert(original_mode)
                
            return watermarked
            
        except Exception as e:
            print(f"Error processing image {input_path}: {e}")
            return None
    
    def process_directory(self):
        """Process all images in the input directory and save to output directory."""
        input_dir = Path(self.config.input_folder)
        output_dir = Path(self.config.output_folder)
        
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # List of supported file extensions
        supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif', '.webp'}
        
        # Track counts
        processed_count = 0
        error_count = 0
        
        # Process each image
        for input_file in input_dir.iterdir():
            if input_file.is_file() and input_file.suffix.lower() in supported_formats:
                try:
                    print(f"Processing: {input_file.name}")
                    
                    # Process the image
                    watermarked = self.process_image(input_file)
                    
                    if watermarked:
                        # Determine output path
                        if self.config.prefix:
                            output_file = output_dir / f"{self.config.prefix}_{input_file.name}"
                        else:
                            output_file = output_dir / input_file.name
                        
                        # Save the watermarked image
                        watermarked.save(output_file)
                        processed_count += 1
                        print(f"  ✓ Saved to: {output_file}")
                    else:
                        error_count += 1
                        
                except Exception as e:
                    print(f"  ✗ Error: {e}")
                    error_count += 1
        
        print(f"\nSummary: {processed_count} images processed successfully, {error_count} errors")


def main():
    """Parse arguments and execute the watermarking process."""
    parser = argparse.ArgumentParser(description="Add watermarks to images")
    
    # Folders (now with defaults)
    parser.add_argument("--input", "-i", dest="input_folder", default=INPUT_FOLDER,
                        help=f"Input folder containing images to watermark (default: '{INPUT_FOLDER}')")
    parser.add_argument("--output", "-o", dest="output_folder", default=OUTPUT_FOLDER,
                        help=f"Output folder for watermarked images (default: '{OUTPUT_FOLDER}')")
    
    # Watermark type (text or image)
    watermark_group = parser.add_mutually_exclusive_group()
    watermark_group.add_argument("--text", "-t", dest="text", default=DEFAULT_TEXT if not DEFAULT_IMAGE else None,
                              help=f"Text to use as watermark (default: '{DEFAULT_TEXT}')")
    watermark_group.add_argument("--image", "-m", dest="image_path", default=DEFAULT_IMAGE if DEFAULT_IMAGE else None,
                              help="Path to image to use as watermark")
    
    # Watermark options
    parser.add_argument("--position", "-p", dest="position", default=DEFAULT_POSITION,
                        choices=["top-left", "top-center", "top-right", 
                                 "center-left", "center", "center-right",
                                 "bottom-left", "bottom-center", "bottom-right"],
                        help=f"Position of the watermark (default: {DEFAULT_POSITION})")
    
    parser.add_argument("--opacity", "-a", dest="opacity", type=float, default=DEFAULT_OPACITY,
                        help=f"Opacity of watermark from 0.0 (invisible) to 1.0 (fully visible) (default: {DEFAULT_OPACITY})")
    
    # Size options (either relative or pixel-based)
    size_group = parser.add_mutually_exclusive_group()
    size_group.add_argument("--size", "-s", dest="size", default=DEFAULT_SIZE,
                        choices=["small", "medium", "large"],
                        help=f"Relative size of the watermark (default: {DEFAULT_SIZE})")
    size_group.add_argument("--pixel-size", "--px", dest="pixel_size", type=int, default=DEFAULT_PIXEL_SIZE,
                        help=f"Fixed size in pixels for watermark text or the longest side of image watermark (default: {DEFAULT_PIXEL_SIZE or 'auto'})")
    
    parser.add_argument("--text-color", "-c", dest="text_color", default=DEFAULT_TEXT_COLOR,
                        help=f"Color of the text watermark, either a name (e.g., 'red') or hex code (e.g., '#FF0000') (default: {DEFAULT_TEXT_COLOR})")
    
    parser.add_argument("--prefix", dest="prefix", default=DEFAULT_PREFIX,
                        help=f"Prefix for output filenames (default: {DEFAULT_PREFIX or 'none'})")
    
    # Parse and execute
    args = parser.parse_args()
    
    # If no watermark specified, use defaults
    if args.text is None and args.image_path is None:
        if DEFAULT_IMAGE:
            args.image_path = DEFAULT_IMAGE
        else:
            args.text = DEFAULT_TEXT
    
    # Validate input folder
    if not os.path.isdir(args.input_folder):
        print(f"Error: Input folder '{args.input_folder}' does not exist.")
        return
    
    # Create watermarker and process images
    watermarker = Watermarker(args)
    watermarker.process_directory()


if __name__ == "__main__":
    main() 