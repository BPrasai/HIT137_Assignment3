# HIT137 Assignment 3 — Spot the Difference Game

## Overview
A desktop "Spot the Difference" game built with Python, Tkinter, and OpenCV.
Two images are shown side-by-side. One is the original; the other has **5 hidden
differences** generated programmatically. The player clicks the modified image to
find them all.

## Files
| File | Purpose |
|------|---------|
| `main.py` | Entry point |
| `game_app.py` | Tkinter GUI (`BaseApp` + `SpotTheDifferenceApp`) |
| `game_state.py` | Game logic & state (`GameState`) |
| `image_processor.py` | OpenCV image manipulation (`ImageProcessor`, `DifferenceRegion`) |
| `requirements.txt` | Python dependencies |

## OOP Design
| Principle | Where demonstrated |
|-----------|-------------------|
| **Encapsulation** | All classes keep internal state private; exposed via methods |
| **Constructor** | Each class has `__init__` initialising its own state |
| **Methods** | Behaviour clearly separated into named methods per class |
| **Inheritance** | `SpotTheDifferenceApp` extends `BaseApp` |
| **Polymorphism** | `SpotTheDifferenceApp` overrides `_quit` and adds game-specific behaviour |
| **Class interaction** | `SpotTheDifferenceApp` ↔ `GameState` ↔ `ImageProcessor` ↔ `DifferenceRegion` |

## Alteration Types (≥3 required, 5 implemented)
1. **Colour Shift** — HSV hue rotation in a rectangular region
2. **Blur** — Gaussian blur applied to region
3. **Brightness** — Pixel brightness lifted or lowered
4. **Invert Region** — Bitwise colour inversion (blended)
5. **Noise** — Random per-pixel noise added

## Installation
```bash
pip install opencv-python Pillow numpy
```

## Running
```bash
python main.py
```

## How to Play
1. Click **Load Image** and choose any JPG, PNG, or BMP file.
2. The original appears on the left; the modified image on the right.
3. Click on the modified (right) image where you think a difference is.
   - ✅ Correct → a **red circle** marks the difference on both images.
   - ❌ Wrong → a mistake is counted (max 3 per image).
4. Find all 5 → congratulations dialog, then load a new image.
5. Hit **Reveal All** at any time to show unfound differences in **blue**.
