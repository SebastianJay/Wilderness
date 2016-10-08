"""
Contains bootstrapping code - run this script to start the game
    python main.py
"""

from global_vars import Globals
from window import Window
from loading_window import LoadingWindow
from input_window import InputWindow
from history_window import HistoryWindow
from window_manager import WindowManager
from display import Display
from input_handler import InputHandler
import tkinter as tk
import sys
import time
import traceback

class GameDriver:
    def __init__(self):
        self.root = tk.Tk()
        self.windowManager = WindowManager(Globals.NumCols, Globals.NumRows)
        # TODO encapsulate window instantiation in WindowManager
        self.windowManager.addWindow(HistoryWindow(90-2, 20-2), 0+1, 0+1)
        self.windowManager.addWindow(InputWindow(90-2, 16-2), 19+1, 0+1)
        self.windowManager.addWindow(LoadingWindow(30-2, 35-2), 0+1, 89+1)
        self.display = Display(self.root, self.windowManager)
        self.inputHandler = InputHandler(self.display.getWidget())

    def mainloop(self):
        while True:
            try:
                time.sleep(Globals.Timestep)
                keypresses = self.inputHandler.getKeyPresses()
                self.windowManager.update(Globals.Timestep, keypresses)
                self.display.draw()
                self.root.update()
            except tk.TclError: # window was closed
                sys.exit()
            except: # some other exception occurred
                if Globals.IsDev:
                    traceback.print_exc()
                sys.exit()

def bootstrap():
    """Perform all processes needed to start up the game"""
    # TODO load assets
    GameDriver().mainloop()

if __name__ == '__main__':
    bootstrap()
