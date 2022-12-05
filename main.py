import curses

import numpy as np

from panel import Panel
from board import Board
from config import Config
from menu import Menu


def main(stdscr):
    
    config = Config(stdscr)
    panel = Panel(stdscr, config)
    board = Board(stdscr, config)
    menu = Menu(stdscr, config)
    
    panel.update_flag_count(board.flags_left)
    while True:
        pressed_key = stdscr.getch()
        panel.update_clock()
        if pressed_key == ord("q"):
            break
        elif pressed_key == curses.KEY_UP:
            board.move_cursor(dy=-1, dx=0)
        elif pressed_key == curses.KEY_DOWN:
            board.move_cursor(dy=1, dx=0)
        elif pressed_key == curses.KEY_LEFT:
            board.move_cursor(dy=0, dx=-1)
        elif pressed_key == curses.KEY_RIGHT:
            board.move_cursor(dy=0, dx=1)
        elif pressed_key == ord("x"):
            board.flag()
            panel.update_flag_count(board.flags_left)
        elif pressed_key == ord("v"):
            if board.check_if_explode():
                panel.update_smile(type="lost")
                board.explode()
            else:
                board.unveil()
                if board.check_if_won():
                    panel.update_smile(type="won")
            

if __name__ == "__main__":
    curses.wrapper(main)
