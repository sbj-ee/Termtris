#!/usr/bin/env python3
"""Termtris — terminal Tetris using curses."""

import curses
import random
import time

# Piece shapes: each is a list of (row, col) offsets from the pivot
PIECES = {
    'I': [[(0,0),(0,1),(0,2),(0,3)], [(0,2),(1,2),(2,2),(3,2)],
          [(3,0),(3,1),(3,2),(3,3)], [(0,1),(1,1),(2,1),(3,1)]],
    'O': [[(0,0),(0,1),(1,0),(1,1)]]*4,
    'T': [[(0,0),(0,1),(0,2),(1,1)], [(0,1),(1,1),(2,1),(1,2)],
          [(1,0),(1,1),(1,2),(0,1)], [(0,0),(1,0),(2,0),(1,1)]],
    'S': [[(0,1),(0,2),(1,0),(1,1)], [(0,0),(1,0),(1,1),(2,1)],
          [(0,1),(0,2),(1,0),(1,1)], [(0,0),(1,0),(1,1),(2,1)]],
    'Z': [[(0,0),(0,1),(1,1),(1,2)], [(0,1),(1,0),(1,1),(2,0)],
          [(0,0),(0,1),(1,1),(1,2)], [(0,1),(1,0),(1,1),(2,0)]],
    'J': [[(0,0),(1,0),(1,1),(1,2)], [(0,1),(0,2),(1,1),(2,1)],
          [(1,0),(1,1),(1,2),(2,2)], [(0,1),(1,1),(2,0),(2,1)]],
    'L': [[(0,2),(1,0),(1,1),(1,2)], [(0,1),(1,1),(2,1),(2,2)],
          [(1,0),(1,1),(1,2),(2,0)], [(0,0),(0,1),(1,1),(2,1)]],
}

PIECE_COLORS = {'I': 1, 'O': 2, 'T': 3, 'S': 4, 'Z': 5, 'J': 6, 'L': 7}

BOARD_ROWS = 20
BOARD_COLS = 10
SPAWN_ROW = 0
SPAWN_COL = 3

LEVEL_SPEEDS = [0.8, 0.7, 0.6, 0.5, 0.4, 0.35, 0.3, 0.25, 0.2, 0.15, 0.1]

LINES_PER_LEVEL = 10


def level_speed(level):
    return LEVEL_SPEEDS[min(level, len(LEVEL_SPEEDS) - 1)]


class Piece:
    def __init__(self, name):
        self.name = name
        self.shapes = PIECES[name]
        self.rotation = 0
        self.row = SPAWN_ROW
        self.col = SPAWN_COL
        self.color = PIECE_COLORS[name]

    def cells(self, row=None, col=None, rotation=None):
        r = self.row if row is None else row
        c = self.col if col is None else col
        rot = self.rotation if rotation is None else rotation
        return [(r + dr, c + dc) for dr, dc in self.shapes[rot % 4]]


class Game:
    def __init__(self):
        self.board = [[0] * BOARD_COLS for _ in range(BOARD_ROWS)]
        self.board_colors = [[0] * BOARD_COLS for _ in range(BOARD_ROWS)]
        self.score = 0
        self.lines = 0
        self.level = 0
        self.piece = self._new_piece()
        self.next_piece = self._new_piece()
        self.game_over = False
        self.last_drop = time.time()

    def _new_piece(self):
        return Piece(random.choice(list(PIECES.keys())))

    def _valid(self, piece, row=None, col=None, rotation=None):
        for r, c in piece.cells(row, col, rotation):
            if r < 0 or r >= BOARD_ROWS or c < 0 or c >= BOARD_COLS:
                return False
            if self.board[r][c]:
                return False
        return True

    def move(self, dr, dc):
        nr, nc = self.piece.row + dr, self.piece.col + dc
        if self._valid(self.piece, row=nr, col=nc):
            self.piece.row, self.piece.col = nr, nc
            return True
        return False

    def rotate(self):
        new_rot = (self.piece.rotation + 1) % 4
        # Wall-kick: try center, then nudge left/right
        for dc in (0, -1, 1, -2, 2):
            if self._valid(self.piece, col=self.piece.col + dc, rotation=new_rot):
                self.piece.col += dc
                self.piece.rotation = new_rot
                return

    def hard_drop(self):
        while self.move(1, 0):
            self.score += 2
        self._lock()

    def soft_drop(self):
        if self.move(1, 0):
            self.score += 1
        else:
            self._lock()

    def _lock(self):
        for r, c in self.piece.cells():
            if 0 <= r < BOARD_ROWS and 0 <= c < BOARD_COLS:
                self.board[r][c] = 1
                self.board_colors[r][c] = self.piece.color
        cleared = self._clear_lines()
        self._update_score(cleared)
        self.piece = self.next_piece
        self.next_piece = self._new_piece()
        if not self._valid(self.piece):
            self.game_over = True
        self.last_drop = time.time()

    def _clear_lines(self):
        full = [r for r in range(BOARD_ROWS) if all(self.board[r])]
        for r in full:
            del self.board[r]
            del self.board_colors[r]
            self.board.insert(0, [0] * BOARD_COLS)
            self.board_colors.insert(0, [0] * BOARD_COLS)
        return len(full)

    def _update_score(self, cleared):
        points = [0, 100, 300, 500, 800]
        self.score += points[cleared] * (self.level + 1)
        self.lines += cleared
        self.level = self.lines // LINES_PER_LEVEL

    def tick(self):
        now = time.time()
        if now - self.last_drop >= level_speed(self.level):
            if not self.move(1, 0):
                self._lock()
            self.last_drop = now

    def ghost_cells(self):
        r = self.piece.row
        while self._valid(self.piece, row=r + 1):
            r += 1
        return self.piece.cells(row=r)


