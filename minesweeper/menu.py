import curses
import curses.panel

class Menu:
    
    def __init__(self, stdscr, config):
        self.config = config
        self.scr = stdscr.subwin(config.board_height, 
                                config.width, 
                                config.panel_height, 
                                config.offset_ncols)
        self.panel = curses.panel.new_panel(self.scr)
        self.scr.refresh()