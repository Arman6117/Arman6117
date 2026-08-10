#!/usr/bin/env python3
"""
prep_photo.py

Prepares a portrait photo for ASCII art conversion.
Run once locally when you change your photo.

Three steps:
1. Remove background using `rembg` library to get an RGBA image with transparent background.
2. Boost local contrast using OpenCV's CLAHE (Contrast-Limited Adaptive Histogram Equalization).
3. Composite onto pure white RGBA background, convert to grayscale ('L' mode), and save as source-prepped.png in the repo root.

Usage:
    python scripts/prep_photo.py path/to/photo.jpg

Dependencies:
    Pillow, numpy, opencv-python, rembg
"""

import os
import sys
import numpy as np
import cv2
from PIL import Image
from rembg import remove


def main():
    """Main execution function for preparing photo for ASCII art conversion."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/prep_photo.py path/to/photo.jpg")
        print("Error: Input photo path is required.")
        sys.exit(1)

    input_path = sys.argv[1]
    if not os.path.isfile(input_path):
        print(f"Error: Input file '{input_path}' does not exist.")
        sys.exit(1)

    here = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.abspath(os.path.join(here, '..', 'source-prepped.png'))

    print(f"Loading image from '{input_path}'...")
    try:
        input_img = Image.open(input_path)
    except Exception as e:
        print(f"Error opening image '{input_path}': {e}")
        sys.exit(1)

    # Step 1: Remove background using rembg library
    print("Step 1: Removing background using rembg...")
    try:
        rembg_img = remove(input_img)
    except Exception as e:
        print(f"Error removing background with rembg: {e}")
        sys.exit(1)

    if rembg_img.mode != 'RGBA':
        rembg_img = rembg_img.convert('RGBA')

    alpha_channel = rembg_img.split()[3]

    # Step 2: Boost local contrast using OpenCV's CLAHE
    print("Step 2: Boosting local contrast with OpenCV CLAHE...")
    rgb_img = rembg_img.convert('RGB')
    gray_arr = cv2.cvtColor(np.array(rgb_img), cv2.COLOR_RGB2GRAY)

    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    clahe_arr = clahe.apply(gray_arr)

    # Step 3: Composite onto pure white background
    print("Step 3: Compositing onto pure white background...")
    clahe_rgba = Image.fromarray(clahe_arr).convert('RGBA')
    white_bg = Image.new('RGBA', rembg_img.size, (255, 255, 255, 255))
    white_bg.paste(clahe_rgba, (0, 0), mask=alpha_channel)

    final_img = white_bg.convert('L')

    # Save prepped image as source-prepped.png in the repo root
    final_img.save(output_path)
    print(f"Successfully prepped photo saved to '{output_path}'")


if __name__ == '__main__':
    main()
