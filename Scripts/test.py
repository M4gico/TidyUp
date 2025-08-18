import sys
from typing import Optional
from PIL import Image
import ctypes

from CustomObjects.Application import Application
from CustomObjects.ExtractIconExe import extract_icon, IconSize

path_exe = r"C:\Program Files\Zen Browser\zen.exe"
app = Application(path_exe)

icon = extract_icon(path_exe, IconSize.SMALL)

print(icon)


def visualize_icon(path_exe, size=IconSize.SMALL):
    """Extract and display icon from executable"""
    # Extract the icon data
    icon_data = extract_icon(path_exe, size)

    # Get dimensions based on size
    if size == IconSize.SMALL:
        width, height = 16, 16
    else:  # LARGE
        width, height = 32, 32

    # Convert ctypes array to bytes
    raw_data = ctypes.string_at(icon_data, width * height * 4)

    # Create PIL Image from raw BGRA data
    # Windows bitmaps use BGRA format, so we need to convert to RGBA
    img = Image.frombytes('RGBA', (width, height), raw_data, 'raw', 'BGRA')

    # Display the image
    img.show()

    # Print analysis table
    print(f"\n=== Icon Analysis ===")
    print(f"Size: {width}x{height} pixels")
    print(f"Format: BGRA (32-bit)")
    print(f"Data length: {len(raw_data)} bytes")
    print(f"Expected length: {width * height * 4} bytes")

    # Sample pixel analysis
    print(f"\n=== Pixel Data Sample ===")
    for y in range(min(4, height)):
        row_data = []
        for x in range(min(4, width)):
            pixel_offset = (y * width + x) * 4
            b = raw_data[pixel_offset]
            g = raw_data[pixel_offset + 1]
            r = raw_data[pixel_offset + 2]
            a = raw_data[pixel_offset + 3]
            row_data.append(f"({r:02x},{g:02x},{b:02x},{a:02x})")
        print(f"Row {y}: {' '.join(row_data)}")

    return img


# Usage
path_exe = r"C:\Program Files\Zen Browser\zen.exe"
image = visualize_icon(path_exe, IconSize.SMALL)