#!/usr/bin/env python3
"""
Convert a portrait photo into a monochrome ASCII-art SVG that 'types' itself in like a terminal.

Usage:
    python make_ascii_svg.py [source_image] [output_svg]

Environment Variables:
    STATIC=1    Disable animation and render the full ASCII art statically.
"""

import os
import sys
import html
try:
    from PIL import Image, ImageEnhance, ImageFilter
except ImportError:
    print("Error: Pillow is required. Please install it using 'pip install Pillow'")
    sys.exit(1)

# Config
COLS = 100
ROWS = 53
CELL_W = 8
CELL_H = 15

PAD = 20
TITLEBAR_H = 30
STATUS_H = 30

ART_W = COLS * CELL_W
ART_H = ROWS * CELL_H

WIDTH = ART_W + PAD * 2
HEIGHT = TITLEBAR_H + ART_H + STATUS_H + PAD

# Colors
BG_COLOR = "#0d1117"
SEC_BG_COLOR = "#111722"
FRAME_COLOR = "#30363d"
TITLE_COLOR = "#7d8590"
INK_COLOR = "#c9d1d9"

# Image processing config
SHARPEN = True
BRIGHTNESS = 1.0
CONTRAST = 1.05
GAMMA = 1.18
WHITE_FLOOR = 0.80

# ASCII Ramp (bright to dark)
RAMP = " .`:-=+*cs#%@"

# Animation config
ROW_DUR = 0.11
STAGGER = 0.11

HERE = os.path.dirname(os.path.abspath(__file__))

def process_image(img_path):
    try:
        img = Image.open(img_path).convert('L')
    except Exception as e:
        print(f"Error opening image '{img_path}': {e}")
        sys.exit(1)
        
    if SHARPEN:
        img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
        
    img = ImageEnhance.Brightness(img).enhance(BRIGHTNESS)
    img = ImageEnhance.Contrast(img).enhance(CONTRAST)
    
    img = img.resize((COLS, ROWS), Image.Resampling.LANCZOS)
    
    return img

def get_char(lum):
    if lum >= WHITE_FLOOR:
        return " "
    
    # Apply gamma
    lum = lum ** (1.0 / GAMMA)
    
    idx = int((1.0 - lum) * (len(RAMP) - 1))
    # clamp
    idx = max(0, min(len(RAMP) - 1, idx))
    return RAMP[idx]

def generate_svg(img_path, out_path, static=False):
    img = process_image(img_path)
    pixels = img.load()
    
    ascii_rows = []
    for y in range(ROWS):
        row_chars = []
        for x in range(COLS):
            lum = pixels[x, y] / 255.0
            row_chars.append(get_char(lum))
        ascii_rows.append("".join(row_chars))
        
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">')
    svg.append('  <style>')
    svg.append('    .text { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; font-size: 14px; fill: ' + INK_COLOR + '; white-space: pre; }')
    svg.append('    .title { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 13px; fill: ' + TITLE_COLOR + '; }')
    svg.append('  </style>')
    
    # Background
    svg.append(f'  <rect width="100%" height="100%" fill="{BG_COLOR}" rx="8"/>')
    svg.append(f'  <rect width="100%" height="{TITLEBAR_H}" fill="{SEC_BG_COLOR}" rx="8"/>')
    svg.append(f'  <path d="M0 {TITLEBAR_H} L0 {TITLEBAR_H-8} Q0 0 8 0 L{WIDTH-8} 0 Q{WIDTH} 0 {WIDTH} 8 L{WIDTH} {TITLEBAR_H} Z" fill="{SEC_BG_COLOR}"/>')
    svg.append(f'  <rect width="100%" height="1" y="{TITLEBAR_H}" fill="{FRAME_COLOR}"/>')
    
    # Traffic lights
    svg.append('  <circle cx="20" cy="15" r="6" fill="#ff5f56"/>')
    svg.append('  <circle cx="40" cy="15" r="6" fill="#ffbd2e"/>')
    svg.append('  <circle cx="60" cy="15" r="6" fill="#27c93f"/>')
    
    # Title
    svg.append(f'  <text x="{WIDTH//2}" y="20" class="title" text-anchor="middle">portrait.sh — arman</text>')
    
    # Art area
    start_y = TITLEBAR_H + PAD
    
    for i, row in enumerate(ascii_rows):
        y_pos = start_y + (i * CELL_H)
        row_escaped = html.escape(row)
        
        if static:
            svg.append(f'  <text x="{PAD}" y="{y_pos + 12}" class="text" xml:space="preserve">{row_escaped}</text>')
        else:
            begin_time = i * STAGGER
            clip_id = f"clip_{i}"
            
            # Clip path animating from left to right
            svg.append(f'  <clipPath id="{clip_id}">')
            svg.append(f'    <rect x="{PAD}" y="{y_pos}" width="0" height="{CELL_H}">')
            svg.append(f'      <animate attributeName="width" from="0" to="{ART_W}" begin="{begin_time}s" dur="{ROW_DUR}s" fill="freeze" />')
            svg.append('    </rect>')
            svg.append('  </clipPath>')
            
            svg.append(f'  <g clip-path="url(#{clip_id})">')
            svg.append(f'    <text x="{PAD}" y="{y_pos + 12}" class="text" xml:space="preserve">{row_escaped}</text>')
            svg.append('  </g>')
            
            # Cursor
            svg.append(f'  <rect x="{PAD}" y="{y_pos + 2}" width="8" height="{CELL_H-4}" fill="{INK_COLOR}" opacity="0">')
            svg.append(f'    <animate attributeName="x" from="{PAD}" to="{PAD + ART_W}" begin="{begin_time}s" dur="{ROW_DUR}s" fill="freeze" />')
            # The cursor should be visible during the wipe, then disappear
            svg.append(f'    <set attributeName="opacity" to="1" begin="{begin_time}s" />')
            svg.append(f'    <set attributeName="opacity" to="0" begin="{begin_time + ROW_DUR}s" />')
            svg.append('  </rect>')
            
    # Status bar
    status_y = start_y + ART_H + 20
    svg.append(f'  <rect width="100%" height="1" y="{start_y + ART_H}" fill="{FRAME_COLOR}"/>')
    svg.append(f'  <text x="{PAD}" y="{status_y}" class="title">100×53 · monochrome</text>')
    
    svg.append('</svg>')
    
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(svg))
        print(f"Successfully generated {out_path}")
    except Exception as e:
        print(f"Error writing to {out_path}: {e}")
        sys.exit(1)

def main():
    default_src = os.path.join(HERE, '..', 'source-prepped.png')
    default_out = os.path.join(HERE, '..', 'arman-ascii.svg')
    
    src = sys.argv[1] if len(sys.argv) > 1 else default_src
    out = sys.argv[2] if len(sys.argv) > 2 else default_out
    
    if not os.path.exists(src):
        print(f"Error: Source image not found at '{src}'.")
        sys.exit(1)
        
    is_static = os.environ.get("STATIC", "0") == "1"
    
    generate_svg(src, out, is_static)

if __name__ == "__main__":
    main()
