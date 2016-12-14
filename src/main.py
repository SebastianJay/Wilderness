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
import tkinter as tk
import sys
import time
import traceback
import threading

class GameDriver:
    def __init__(self):
        GameState() # initialize the singleton before threading to avoid race conditions
        self.root = tk.Tk()
        self.windowManager = WindowManager()
        self.display = Display(self.root, self.windowManager)
        self.inputHandler = InputHandler(self.display.widget)

    def initAssets(self):
        AssetLoader().loadAssets()
        AssetLoader().loadSaves()
        AssetLoader().loadSettings()
        # send events for loaded settings
        if AssetLoader().getSettings() is not None:
            for setting in AssetLoader().getSettings():
                GameState().onSettingChange(setting[0], setting[1])
        self.windowManager.load()
        GameState().unlockGameMode()

    def mainloop(self):
        # start off separate thread to load assets
        GameState().lockGameMode(GameMode.isLoading)
        t = threading.Thread(target=self.initAssets)
        t.daemon = True
        t.start()

        # run update-draw loop forever
        dt = 0.0
        while True:
            try:
                time.sleep(max(Globals.Timestep - dt, 0.0))
                timeElapsed = max(Globals.Timestep, dt)
                time1 = time.time()
                self.display.draw()
                keypresses = self.inputHandler.getKeyPresses()
                self.windowManager.update(timeElapsed, keypresses)
                self.root.update()
                time2 = time.time()
                dt = time2 - time1
            except tk.TclError: # window was closed
                sys.exit()
            except SystemExit:
                break    # thrown on main menu exit
            except: # some other exception occurred
                if Globals.IsDev:
                    traceback.print_exc()
                sys.exit()

if __name__ == '__main__':
    GameDriver().mainloop()
