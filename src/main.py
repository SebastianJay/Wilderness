"""
Contains bootstrapping code - run this script to start the game
    python main.py
"""

from global_vars import Globals
from window import Window
from loading_window import LoadingWindow
from display import Display
from input_handler import InputHandler
import tkinter as tk
import sys
import time
import traceback

class GameDriver:
    def __init__(self):
        self.root = tk.Tk()
        self.window = LoadingWindow(Globals.NumCols, Globals.NumRows)
        self.display = Display(self.root, self.window)
        self.inputHandler = InputHandler(self.display.getWidget())

    def mainloop(self):
        while True:
            try:
                time.sleep(Globals.Timestep)
                keypresses = self.inputHandler.getKeyPresses()
                self.window.update(Globals.Timestep, keypresses)
                self.display.draw()
                self.root.update()
            except tk.TclError: # occurs when window is closed
                sys.exit()
            except:
                if Globals.IsDev:
                    traceback.print_exc()
                sys.exit()

def bootstrap():
    """Perform all processes needed to start up the game"""
    # TODO load assets
    GameDriver().mainloop()

if __name__ == '__main__':
    bootstrap()
