# Termtris

Terminal-based Tetris written in Python using the built-in `curses` library. No external dependencies.

## Requirements

Python 3.6+ (curses is included in the standard library on macOS and Linux)

## Run

```bash
python3 termtris.py
```

## Controls

| Key | Action |
|-----|--------|
| `←` `→` | Move piece left / right |
| `↑` `X` | Rotate clockwise |
| `Z` | Rotate counterclockwise |
| `↓` | Soft drop |
| `Space` | Hard drop |
| `P` | Pause / resume |
| `R` | Restart (after game over) |
| `Q` | Quit |

## Scoring

| Lines cleared | Points (× level + 1) |
|---------------|---------------------|
| 1 | 100 |
| 2 | 300 |
| 3 | 500 |
| 4 (Tetris) | 800 |

Soft drop awards 1 point per row; hard drop awards 2 points per row.

Levels start at 0 and increase every 10 lines. Drop speed increases with each level and caps at level 10.

## Features

- All 7 standard tetrominoes (I, O, T, S, Z, J, L) in distinct colors
- 7-bag randomizer (each piece appears once per 7 spawns)
- Ghost piece showing landing position
- Next piece preview
- Wall-kick rotation, clockwise and counterclockwise
- Pause
- 11 speed levels (0–10)
- Adapts to terminal resize

## Development

The repo uses [pre-commit](https://pre-commit.com/) with [gitleaks](https://github.com/gitleaks/gitleaks) to scan for secrets before each commit:

```bash
pip install pre-commit
pre-commit install
```
