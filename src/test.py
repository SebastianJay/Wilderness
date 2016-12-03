# -*- coding: utf-8 -*-
"""
Created on Mon Nov 21 22:55:35 2016

@author: Kwon
"""

from window import Window
from game_state import GameState
from asset_loader import AssetLoader
from global_vars import Globals

class InAreaWindow():
    def __init__(self):
        super().__init__()
        self.details = []
        self.names = []

    def load(self):
        artslst = Globals.InAreaPaths
        loader = AssetLoader()
        self.details = []
        self.details.append(loader.getConfig(artslst[1]))

    def update(self, timestep, keypresses):
        pass

    def draw(self):
        artslst = Globals.InAreaPaths
        loader = AssetLoader()
        self.details.append(loader.getConfig(artslst[1]))
        for item in self.details[0]:
            self.names.append(item)
        for x in self.names:
            print(x)
            print(self.details[0][x]['r'])
            print(self.details[0][x]['c'])

if __name__ == '__main__':
    AssetLoader().loadAssets()
    inareawindow = InAreaWindow()
    inareawindow.draw()