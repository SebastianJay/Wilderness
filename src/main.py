"""
Contains bootstrapping code - run this script to start the game
    python main.py
"""

from global_vars import Globals
from window_manager import WindowManager
from display import Display
from input_handler import InputHandler
from asset_loader import AssetLoader
from game_state import GameState, GameMode
from inventory_window import InventoryWindow
import tkinter as tk
import sys
import time
import traceback
import threading

class GameDriver:
    def __init__(self):
        self.root = tk.Tk()
        self.windowManager = WindowManager(Globals.NumCols, Globals.NumRows)
        #self.windowManager = InventoryWindow(Globals.NumCols, Globals.NumRows)
        self.display = Display(self.root, self.windowManager)
        self.inputHandler = InputHandler(self.display.getWidget())

    def initAssets(self):
        GameState().lockGameMode(GameMode.isLoading)
        print('initAssets')
        AssetLoader().loadAssets()
        self.windowManager.load()
        GameState().unlockGameMode()

    def mainloop(self):
        # start off separate thread to load assets
        t = threading.Thread(target = self.initAssets)
        t.daemon = True
        t.start()

        # run update-draw loop forever
        dt = 0.0
        while True:
            try:
                time.sleep(Globals.Timestep - dt if Globals.Timestep - dt > 0.0 else 0.0)
                time1 = time.time()
                keypresses = self.inputHandler.getKeyPresses()
                self.windowManager.update(Globals.Timestep, keypresses)
                self.display.draw()
                self.root.update()
                time2 = time.time()
                dt = time2 - time1
            except tk.TclError: # window was closed
                sys.exit()
            except: # some other exception occurred
                if Globals.IsDev:
                    traceback.print_exc()
                sys.exit()

def bootstrap():
    """Perform all processes needed to start up the game"""
    GameState() # initialize the singleton before threading to avoid race conditions
    GameDriver().mainloop()

if __name__ == '__main__':
    bootstrap()
