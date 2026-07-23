#!/usr/bin/env python3
"""
render_heatmap_svg.py — render data/contributions.json as a classic
53-week x 7-day calendar of rounded boxes, revealed once with a
diagonal slide-down (then freezes, no looping).

Usage:
    python scripts/render_heatmap_svg.py
Output:
    contrib-heatmap.svg
"""
import json
from datetime import datetime, timedelta

IN_FILE = "data/contributions.json"
OUT_FILE = "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32",
           "#26a641", "#39d353", "#69f0a0"]
#          none -> brightest (level 5 is a neon top end)

BOX = 11
GAP = 3
CELL = BOX + GAP
LEFT_PAD = 34
TOP_PAD = 34
BOTTOM_PAD = 46
RIGHT_PAD = 14

STAGGER = 0.012   # seconds between diagonal-neighbor boxes
DUR = 0.4

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DAY_LABELS = {1: "Mon", 3: "Wed", 5: "Fri"}


def escape_xml(s):
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_grid(days):
    """Arrange days into a week-column x weekday-row grid, GitHub-style
    (columns = weeks, Sunday-start rows 0..6)."""
    if not days:
        return [], None

    by_date = {d["date"]: d["level"] for d in days}
    last_date = datetime.strptime(days[-1]["date"], "%Y-%m-%d")

    # find the most recent Saturday to anchor the last full week,
    # and go back 52 weeks (53 columns total) from the Sunday that
    # starts the first week.
    end = last_date
    # roll forward to the Saturday ending this week (Sunday=6 in %w? use isoweekday)
    while end.weekday() != 5:  # Saturday = 5 (Mon=0..Sun=6)
        end += timedelta(days=1)

    start = end - timedelta(weeks=52) - timedelta(days=end.weekday() + 1)
    # start should land on a Sunday
    while start.weekday() != 6:  # Sunday = 6
        start -= timedelta(days=1)

    weeks = []
    cur = start
    while cur <= end:
        week = []
        for i in range(7):
            day = cur + timedelta(days=i)
            date_str = day.strftime("%Y-%m-%d")
            level = by_date.get(date_str, None)
            week.append({"date": date_str, "level": level})
        weeks.append(week)
        cur += timedelta(weeks=1)

    return weeks, start


def main():
    with open(IN_FILE) as f:
        data = json.load(f)

    days = data["days"]
    stats = data.get("stats", {})
    username = data.get("username", "")

    weeks, start = build_grid(days)
    n_weeks = len(weeks)

    width = LEFT_PAD + n_weeks * CELL + RIGHT_PAD
    height = TOP_PAD + 7 * CELL + BOTTOM_PAD

    parts = []
    parts.append(
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Consolas, Menlo, \'Courier New\', monospace">'
    )
    parts.append('<style>@keyframes noop{}</style>')

    # month labels (only when a new month starts within a week column)
    last_month = None
    for w, week in enumerate(weeks):
        first_day = datetime.strptime(week[0]["date"], "%Y-%m-%d")
        month = first_day.month
        if month != last_month and first_day.day <= 7:
            x = LEFT_PAD + w * CELL
            parts.append(
                f'<text x="{x}" y="16" font-size="10" fill="#7d8590">'
                f'{MONTH_NAMES[month-1]}</text>'
            )
            last_month = month

    # weekday labels
    for row, label in DAY_LABELS.items():
        y = TOP_PAD + row * CELL + BOX - 2
        parts.append(f'<text x="0" y="{y}" font-size="9" fill="#7d8590">{label}</text>')

    # boxes, diagonal stagger by (week + row)
    for w, week in enumerate(weeks):
        for row, day in enumerate(week):
            level = day["level"]
            x = LEFT_PAD + w * CELL
            y = TOP_PAD + row * CELL

            if level is None:
                # future/out-of-range day: draw nothing (blank)
                continue

            color = PALETTE[level] if 0 <= level < len(PALETTE) else PALETTE[0]
            begin = (w + row) * STAGGER

            parts.append(
                f'<rect x="{x}" y="{y}" width="{BOX}" height="{BOX}" rx="2.5" '
                f'fill="{color}" opacity="0">'
                f'<animate attributeName="opacity" from="0" to="1" '
                f'begin="{begin:.3f}s" dur="{DUR:.3f}s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" '
                f'from="0 -10" to="0 0" begin="{begin:.3f}s" dur="{DUR:.3f}s" '
                f'fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/>'
                f'</rect>'
            )

    # legend: Less -> More
    legend_y = height - 18
    legend_x = LEFT_PAD
    parts.append(f'<text x="{legend_x}" y="{legend_y+7}" font-size="10" fill="#7d8590">Less</text>')
    lx = legend_x + 32
    for c in PALETTE:
        parts.append(f'<rect x="{lx}" y="{legend_y}" width="{BOX}" height="{BOX}" rx="2.5" fill="{c}"/>')
        lx += CELL
    parts.append(f'<text x="{lx+4}" y="{legend_y+7}" font-size="10" fill="#7d8590">More</text>')

    # stats footer
    total = stats.get("total_contributions", 0)
    streak = stats.get("longest_streak", 0)
    footer = f"{total} contributions in the last year  \u00b7  longest streak {streak} days"
    parts.append(
        f'<text x="{width - RIGHT_PAD}" y="{legend_y+7}" font-size="10" '
        f'fill="#7d8590" text-anchor="end">{escape_xml(footer)}</text>'
    )

    parts.append('</svg>')

    with open(OUT_FILE, "w") as f:
        f.write("\n".join(parts))
    print(f"Saved {OUT_FILE} ({n_weeks} weeks x 7 days)")


if __name__ == "__main__":
    main()
