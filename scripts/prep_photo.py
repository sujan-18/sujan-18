#!/usr/bin/env python3
"""
prep_photo.py — turn a normal photo into a clean, high-contrast,
background-removed grayscale image ready for ASCII conversion.

Usage:
    python scripts/prep_photo.py source-photo.jpg
Output:
    source-prepped.png
"""
import sys
import io
import numpy as np
import cv2
from PIL import Image
from rembg import remove


def prep(input_path: str, output_path: str = "source-prepped.png"):
    with open(input_path, "rb") as f:
        input_bytes = f.read()

    # 1. Remove background -> RGBA with subject isolated
    print("Removing background...")
    result_bytes = remove(input_bytes)
    subject = Image.open(io.BytesIO(result_bytes)).convert("RGBA")

    # 2. Composite onto pure white so background maps to blank end of ramp
    white_bg = Image.new("RGBA", subject.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, subject).convert("RGB")

    # 3. Boost local contrast with CLAHE
    print("Boosting local contrast (CLAHE)...")
    arr = np.array(composited)
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    contrasted = clahe.apply(gray)

    out = Image.fromarray(contrasted)
    out.save(output_path)
    print(f"Saved {output_path} ({out.size[0]}x{out.size[1]})")


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "source-photo.jpg"
    prep(src)
