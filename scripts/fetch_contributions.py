#!/usr/bin/env python3
"""
fetch_contributions.py

Scrapes GitHub's public contribution calendar HTML for a specified user,
parses daily contribution counts from tooltip data, calculates statistics
(total contributions, current streak, longest streak, best day), and writes
the result to data/contributions.json.

Usage:
    python fetch_contributions.py
    GH_PROFILE_USER=otheruser python fetch_contributions.py
"""

from datetime import datetime, timedelta
import json
import os
import re
import sys
import bs4
import requests


def parse_count_from_tooltip(text: str) -> int:
    """
    Parses contribution count from tooltip text.
    
    Examples:
        - "5 contributions on August 10, 2023" -> 5
        - "1 contribution on August 10, 2023" -> 1
        - "No contributions on August 10, 2023" -> 0
    """
    if not text:
        return 0
    text_lower = text.lower().strip()
    if "no contribution" in text_lower or text_lower.startswith("no "):
        return 0
    match = re.search(r'(\d+)\s+contribution', text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    match_num = re.search(r'\b(\d+)\b', text)
    if match_num:
        return int(match_num.group(1))
    return 0


def fetch_contributions(username: str) -> dict:
    """
    Fetches the GitHub contribution calendar HTML for `username` and returns
    structured contribution statistics.
    """
    url = f"https://github.com/users/{username}/contributions"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()

    soup = bs4.BeautifulSoup(response.text, "html.parser")

    # Map tooltip 'for' attribute (referencing td id) to text content
    tooltip_map = {}
    for tooltip in soup.find_all(["tool-tip", "tool-tip-element"]):
        for_id = tooltip.get("for")
        if for_id:
            tooltip_map[for_id] = tooltip.get_text(strip=True)

    days_data = []

    # Find day cells: td elements with class ContributionCalendar-day or data-date attribute
    day_cells = soup.find_all("td", class_=re.compile(r"ContributionCalendar-day"))
    if not day_cells:
        day_cells = soup.find_all("td", attrs={"data-date": True})

    for cell in day_cells:
        date_str = cell.get("data-date")
        if not date_str:
            continue

        cell_id = cell.get("id")
        tooltip_text = ""

        if cell_id and cell_id in tooltip_map:
            tooltip_text = tooltip_map[cell_id]
        else:
            # Fallback checks: child tool-tip or aria-label attribute
            child_tooltip = cell.find(["tool-tip", "tool-tip-element"])
            if child_tooltip:
                tooltip_text = child_tooltip.get_text(strip=True)
            elif cell.get("aria-label"):
                tooltip_text = cell.get("aria-label")

        count = parse_count_from_tooltip(tooltip_text)

        # Additional fallback if cell has explicit data-count attribute
        if count == 0 and cell.get("data-count"):
            try:
                count = int(cell.get("data-count"))
            except ValueError:
                pass

        days_data.append({"date": date_str, "count": count})

    # Sort days array by date ascending
    days_sorted = sorted(days_data, key=lambda x: x["date"])

    # Total contributions
    total_contributions = sum(item["count"] for item in days_sorted)

    # Best day
    best_day = None
    if days_sorted:
        best_item = max(days_sorted, key=lambda x: x["count"])
        best_day = {"date": best_item["date"], "count": best_item["count"]}

    # Date mapping for streak calculations
    date_map = {}
    for item in days_sorted:
        try:
            dt = datetime.strptime(item["date"], "%Y-%m-%d").date()
            date_map[dt] = item["count"]
        except ValueError:
            continue

    # Longest streak calculation
    longest_streak = 0
    current_seq = 0
    prev_date = None

    for dt in sorted(date_map.keys()):
        cnt = date_map[dt]
        if cnt > 0:
            if prev_date is not None and dt == prev_date + timedelta(days=1):
                current_seq += 1
            else:
                current_seq = 1
            if current_seq > longest_streak:
                longest_streak = current_seq
        else:
            current_seq = 0
        prev_date = dt

    # Current streak calculation (consecutive days with contributions ending today or latest available date)
    today = datetime.now().date()
    start_date = today
    if start_date not in date_map and date_map:
        start_date = max(date_map.keys())

    check_date = start_date
    current_streak = 0

    # If start_date has 0 contributions, check if yesterday (start_date - 1 day) had contributions
    if date_map.get(check_date, 0) == 0:
        check_date = check_date - timedelta(days=1)

    while check_date in date_map and date_map[check_date] > 0:
        current_streak += 1
        check_date -= timedelta(days=1)

    return {
        "days": days_sorted,
        "total": total_contributions,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
    }


def main():
    username = os.environ.get("GH_PROFILE_USER", "Arman6117")
    out_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "data", "contributions.json")
    )
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    print(f"Fetching contribution calendar for GitHub user '{username}'...")
    try:
        data = fetch_contributions(username)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Successfully wrote contribution data to '{out_path}'.")
    except Exception as e:
        print(f"Error fetching contributions for '{username}': {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
