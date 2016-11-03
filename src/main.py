"""
Contains bootstrapping code - run this script to start the game
    python main.py
"""

from global_vars import Globals
from window_manager import WindowManager
from display import Display
from input_handler import InputHandler
from asset_loader import AssetLoader
import tkinter as tk
import sys
import time
import traceback

class GameDriver:
    def __init__(self):
        self.root = tk.Tk()
        self.windowManager = WindowManager(Globals.NumCols, Globals.NumRows)
        self.display = Display(self.root, self.windowManager)
        self.inputHandler = InputHandler(self.display.getWidget())

    def mainloop(self):
        while True:
            try:
                time.sleep(Globals.Timestep)    # TODO only sleep Timestep - computation time
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
    AssetLoader().loadAssets()  # TODO do in separate thread
    GameDriver().mainloop()

if __name__ == '__main__':
    bootstrap()
