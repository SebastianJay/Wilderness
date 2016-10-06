"""
Contains bootstrapping code - run this script to start the game
    python main.py
"""

from global_vars import Globals
from window import Window
from display import Display
import tkinter as tk
import sys
import time

class GameDriver:
    def __init__(self):
        self.root = tk.Tk()
        self.window = Window(Globals.NumCols, Globals.NumRows)
        self.display = Display(self.root, self.window)

    def mainloop(self):
        while True:
            try:
                time.sleep(Globals.Timestep)
                self.display.draw()
                self.root.update()
            except:
                sys.exit()

def bootstrap():
    """Perform all processes needed to start up the game"""
    # TODO load assets
    GameDriver().mainloop()

if __name__ == '__main__':
    bootstrap()
