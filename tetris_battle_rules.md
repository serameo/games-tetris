# Tetris Battle - Game Rules

## 1. Board

- Play field size: **9 columns wide x 18 rows tall**, per player.
- In two-player mode, two boards are shown side by side (split-screen)
  in a single window.

## 2. Modes

- **Single player**: one board, one set of controls.
- **Two player**: two boards side by side, each player controls their
  own board independently and simultaneously.

## 3. Controls

### Single player
| Key | Action |
|---|---|
| Up | Rotate the active Tetrimino |
| Left | Move the Tetrimino left |
| Right | Move the Tetrimino right |
| Down | Move the Tetrimino down (soft drop) |

### Two player (Player 2)
| Key | Action |
|---|---|
| W | Rotate the active Tetrimino |
| A | Move the Tetrimino left |
| D | Move the Tetrimino right |
| S | Move the Tetrimino down (soft drop) |

(Player 1 keeps the Arrow-key controls above in two-player mode.)

## 4. Tetriminoes

Each block is rendered as a shiny metal panel. Seven pieces, matching
classic Tetris colors:

| Piece | Color | Orientations |
|---|---|---|
| O | Yellow | 1 (square, no rotation) |
| I | Cyan | 2 (horizontal, vertical) |
| S | Green | 2 (horizontal, vertical) |
| Z | Red | 2 (horizontal, vertical) |
| T | Purple | 4 (up, down, left, right pointing) |
| L | Blue | 4 (four rotations) |
| J | Orange | 4 (four rotations) |

Shapes (as given in the original spec):

```
O:
XX
XX

I (horizontal):        I (vertical):
XXXX                   X
                        X
                        X
                        X

S (horizontal):         S (vertical):
 XX                     X
XX                      XX
                          X

Z (horizontal):         Z (vertical):
XX                       X
 XX                     XX
                        X

T (four rotations):
XXX      X       X        X
 X       XX      XXX     XX
         X                X

L (four rotations):
X        XXX     XX          X
X        X         X      XXX
XX                  X

J (four rotations):
 X       X        XX       XXX
 X       XXX      X          X
XX                 X
```

## 5. Falling Speed

- Level 1: the active Tetrimino drops one row every **1.00 second**.
- Each level above 1 is **0.01 seconds faster** than the previous level
  (i.e. drop interval = `1.00 - 0.01 * (level - 1)` seconds).

## 6. Scoring & Leveling

- Line-clear scoring:

| Lines cleared at once | Points |
|---|---|
| 1 | 1 |
| 2 | 3 |
| 3 | 5 |
| 4 | 7 |

- Leveling: Level 1 requires **30 points** to advance to Level 2. Each
  subsequent level's point requirement is the previous level's
  requirement **+ 10**. (Level 2 = 40, Level 3 = 50, ...). These values
  are configurable.
- **Level 30 is the final level.** Reaching level 30's score requirement
  wins the game.

## 7. Win / Lose Conditions

- **Loss**: a new Tetrimino cannot be placed on the board when it spawns
  (it overlaps an already-locked Tetrimino)  -  the board is "blocked out."
- **Win**: reaching the Level 30 score requirement.
- **Single player**: the outcome (win or loss) follows the conditions
  above directly.
- **Two player**: if one player loses by the block-out condition, the
  other player is declared the winner (regardless of their own score/level
  at that moment).
