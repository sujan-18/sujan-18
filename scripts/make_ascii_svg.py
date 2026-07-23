#!/usr/bin/env python3
"""
make_ascii_svg.py — convert source-prepped.png into a monochrome ASCII
portrait SVG that "types" itself in row by row (SMIL clip-path wipe),
prints once, and freezes.

Usage:
    python scripts/make_ascii_svg.py
Output:
    avi-ascii.svg   (kept name generic below as OUT_FILE)
"""
from PIL import Image

IN_FILE = "source-prepped.png"
OUT_FILE = "sujan-ascii.svg"

COLS = 100
ROWS = 53

RAMP = " .`:-=+*cs#%@"   # bright (sparse) -> dark (dense)

FONT_SIZE = 9
CHAR_W = FONT_SIZE * 0.6
LINE_H = FONT_SIZE * 1.0

FILL_COLOR = "#9fb0c3"       # light gray-blue, monochrome
BG_COLOR = "transparent"

ROW_STAGGER = 0.045          # seconds between each row starting to type
ROW_DURATION = 0.28          # seconds for a row to fully wipe in


def image_to_ascii_rows(path, cols, rows):
    img = Image.open(path).convert("L")
    # character cells are taller than wide, so squash vertically when sampling
    img = img.resize((cols, rows))
    pixels = list(img.getdata())

    ramp_len = len(RAMP)
    ascii_rows = []
    for r in range(rows):
        row_chars = []
        for c in range(cols):
            brightness = pixels[r * cols + c]  # 0=black .. 255=white
            idx = int((255 - brightness) / 255 * (ramp_len - 1))
            row_chars.append(RAMP[idx])
        ascii_rows.append("".join(row_chars))
    return ascii_rows


def escape_xml(s):
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_svg(ascii_rows):
    width = COLS * CHAR_W + 20
    height = ROWS * LINE_H + 20

    svg_parts = []
    svg_parts.append(
        f'<svg viewBox="0 0 {width:.0f} {height:.0f}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Consolas, Menlo, \'Courier New\', monospace" font-size="{FONT_SIZE}">'
    )
    svg_parts.append(
        f'<rect width="100%" height="100%" fill="{BG_COLOR}"/>'
    )
    svg_parts.append(
        f'<style>'
        f'.row {{ fill: {FILL_COLOR}; white-space: pre; }}'
        f'.cursor {{ fill: {FILL_COLOR}; }}'
        f'</style>'
    )

    for r, row_text in enumerate(ascii_rows):
        # skip fully-blank rows quickly (no need to animate empty space)
        stripped = row_text.rstrip()
        row_len = len(row_text)
        y = 15 + r * LINE_H
        start_time = r * ROW_STAGGER
        end_time = start_time + ROW_DURATION
        row_width_px = row_len * CHAR_W

        text_escaped = escape_xml(row_text)

        group_id = f"row{r}"
        clip_id = f"clip{r}"

        # clipPath rectangle animates its width from 0 -> full row width
        svg_parts.append(f'<clipPath id="{clip_id}">')
        svg_parts.append(
            f'<rect x="10" y="{y - FONT_SIZE:.1f}" width="0" height="{LINE_H:.1f}">'
            f'<animate attributeName="width" from="0" to="{row_width_px:.1f}" '
            f'begin="{start_time:.3f}s" dur="{ROW_DURATION:.3f}s" '
            f'fill="freeze" calcMode="linear"/>'
            f'</rect>'
        )
        svg_parts.append('</clipPath>')

        svg_parts.append(f'<g clip-path="url(#{clip_id})">')
        svg_parts.append(
            f'<text class="row" x="10" y="{y:.1f}" xml:space="preserve">{text_escaped}</text>'
        )
        svg_parts.append('</g>')

        # small block cursor riding the wipe edge, fades out once row is done
        if stripped:
            svg_parts.append(
                f'<rect class="cursor" x="10" y="{y - FONT_SIZE:.1f}" '
                f'width="{CHAR_W:.1f}" height="{LINE_H:.1f}" opacity="0">'
                f'<animate attributeName="x" from="10" to="{10 + row_width_px:.1f}" '
                f'begin="{start_time:.3f}s" dur="{ROW_DURATION:.3f}s" fill="freeze" calcMode="linear"/>'
                f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.01;0.9;1" '
                f'begin="{start_time:.3f}s" dur="{ROW_DURATION:.3f}s" fill="freeze"/>'
                f'</rect>'
            )

    svg_parts.append('</svg>')
    return "\n".join(svg_parts)


def main():
    ascii_rows = image_to_ascii_rows(IN_FILE, COLS, ROWS)
    svg = build_svg(ascii_rows)
    with open(OUT_FILE, "w") as f:
        f.write(svg)
    print(f"Saved {OUT_FILE} ({COLS}x{ROWS} chars)")


if __name__ == "__main__":
    main()
