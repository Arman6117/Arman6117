#!/usr/bin/env python3
"""
render_heatmap_svg.py

Generates a GitHub-style animated SVG contribution heatmap.
Reads data/contributions.json and outputs contrib-heatmap.svg.
"""

import os
import json
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
IN_PATH = os.path.join(HERE, '..', 'data', 'contributions.json')
OUT_PATH = os.path.join(HERE, '..', 'contrib-heatmap.svg')

# Constants
CELL_SIZE = 12
CELL_GAP = 3
STEP = CELL_SIZE + CELL_GAP
PAD = 22
LEFT_LABEL_W = 30
TOP_LABEL_H = 20
TITLEBAR_H = 30
STATS_H = 88
BG_COLOR = '#0a0e14'
SEC_BG_COLOR = '#0d1420'
FRAME_COLOR = '#1f6feb'

PALETTE = ['#161b22', '#0e4429', '#006d32', '#26a641', '#39d353', '#69f0a0']
MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

def get_level(count):
    if count == 0: return 0
    if count <= 5: return 1
    if count <= 15: return 2
    if count <= 30: return 3
    if count <= 50: return 4
    return 5

def generate_svg():
    if not os.path.exists(IN_PATH):
        print(f"Error: {IN_PATH} not found.")
        return

    with open(IN_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    days_data = data.get('days', [])
    total_count = data.get('total', 0)
    current_streak = data.get('current_streak', 0)
    longest_streak = data.get('longest_streak', 0)
    best_day_obj = data.get('best_day', {})
    best_day = best_day_obj.get('count', 0) if best_day_obj else 0
    
    # Process dates and group into columns
    columns = []
    current_col = []
    
    if not days_data:
        return

    # Find the weekday of the first day (0=Sunday ... 6=Saturday)
    first_date = datetime.strptime(days_data[0]['date'], "%Y-%m-%d")
    first_weekday = first_date.weekday() # Monday is 0
    # Map to Sunday=0
    first_weekday = (first_weekday + 1) % 7
    
    # Pad first column
    for _ in range(first_weekday):
        current_col.append(None)
        
    for day in days_data:
        current_col.append(day)
        if len(current_col) == 7:
            columns.append(current_col)
            current_col = []
            
    # Pad last column
    if current_col:
        while len(current_col) < 7:
            current_col.append(None)
        columns.append(current_col)

    grid_cols = len(columns)
    grid_w = grid_cols * STEP
    grid_h = 7 * STEP
    
    w = PAD + LEFT_LABEL_W + grid_w + PAD
    h = PAD + TITLEBAR_H + TOP_LABEL_H + grid_h + STATS_H + PAD
    
    svg = []
    svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">')
    
    # CSS
    svg.append('<defs>')
    svg.append('<style>')
    svg.append('''
        text { font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace; font-size: 10px; }
        .bg { fill: ''' + BG_COLOR + '''; stroke: ''' + FRAME_COLOR + '''; stroke-width: 1px; rx: 8px; }
        .title { fill: #8b949e; font-size: 12px; }
        .label { fill: #8b949e; }
        .stat-value { fill: #c9d1d9; font-size: 16px; font-weight: bold; }
        .stat-label { fill: #8b949e; font-size: 11px; }
        .anim-cell { animation: cell 0.42s ease-out both; }
        @keyframes cell {
            0% { opacity: 0; transform: translateY(-6px); }
            100% { opacity: 1; transform: translateY(0); }
        }
    ''')
    svg.append('</style>')
    svg.append('</defs>')
    
    # Background
    svg.append(f'<rect class="bg" width="{w-1}" height="{h-1}" x="0.5" y="0.5" />')
    
    # Titlebar
    svg.append(f'<rect width="{w}" height="{TITLEBAR_H}" fill="{SEC_BG_COLOR}" rx="8" />')
    svg.append(f'<rect width="{w}" height="10" y="{TITLEBAR_H-10}" fill="{SEC_BG_COLOR}" />') # Square bottom
    svg.append(f'<line x1="0" y1="{TITLEBAR_H}" x2="{w}" y2="{TITLEBAR_H}" stroke="#30363d" stroke-width="1" />')
    
    # Mac dots
    dot_y = TITLEBAR_H / 2
    svg.append(f'<circle cx="20" cy="{dot_y}" r="6" fill="#ff5f57" />')
    svg.append(f'<circle cx="40" cy="{dot_y}" r="6" fill="#febc2e" />')
    svg.append(f'<circle cx="60" cy="{dot_y}" r="6" fill="#27c93f" />')
    
    svg.append(f'<text x="90" y="{dot_y+4}" class="title">arman@github:~/contributions $</text>')
    
    # Grid Translation
    grid_start_x = PAD + LEFT_LABEL_W
    grid_start_y = PAD + TITLEBAR_H + TOP_LABEL_H
    
    svg.append(f'<g transform="translate({grid_start_x}, {grid_start_y})">')
    
    # Render Month Labels & Cells
    month_labels = []
    
    for c_idx, col in enumerate(columns):
        col_x = c_idx * STEP
        
        for r_idx, day in enumerate(col):
            if day is None:
                continue
                
            row_y = r_idx * STEP
            date_obj = datetime.strptime(day['date'], "%Y-%m-%d")
            
            # Month label if this is early in the month
            if date_obj.day <= 7 and r_idx == 0:
                month_labels.append((col_x, MONTHS[date_obj.month - 1]))
                
            count = day.get('count', 0)
            lvl = get_level(count)
            color = PALETTE[lvl]
            
            delay = (c_idx * 0.018) + (r_idx * 0.045)
            
            svg.append(f'<rect class="anim-cell" x="{col_x}" y="{row_y}" width="{CELL_SIZE}" height="{CELL_SIZE}" '
                       f'fill="{color}" rx="2" style="animation-delay: {delay}s;" />')
                       
    svg.append('</g>')
    
    # Top Labels
    svg.append(f'<g transform="translate({grid_start_x}, {PAD + TITLEBAR_H + 12})">')
    for mx, mname in month_labels:
        svg.append(f'<text x="{mx}" y="0" class="label">{mname}</text>')
    svg.append('</g>')
    
    # Left Labels (Mon, Wed, Fri -> rows 1, 3, 5)
    svg.append(f'<g transform="translate({PAD}, {grid_start_y})">')
    svg.append(f'<text x="0" y="{1 * STEP + 10}" class="label">Mon</text>')
    svg.append(f'<text x="0" y="{3 * STEP + 10}" class="label">Wed</text>')
    svg.append(f'<text x="0" y="{5 * STEP + 10}" class="label">Fri</text>')
    svg.append('</g>')
    
    # Legend
    leg_x = grid_start_x + grid_w - (6 * 14 + 60)
    leg_y = grid_start_y + grid_h + 15
    svg.append(f'<g transform="translate({leg_x}, {leg_y})">')
    svg.append(f'<text x="0" y="9" class="label">Less</text>')
    for i, color in enumerate(PALETTE):
        svg.append(f'<rect x="{30 + i * 14}" y="0" width="10" height="10" fill="{color}" rx="2" />')
    svg.append(f'<text x="{30 + 6 * 14 + 5}" y="9" class="label">More</text>')
    svg.append('</g>')
    
    # Stats section
    stat_y = grid_start_y + grid_h + 40
    stat_w = grid_w + LEFT_LABEL_W
    svg.append(f'<g transform="translate({PAD}, {stat_y})">')
    
    svg.append(f'<rect x="0" y="0" width="{stat_w}" height="45" fill="{SEC_BG_COLOR}" rx="6" />')
    
    # Left stat: Total
    svg.append(f'<text x="15" y="27" fill="#c9d1d9" font-size="14" font-weight="bold">{total_count:,} contributions</text>')
    svg.append(f'<text x="160" y="27" class="stat-label">in the last year</text>')
    
    # Right stat boxes
    box_w = 120
    box_gap = 10
    start_box = stat_w - (3 * box_w + 2 * box_gap) - 15
    
    stats_data = [
        ("Current Streak", f"{current_streak} days", "#22d3ee"),
        ("Longest Streak", f"{longest_streak} days", "#39d353"),
        ("Best Day", f"{best_day} contribs", "#f2cc60")
    ]
    
    for i, (label, val, color) in enumerate(stats_data):
        bx = start_box + i * (box_w + box_gap)
        svg.append(f'<rect x="{bx}" y="5" width="{box_w}" height="35" fill="{BG_COLOR}" rx="4" />')
        svg.append(f'<rect x="{bx}" y="5" width="3" height="35" fill="{color}" rx="1" />')
        svg.append(f'<text x="{bx + 10}" y="19" class="stat-label">{label}</text>')
        svg.append(f'<text x="{bx + 10}" y="34" class="stat-value">{val}</text>')
        
    svg.append('</g>')
    
    svg.append('</svg>')
    
    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(svg))
        
    print(f"Generated {OUT_PATH}")

if __name__ == "__main__":
    generate_svg()
