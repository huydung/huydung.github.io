#!/usr/bin/env python3
"""
Logo Processor Script
Processes all logo images in the current folder:
- Keeps original aspect ratio
- Landscape logos: width = 300px (with 15px padding = 270px content)
- Portrait/Square logos: height = 200px (with 15px padding = 170px content)
- Adds 15px padding on all sides
- White rounded corner background (7px radius)
- Transparent corners
"""

from PIL import Image, ImageDraw
import os
import sys

# Configuration
OUTPUT_FOLDER = "processed_logos"
LANDSCAPE_WIDTH = 300  # Max width for landscape logos
PORTRAIT_HEIGHT = 200  # Max height for portrait/square logos
PADDING = 15  # Padding on all sides
CORNER_RADIUS = 7
BACKGROUND_COLOR = (255, 255, 255, 255)  # White

def process_logo(input_path, output_path, padding=PADDING, corner_radius=CORNER_RADIUS):
    """Process a single logo image"""
    try:
        # Open and convert to RGBA
        img = Image.open(input_path).convert("RGBA")
        print(f"  Original size: {img.width}x{img.height}")
        
        # Determine orientation and resize accordingly
        # Landscape: width > height
        # Portrait/Square: height >= width
        if img.width > img.height:
            # Landscape: fit width to LANDSCAPE_WIDTH - (padding * 2)
            target_width = LANDSCAPE_WIDTH - (padding * 2)
            ratio = target_width / img.width
            new_width = target_width
            new_height = int(img.height * ratio)
            orientation = "landscape"
        else:
            # Portrait or Square: fit height to PORTRAIT_HEIGHT - (padding * 2)
            target_height = PORTRAIT_HEIGHT - (padding * 2)
            ratio = target_height / img.height
            new_height = target_height
            new_width = int(img.width * ratio)
            orientation = "portrait/square"
        
        # Resize the image
        img = img.resize((new_width, new_height), Image.LANCZOS)
        print(f"  Orientation: {orientation}")
        print(f"  Resized to: {new_width}x{new_height}")
        
        # Calculate canvas size (resized image + padding on all sides)
        canvas_width = new_width + (padding * 2)
        canvas_height = new_height + (padding * 2)
        print(f"  Canvas size: {canvas_width}x{canvas_height} (with {padding}px padding)")
        
        # Create white background canvas
        background = Image.new('RGBA', (canvas_width, canvas_height), BACKGROUND_COLOR)
        
        # Create rounded corner mask
        mask = Image.new('L', (canvas_width, canvas_height), 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), (canvas_width-1, canvas_height-1)], corner_radius, fill=255)
        
        # Center the logo on the background (with padding)
        offset = (padding, padding)
        background.paste(img, offset, img)
        
        # Apply rounded corner mask (makes corners transparent)
        background.putalpha(mask)
        
        # Save the processed image
        background.save(output_path, 'PNG')
        print(f"  ✓ Saved to: {output_path}")
        return True
        
    except Exception as e:
        print(f"  ✗ Error processing {input_path}: {str(e)}")
        return False

def main():
    """Main function to process all logos in current directory"""
    print("=" * 60)
    print("Logo Processor - Starting...")
    print("=" * 60)
    
    # Create output folder if it doesn't exist
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
        print(f"Created output folder: {OUTPUT_FOLDER}\n")
    
    # Supported image formats
    supported_formats = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')
    
    # Find all image files in current directory
    image_files = [f for f in os.listdir('.') 
                   if f.lower().endswith(supported_formats) 
                   and os.path.isfile(f)]
    
    if not image_files:
        print("No image files found in current directory!")
        print(f"Supported formats: {', '.join(supported_formats)}")
        return
    
    print(f"Found {len(image_files)} image(s) to process:\n")
    
    # Process each image
    success_count = 0
    for idx, filename in enumerate(image_files, 1):
        print(f"[{idx}/{len(image_files)}] Processing: {filename}")
        
        input_path = filename
        output_filename = os.path.splitext(filename)[0] + '_processed.png'
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        if process_logo(input_path, output_path):
            success_count += 1
        print()
    
    # Summary
    print("=" * 60)
    print(f"Processing complete!")
    print(f"Successfully processed: {success_count}/{len(image_files)} images")
    print(f"Output folder: {OUTPUT_FOLDER}")
    print("=" * 60)

if __name__ == "__main__":
    try:
        # Check if PIL/Pillow is installed
        import PIL
        main()
    except ImportError:
        print("ERROR: Pillow library not found!")
        print("\nPlease install it first:")
        print("  pip install Pillow")
        print("\nOr if you have pip3:")
        print("  pip3 install Pillow")
        sys.exit(1)
