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
| `↑` | Rotate piece |
| `↓` | Soft drop |
| `Space` | Hard drop |
| `R` | Restart (after game over) |
| `Q` | Quit |

## Scoring

| Lines cleared | Points (× level) |
|---------------|-----------------|
| 1 | 100 |
| 2 | 300 |
| 3 | 500 |
| 4 (Tetris) | 800 |

Soft drop awards 1 point per row; hard drop awards 2 points per row.

Speed increases every 10 lines, up to level 10.

## Features

- All 7 standard tetrominoes (I, O, T, S, Z, J, L) in distinct colors
- Ghost piece showing landing position
- Next piece preview
- Wall-kick rotation
- 10 difficulty levels
