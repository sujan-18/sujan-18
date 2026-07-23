#!/usr/bin/env python3
"""
make_info_card.py — hand-authored neofetch-style SVG info panel.
Lines fade + slide in on a short stagger, like the panel is printing.

Usage:
    python scripts/make_info_card.py
    STATIC=1 python scripts/make_info_card.py   # frozen frame, for Quick Look
Output:
    info-card.svg
"""
import os

OUT_FILE = "info-card.svg"

WIDTH = 620
LINE_H = 24
PAD_X = 26
PAD_TOP = 34

BG = "#0d1117"
BORDER = "#30363d"
TITLE_BAR = "#161b22"
DOT_RED, DOT_YEL, DOT_GRN = "#ff5f56", "#ffbd2e", "#27c93f"

FG_HEADER = "#e6edf3"     # section headers
FG_LABEL = "#7ee787"      # key labels (green, like neofetch)
FG_TEXT = "#c9d1d9"       # values
FG_MUTE = "#8b949e"       # muted separators
FG_TITLE = "#58a6ff"

STAGGER = 0.09   # seconds between each line's fade-in
DUR = 0.35

NAME = "sujan-18"
TITLEBAR_LABEL = "sujan@github: ~"

# (kind, text) where kind selects styling
# kind: "name" | "sep" | "section" | "line"
CONTENT = [
    ("name", "Sujan Shrestha"),
    ("sep", ""),
    ("section", "Current Role"),
    ("line", "BSc (Hons) Computer Science Student"),
    ("line", "LBEF College (APU, Malaysia Affiliated)"),
    ("line", "Learning Backend & Computer Networking"),
    ("sep", ""),
    ("section", "Previous Experience"),
    ("line", "Former Branch Manager"),
    ("line", "Hackathon Participant & Team Collaborator"),
    ("line", "Python Instructor (Secondary Level)"),
    ("sep", ""),
    ("section", "Stack"),
    ("line", "Python  \u2022  Django  \u2022  FastAPI"),
    ("line", "HTML  \u2022  CSS  \u2022  JavaScript"),
    ("line", "MySQL  \u2022  PostgreSQL  \u2022  Git"),
    ("line", "Linux  \u2022  Networking  \u2022  REST APIs"),
    ("sep", ""),
    ("section", "Highlights"),
    ("line", "\u2605 1st Place \u2014 HackXLBEF Hackathon"),
    ("line", "\u2605 Built Backend & Database Projects"),
    ("line", "\u2605 Exploring Computer Networking & Systems"),
]


def escape_xml(s):
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def main():
    static = os.environ.get("STATIC") == "1"

    n_lines = len(CONTENT)
    height = PAD_TOP + n_lines * LINE_H + 26

    parts = []
    parts.append(
        f'<svg viewBox="0 0 {WIDTH} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Consolas, Menlo, \'Courier New\', monospace">'
    )

    # card background + border
    parts.append(
        f'<rect x="1" y="1" width="{WIDTH-2}" height="{height-2}" rx="10" '
        f'fill="{BG}" stroke="{BORDER}" stroke-width="1.5"/>'
    )

    # title bar
    parts.append(f'<rect x="1" y="1" width="{WIDTH-2}" height="26" rx="10" fill="{TITLE_BAR}"/>')
    parts.append(f'<rect x="1" y="14" width="{WIDTH-2}" height="13" fill="{TITLE_BAR}"/>')
    parts.append(f'<circle cx="20" cy="14" r="5.5" fill="{DOT_RED}"/>')
    parts.append(f'<circle cx="38" cy="14" r="5.5" fill="{DOT_YEL}"/>')
    parts.append(f'<circle cx="56" cy="14" r="5.5" fill="{DOT_GRN}"/>')
    parts.append(
        f'<text x="{WIDTH/2}" y="18" text-anchor="middle" font-size="11.5" '
        f'fill="{FG_MUTE}">{escape_xml(TITLEBAR_LABEL)}</text>'
    )

    y = PAD_TOP + 8
    idx = 0
    for kind, text in CONTENT:
        line_id = f"l{idx}"
        begin = idx * STAGGER

        if kind == "sep":
            y += LINE_H * 0.35
            idx += 1
            continue

        if kind == "name":
            size = 19
            fill = FG_TITLE
            weight = "bold"
            content = escape_xml(text)
        elif kind == "section":
            size = 13.5
            fill = FG_HEADER
            weight = "bold"
            content = escape_xml(text)
        else:  # "line"
            size = 13
            fill = FG_TEXT
            weight = "normal"
            content = escape_xml(text)

        opacity_attr = "1" if static else "0"
        anim = ""
        transform_anim = ""
        if not static:
            anim = (
                f'<animate attributeName="opacity" from="0" to="1" '
                f'begin="{begin:.3f}s" dur="{DUR:.3f}s" fill="freeze"/>'
            )
            transform_anim = (
                f'<animateTransform attributeName="transform" type="translate" '
                f'from="-14 0" to="0 0" begin="{begin:.3f}s" dur="{DUR:.3f}s" '
                f'fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/>'
            )

        parts.append(
            f'<g opacity="{opacity_attr}">'
            f'<text x="{PAD_X}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}">{content}'
            f'{transform_anim}'
            f'</text>'
            f'{anim}'
            f'</g>'
        )

        y += LINE_H
        idx += 1

    parts.append('</svg>')

    with open(OUT_FILE, "w") as f:
        f.write("\n".join(parts))
    print(f"Saved {OUT_FILE} ({'static' if static else 'animated'})")


if __name__ == "__main__":
    main()
