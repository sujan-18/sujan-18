#!/usr/bin/env python3
"""
fetch_contributions.py — scrape a user's public contribution calendar
from https://github.com/users/<username>/contributions (no auth needed)
and write data/contributions.json with raw days + derived stats.

Usage:
    python scripts/fetch_contributions.py
Output:
    data/contributions.json
"""
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

USERNAME = "sujan-18"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT_FILE = "data/contributions.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; profile-readme-bot/1.0)"
}


def fetch_html():
    resp = requests.get(URL, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return resp.text


def parse_days(html):
    soup = BeautifulSoup(html, "html.parser")
    days = []

    # GitHub renders each day as either a <td> with data-date, or (newer
    # markup) a <table> of tool-tips + a list of <td class="ContributionCalendar-day">.
    cells = soup.select("td.ContributionCalendar-day")
    if not cells:
        # fallback: older markup used <rect class="ContributionCalendar-day">
        cells = soup.select("rect.ContributionCalendar-day")

    for cell in cells:
        date = cell.get("data-date")
        level = cell.get("data-level")
        if date is None:
            continue
        days.append({
            "date": date,
            "level": int(level) if level is not None else 0,
        })

    days.sort(key=lambda d: d["date"])
    return days


def derive_stats(days):
    if not days:
        return {}

    total = sum(1 for d in days if d["level"] and d["level"] > 0)

    # streaks are approximate: a "contribution day" is level > 0
    current_streak = 0
    longest_streak = 0
    running = 0
    for d in days:
        if d["level"] and d["level"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0
    # current streak = trailing run ending at the last day
    for d in reversed(days):
        if d["level"] and d["level"] > 0:
            current_streak += 1
        else:
            break

    monthly = {}
    for d in days:
        month = d["date"][:7]
        monthly[month] = monthly.get(month, 0) + (1 if d["level"] and d["level"] > 0 else 0)

    best_day = max(days, key=lambda d: d["level"] or 0)

    return {
        "total_contributions": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day["date"],
        "monthly_totals": monthly,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }


def main():
    html = fetch_html()
    days = parse_days(html)
    stats = derive_stats(days)

    out = {
        "username": USERNAME,
        "days": days,
        "stats": stats,
    }

    with open(OUT_FILE, "w") as f:
        json.dump(out, f, indent=2)

    print(f"Fetched {len(days)} days for {USERNAME}")
    print(f"Stats: {stats}")


if __name__ == "__main__":
    main()
