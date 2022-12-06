import curses

class Config():
    CELL_WIDTH = 4
    CELL_HEIGHT = 2 
    
    def __init__(self, stdscr):
        self._setup_general(stdscr)
        self._setup_geometry(stdscr)
        self._setup_colors()
        self._setup_symbols()
        
    def _setup_general(self, stdscr): 
        stdscr.timeout(100)
        curses.curs_set(0)
               
    def _setup_geometry(self, stdscr):
        scr_height, scr_width = stdscr.getmaxyx()
        self.panel_height = 2
        self.ncols = self._calc_dim(scr_width, self.CELL_WIDTH)
        self.nrows = self._calc_dim(scr_height - self.panel_height, self.CELL_HEIGHT)  
        self.board_height = self.nrows * self.CELL_HEIGHT + 1
        self.menu_height = self.board_height + 1
        self.width = self.ncols * self.CELL_WIDTH + 1
        self.offset_ncols = (scr_width - self.width) // 2 
        
    def _setup_colors(self):
        curses.init_color(200, 0, 1000, 0)
        curses.init_color(201, 1000, 0, 0)
        curses.init_color(202, 1000, 1000, 0)
        
        curses.init_pair(1, 200, curses.COLOR_BLACK)
        curses.init_pair(2, 201, curses.COLOR_BLACK)
        curses.init_pair(3, 200, 202)
        
    def _setup_symbols(self):
        pass
    
    def _calc_dim(self, size, cell_size):
        return size // cell_size - 1 if size % cell_size == 0 else size // cell_size