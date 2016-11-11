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
    AssetLoader().loadAssets()  # TODO do in separate thread

    # TODO move out of bootstrap
    from game_state import GameState, GameMode
    from lang_interpreter import Interpreter
    GameState().areaId = 'aspire'
    GameState().roomId = 'townCenter'
    GameState().gameMode = GameMode.inAreaCommand
    i = Interpreter()
    i.executeAction(AssetLoader().getScript('aspire/Rooms/town center.txt')[0][1])
    i.refreshCommandList()

    GameDriver().mainloop()

if __name__ == '__main__':
    bootstrap()
