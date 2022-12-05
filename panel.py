import curses
import numpy as np
import datetime

class Panel:
    CELL_WIDTH = 4
    
    def __init__(self, stdscr, config):
        self.config = config
        self.scr = stdscr.subwin(self.config.panel_height, 
                                self.config.width, 
                                0, 
                                self.config.offset_ncols)
        self._setup_border()
        self.start_new_game()
        
    def _setup_border(self):
        max_x = self.config.width - 1
        
        self.scr.addch(0, 0, curses.ACS_ULCORNER)
        self.scr.insch(0, max_x, curses.ACS_URCORNER)
        vlines_indicies = [2*self.config.CELL_WIDTH,
                            max_x-2*self.config.CELL_WIDTH,
                            max_x // 2 - (self.config.CELL_WIDTH // 2), 
                            max_x // 2 + (self.config.CELL_WIDTH // 2)]
        self.scr.hline(0, 1, curses.ACS_HLINE, max_x-1)
        for i in vlines_indicies:
            self.scr.addch(0, i, curses.ACS_TTEE)
            self.scr.addch(1, i, curses.ACS_VLINE)
        
        self.scr.addch(1, 0, curses.ACS_VLINE)
        self.scr.insch(1, max_x, curses.ACS_VLINE)
        self.scr.refresh()

    def update_clock(self):
        secs = str((datetime.datetime.now() - self.start_time).seconds).zfill(3)
        self.scr.addstr(1, self.CELL_WIDTH - 1, secs)
        self.scr.refresh()
    
    def update_flag_count(self, n):
        self.scr.addstr(1, self.config.width - 6, str(n).zfill(3))
        self.scr.refresh()
        
    def update_smile(self, type):
        if type == "won":
            self.scr.addstr(1, (self.config.width - 1) // 2 - 1, "B-)", curses.color_pair(3) | curses.A_BOLD)
        elif type == "lost":
            self.scr.addstr(1, (self.config.width - 1) // 2 - 1, ":-(", curses.color_pair(3) | curses.A_BOLD)
        else:
            self.scr.addstr(1, 
            (self.config.width - 1) // 2 - 1, ":-)", 
            curses.A_VERTICAL)
        self.scr.refresh()
            
    def start_new_game(self):
        self.start_time = datetime.datetime.now()
        self.update_clock()
        self.update_smile(type="normal")