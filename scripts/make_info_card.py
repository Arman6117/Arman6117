#!/usr/bin/env python3
"""
Generates a neofetch-style info card SVG that shows developer information in a terminal-like panel.
"""

import os
import html

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(HERE, '..', 'info-card.svg')
STATIC = os.environ.get('STATIC') == '1'

WIDTH = 490
HEIGHT = 380

COLORS = [
    "#22d3ee", # cyan
    "#39d353", # green
    "#a78bfa", # violet
    "#f2cc60", # gold
]

INFO_LINES = [
    ("Now", "Full-Stack Developer (MERN + Next.js)"),
    ("Edu", "Final-Year BS CS, Ahmednagar"),
    ("Stack", "React \u00b7 Next.js \u00b7 Node \u00b7 Express \u00b7 MongoDB"),
    ("Building", "NexusOS \u2014 browser-based OS"),
    ("Shipped", "RAG AI Doc Assistant (Gemini + Qdrant)"),
    ("Freelance", "PhD consulting site \u2014 40+ pages"),
    ("Goal", "Postgrad study in Japan"),
    ("Fun", "Anime \u00b7 Space \u00b7 Drawing \u00b7 Gaming"),
]

COLOR_BAR = [
    "#282c34", "#e06c75", "#98c379", "#e5c07b", 
    "#61afef", "#c678dd", "#56b6c2", "#abb2bf"
]

def main():
    svg_elements = []
    
    # CSS
    style = """
    .font { font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace; }
    .bg { fill: #0d1117; }
    .panel { fill: #111722; stroke: #30363d; stroke-width: 1px; }
    .titlebar { fill: #161b22; stroke: #30363d; stroke-width: 1px; }
    .title { fill: #7d8590; font-size: 13px; }
    .val { fill: #e6edf3; font-size: 14px; }
    .sep { fill: #30363d; font-size: 14px; }
    """
    
    if not STATIC:
        style += """
        .line { opacity: 0; animation: fade-in 0.35s ease-out forwards; }
        @keyframes fade-in {
            0% { opacity: 0; transform: translateY(8px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        """
    else:
        style += """
        .line { opacity: 1; }
        """
        
    svg_elements.append(f'<defs><style>{style}</style></defs>')
    
    # Background
    svg_elements.append(f'<rect width="{WIDTH}" height="{HEIGHT}" rx="8" class="panel" />')
    
    # Titlebar
    svg_elements.append(f'<path d="M 0 8 Q 0 0 8 0 L {WIDTH-8} 0 Q {WIDTH} 0 {WIDTH} 8 L {WIDTH} 30 L 0 30 Z" class="titlebar" />')
    
    # Traffic lights
    svg_elements.append('<circle cx="16" cy="15" r="5" fill="#ff5f57" />')
    svg_elements.append('<circle cx="32" cy="15" r="5" fill="#febc2e" />')
    svg_elements.append('<circle cx="48" cy="15" r="5" fill="#27c93f" />')
    
    # Title text
    svg_elements.append(f'<text x="{WIDTH/2}" y="20" class="font title" text-anchor="middle">arman@github:~/info $ neofetch</text>')
    
    # Content area (starting below titlebar)
    # 20px padding from the left edge
    x_offset = 20
    y_offset = 65
    
    # Header
    svg_elements.append(f'<g class="line" style="animation-delay: 0.12s"><text x="{x_offset}" y="{y_offset}" class="font val" fill="#22d3ee" font-weight="bold">arman@github</text></g>')
    y_offset += 20
    svg_elements.append(f'<g class="line" style="animation-delay: 0.24s"><text x="{x_offset}" y="{y_offset}" class="font sep">──────────────</text></g>')
    y_offset += 25
    
    # Info lines
    max_key_len = max(len(k) for k, _ in INFO_LINES)
    # Each monospace character is about 8.4px wide at 14px size. 
    # Let's just use fixed pixel offsets.
    value_x = x_offset + (max_key_len * 9) + 15
    
    for i, (key, val) in enumerate(INFO_LINES):
        delay = 0.36 + (i * 0.12)
        color = COLORS[i % len(COLORS)]
        
        g_style = f'animation-delay: {delay}s' if not STATIC else ''
        
        svg_elements.append(f'<g class="line" style="{g_style}">')
        svg_elements.append(f'  <text x="{x_offset}" y="{y_offset}" class="font" fill="{color}" font-weight="bold" font-size="14px">{html.escape(key)}</text>')
        svg_elements.append(f'  <text x="{value_x}" y="{y_offset}" class="font val">{html.escape(val)}</text>')
        svg_elements.append('</g>')
        
        y_offset += 24
    
    # Color bar
    y_offset += 20
    sq_size = 14
    gap = 6
    total_w = len(COLOR_BAR) * sq_size + (len(COLOR_BAR) - 1) * gap
    bar_x = (WIDTH - total_w) / 2
    
    delay = 0.36 + (len(INFO_LINES) * 0.12)
    g_style = f'animation-delay: {delay}s' if not STATIC else ''
    
    svg_elements.append(f'<g class="line" style="{g_style}">')
    for i, color in enumerate(COLOR_BAR):
        cx = bar_x + i * (sq_size + gap)
        svg_elements.append(f'  <rect x="{cx}" y="{y_offset}" width="{sq_size}" height="{sq_size}" fill="{color}" rx="2" />')
    svg_elements.append('</g>')
    
    svg_content = f"""<svg width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" fill="none" xmlns="http://www.w3.org/2000/svg">
{''.join(svg_elements)}
</svg>"""

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        f.write(svg_content)
        
    print(f"Created SVG at {OUT_PATH}")

if __name__ == '__main__':
    main()
