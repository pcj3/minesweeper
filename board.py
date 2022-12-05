import curses
import numpy as np
from enum import IntEnum

class Tile(IntEnum):
    VEILED = 0
    UNVEILED = 1
    BOMB = -1
    FLAG = -2
    
class Board:
    CURSOR_SYMBOL = " "
    BOMB_SYMBOL = "O"
    TILE_SYMBOL = " "
    FLAG_SYMBOL = "F"
    
    def __init__(self, stdscr, config):
        self.config = config
        self.scr = stdscr.subwin(config.board_height, 
                                    config.width, 
                                    config.panel_height, 
                                    config.offset_ncols)
        self.cursor_y, self.cursor_x = 0, 0
        self.solved, self.state  = self._setup_board()
        self.nbombs = np.count_nonzero(self.solved == -1)
        self.move_cursor(dy=0, dx=0)
        self._setup_grid() 
          
    @property
    def visited(self):
        return 
            
    @property
    def flags_left(self):
        return self.nbombs - np.count_nonzero(self.state == Tile.FLAG)
        
    def _get_cursor_symbol(self, current_yx=False):
        if self.state[self.cursor_y, self.cursor_x] == Tile.FLAG:
            return self.FLAG_SYMBOL
        elif self.state[self.cursor_y, self.cursor_x] == Tile.UNVEILED:
            if self.solved[self.cursor_y, self.cursor_x] == 0:
                return "-"
            return str(self.solved[self.cursor_y, self.cursor_x])
        elif current_yx:
            return curses.ACS_DIAMOND
        else:
            return self.TILE_SYMBOL
        
    def _get_scr_col(self, x=None):
        if x is not None:
            return x * self.config.CELL_WIDTH + 2
        return self.cursor_x * self.config.CELL_WIDTH + 2
    
    def _get_scr_row(self, y=None):
        if y is not None:
            return y * self.config.CELL_HEIGHT + 1
        return self.cursor_y * self.config.CELL_HEIGHT + 1 
        
    def _get_surrounding_tiles(self, y, x):
        for i in [x-1, x, x+1]:
            for j in [y-1, y, y+1]:
                if (0 <= i < self.config.ncols) and (0 <= j < self.config.nrows) and ((j, i) != (y, x)):
                    yield  [j, i]

            
    def _setup_grid(self):
        max_x = self.config.width - 1
        max_y = self.config.board_height - 1
    
        self.scr.border()
        self.scr.addch(0, 0, curses.ACS_LTEE)
        self.scr.addch(0, max_x, curses.ACS_RTEE)        
        for i in np.arange(self.config.CELL_WIDTH, max_x, self.config.CELL_WIDTH):
            self.scr.addch(0, i, curses.ACS_TTEE)
        for i in np.arange(self.config.CELL_WIDTH, max_x, self.config.CELL_WIDTH):
            self.scr.addch(max_y, i, curses.ACS_BTEE)
        for i in np.arange(self.config.CELL_HEIGHT, max_y, self.config.CELL_HEIGHT): 
            self.scr.addch(i, 0, curses.ACS_LTEE)
        for i in np.arange(self.config.CELL_HEIGHT, max_y, self.config.CELL_HEIGHT): 
            self.scr.addch(i, max_x, curses.ACS_RTEE)
        for i in np.arange(self.config.CELL_HEIGHT, max_y, self.config.CELL_HEIGHT): 
            self.scr.hline(i, 1, curses.ACS_HLINE, max_x-1)
        for i in [2*self.config.CELL_WIDTH, 
                    max_x-2*self.config.CELL_WIDTH]:
            self.scr.addch(0, i, curses.ACS_PLUS)        
        for i in [max_x // 2 - (self.config.CELL_WIDTH // 2),
                    max_x // 2 + (self.config.CELL_WIDTH // 2)]: 
            if self.config.ncols // 2 == 0:
                self.scr.addch(0, i, curses.ACS_BTEE)
            else:
                self.scr.addch(0, i, curses.ACS_PLUS)
        for i in np.arange(self.config.CELL_WIDTH, max_x, self.config.CELL_WIDTH):
            for j in np.arange(1, max_y, self.config.CELL_HEIGHT):
                self.scr.addch(j, i, curses.ACS_VLINE)        
        for i in np.arange(self.config.CELL_WIDTH, max_x, self.config.CELL_WIDTH):
            for j in np.arange(self.config.CELL_HEIGHT, max_y, self.config.CELL_HEIGHT):
                self.scr.addch(j, i, curses.ACS_PLUS)                        
        self.scr.refresh()

    def _setup_board(self, seed=None, mine_prob=0.2):
        rng = np.random.default_rng(0)
        mines = rng.choice([0, 1], size=(self.config.nrows, self.config.ncols), p=[1-mine_prob, mine_prob])
        mines_paded = np.pad(mines, pad_width=((1, 1),(1, 1)), mode="constant", constant_values=0)
        kernel = np.pad([[0]], pad_width=((1, 1),(1, 1)), mode="constant", constant_values=1)
        subarrays_shape = kernel.shape + tuple(np.subtract(mines_paded.shape, kernel.shape) + 1)
        subarrays = np.lib.stride_tricks.as_strided(mines_paded, 
                                                    shape = subarrays_shape, 
                                                    strides = mines_paded.strides * 2)
        solved = np.einsum('ij,ijkl->kl', kernel, subarrays)
        solved[mines == 1] = Tile.BOMB
        return solved, np.zeros(shape=(self.config.nrows, self.config.ncols))
        
    def move_cursor(self, dy, dx):
        self.scr.addch(self._get_scr_row(), 
                        self._get_scr_col(),    
                        self._get_cursor_symbol())
        self.cursor_y = np.clip(self.cursor_y + dy, 0, self.config.nrows-1)
        self.cursor_x = np.clip(self.cursor_x + dx, 0, self.config.ncols-1)
        self.scr.addch(self._get_scr_row(), 
                        self._get_scr_col(), 
                        self._get_cursor_symbol(current_yx=True),
                        curses.color_pair(1) | curses.A_LEFT)
        self.scr.refresh()
        
    def flag(self):
        if self.state[self.cursor_y, self.cursor_x] == Tile.FLAG:
            self.state[self.cursor_y, self.cursor_x] = Tile.VEILED
            self.move_cursor(dy=0, dx=0)
        elif self.flags_left > 0:
            self.state[self.cursor_y, self.cursor_x] = Tile.FLAG
            self.scr.addch(self._get_scr_row(), self._get_scr_col(), self.FLAG_SYMBOL)
            self.scr.refresh()
                              
    def unveil(self):
        if self.solved[self.cursor_y, self.cursor_x] == 0:
            cascade_stack = [[self.cursor_y, self.cursor_x]]
            while cascade_stack:
                surrounding_tiles = self._get_surrounding_tiles(*cascade_stack.pop())
                for tile in surrounding_tiles:
                    if self.state[tile[0], tile[1]] == Tile.UNVEILED:
                        pass
                    else:
                        solved_val = self.solved[tile[0], tile[1]]
                        if solved_val != Tile.BOMB:
                            self.state[tile[0], tile[1]] = Tile.UNVEILED
                            self.scr.addch(self._get_scr_row(tile[0]), 
                                            self._get_scr_col(tile[1]), 
                                            str(solved_val))  
                            if solved_val == 0:
                                cascade_stack.append(tile)
                                self.scr.addch(self._get_scr_row(tile[0]), 
                                                self._get_scr_col(tile[1]), 
                                                "-") 
        else:
            self.state[self.cursor_y, self.cursor_x] = Tile.UNVEILED
        self.move_cursor(dy=0, dx=0)
        self.scr.refresh()
                
    def check_if_explode(self):
        return self.solved[self.cursor_y, self.cursor_x] == Tile.BOMB
        
    def explode(self):
        bombs_in_order = sorted(np.argwhere(self.solved == Tile.BOMB), 
                        key=lambda i: np.abs(self.cursor_y - i[0] + self.cursor_x - i[1]))
        for i in bombs_in_order:
            self.scr.addch(self._get_scr_row(i[0]), 
                            self._get_scr_col(i[1]), 
                            self.BOMB_SYMBOL,
                            curses.color_pair(2))
            self.scr.refresh()
            curses.napms(100)
                    
    def check_if_won(self):
        return np.logical_xor(self.solved == Tile.BOMB, self.state == Tile.UNVEILED).all()
        
        