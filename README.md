# Mario-Style 2D Platformer

This repo now includes:
- Web version for GitHub Pages: `index.html` + `game.js`
- Python desktop version: `main.py` (pygame)

## Controls
- `Left/Right` or `A/D`: Move
- `Up`, `W`, or `Space`: Jump
- `R`: Reset

## Asset Setup
Put your files in:
- `asset/background.png`
- `asset/sprite.png`

The web game removes pink sprite background color at runtime.

## Play On GitHub Pages
1. Open your repo: `https://github.com/TESVM/mario_platformer`
2. Go to `Settings` -> `Pages`
3. Under `Build and deployment`:
   - `Source`: `Deploy from a branch`
   - `Branch`: `main`
   - `Folder`: `/ (root)`
4. Save
5. Wait about 1 minute, then open:
   - `https://tesvm.github.io/mario_platformer/`

## Run Desktop Python Version
```bash
cd /Users/tes/mario_platformer
pip3 install -r requirements.txt
python3 main.py
```