def init_colors():
    curses.start_color()
    curses.use_default_colors()
    pairs = [(1, curses.COLOR_CYAN), (2, curses.COLOR_YELLOW),
             (3, curses.COLOR_MAGENTA), (4, curses.COLOR_GREEN),
             (5, curses.COLOR_RED), (6, curses.COLOR_BLUE),
             (7, curses.COLOR_WHITE)]
    for num, fg in pairs:
        curses.init_pair(num, fg, -1)
    curses.init_pair(8, curses.COLOR_WHITE, -1)   # ghost
    curses.init_pair(9, curses.COLOR_BLACK, curses.COLOR_WHITE)  # overlay


def draw_board(win, game, board_top, board_left):
    # Border
    for r in range(BOARD_ROWS + 1):
        win.addch(board_top + r, board_left - 1, curses.ACS_VLINE)
        win.addch(board_top + r, board_left + BOARD_COLS * 2, curses.ACS_VLINE)
    for c in range(BOARD_COLS * 2 + 1):
        win.addch(board_top + BOARD_ROWS, board_left - 1 + c, curses.ACS_HLINE)
    win.addch(board_top + BOARD_ROWS, board_left - 1, curses.ACS_LLCORNER)
    win.addch(board_top + BOARD_ROWS, board_left + BOARD_COLS * 2, curses.ACS_LRCORNER)

    # Board cells
    for r in range(BOARD_ROWS):
        for c in range(BOARD_COLS):
            color = game.board_colors[r][c]
            if color:
                win.addstr(board_top + r, board_left + c * 2,
                           '[]', curses.color_pair(color) | curses.A_BOLD)
            else:
                win.addstr(board_top + r, board_left + c * 2, '  ')

    # Ghost piece
    ghost = set(game.ghost_cells())
    active = set(game.piece.cells())
    for r, c in ghost - active:
        if 0 <= r < BOARD_ROWS:
            win.addstr(board_top + r, board_left + c * 2,
                       '::',  curses.color_pair(8))

    # Active piece
    for r, c in game.piece.cells():
        if 0 <= r < BOARD_ROWS:
            win.addstr(board_top + r, board_left + c * 2,
                       '[]', curses.color_pair(game.piece.color) | curses.A_BOLD)


def draw_sidebar(win, game, board_top, sidebar_left):
    def label(row, text):
        win.addstr(board_top + row, sidebar_left, text)

    label(0, 'TERMTRIS')
    label(2, f'Score')
    label(3, f'{game.score:>8}')
    label(5, f'Lines')
    label(6, f'{game.lines:>8}')
    label(8, f'Level')
    label(9, f'{game.level:>8}')

    label(11, 'Next:')
    next_cells = game.next_piece.cells(row=0, col=0)
    min_r = min(r for r, _ in next_cells)
    min_c = min(c for _, c in next_cells)
    for r, c in next_cells:
        dr, dc = r - min_r, c - min_c
        win.addstr(board_top + 12 + dr, sidebar_left + dc * 2,
                   '[]', curses.color_pair(game.next_piece.color) | curses.A_BOLD)

    label(17, 'Controls:')
    label(18, '← → Move')
    label(19, '↑  Rotate')
    label(20, '↓  Soft drop')
    label(21, 'SPC Hard drop')
    label(22, 'Q  Quit')


def draw_game_over(win, rows, cols):
    msg1 = ' GAME OVER '
    msg2 = ' Press R to restart '
    msg3 = ' Press Q to quit '
    r = rows // 2
    c1 = (cols - len(msg1)) // 2
    c2 = (cols - len(msg2)) // 2
    c3 = (cols - len(msg3)) // 2
    attr = curses.color_pair(9) | curses.A_BOLD
    win.addstr(r - 1, c1, msg1, attr)
    win.addstr(r + 1, c2, msg2, attr)
    win.addstr(r + 2, c3, msg3, attr)


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)
    init_colors()

    rows, cols = stdscr.getmaxyx()
    board_h = BOARD_ROWS + 1
    board_w = BOARD_COLS * 2 + 2
    sidebar_w = 22
    total_w = board_w + sidebar_w
    board_top = max(0, (rows - board_h) // 2)
    board_left = max(1, (cols - total_w) // 2 + 1)
    sidebar_left = board_left + board_w + 1

    game = Game()

    while True:
        rows, cols = stdscr.getmaxyx()
        stdscr.erase()

        if not game.game_over:
            game.tick()

        try:
            draw_board(stdscr, game, board_top, board_left)
            draw_sidebar(stdscr, game, board_top, sidebar_left)
            if game.game_over:
                draw_game_over(stdscr, rows, cols)
        except curses.error:
            pass  # ignore draws outside terminal bounds

        stdscr.refresh()

        key = stdscr.getch()
        if key == ord('q') or key == ord('Q'):
            break
        if game.game_over:
            if key == ord('r') or key == ord('R'):
                game = Game()
            continue

        if key == curses.KEY_LEFT:
            game.move(0, -1)
        elif key == curses.KEY_RIGHT:
            game.move(0, 1)
        elif key == curses.KEY_UP:
            game.rotate()
        elif key == curses.KEY_DOWN:
            game.soft_drop()
        elif key == ord(' '):
            game.hard_drop()

        time.sleep(0.02)


if __name__ == '__main__':
    curses.wrapper(main)
