# Mario-Style 2D Platformer (Python)

This is a Mario-inspired side-scrolling platformer built with `pygame`.

## Controls
- `Left/Right` or `A/D`: Move
- `Up`, `W`, or `Space`: Jump
- `R`: Reset level

## Asset Setup
Put your two attached images in:

`asset/`

Recommended names:
- `asset/background.png` (or `.jpg`, `.jpeg`, `.webp`)
- `asset/sprite.png` (or `.jpg`, `.jpeg`, `.webp`)

The game auto-detects files and will remove pink backgrounds from the sprite image so the character renders transparently.

## Run
1. Install dependency:
   ```bash
   pip3 install pygame
   ```
2. Start:
   ```bash
   python3 main.py
   ```
