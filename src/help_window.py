"""
In order to help new players know what keys to press, we will
reserve a 1 row window that will contain prompts on what keys
map to what behaviors, e.g.

Arrow keys: Move      Return: Confirm choice
This will be visible in practically every view in the game (except
perhaps the title screen, which player can probably figure out).

We will statically define for every situation in the game what the
keybindings are. The GameState will maintain which "situation" it is
in at any point in time, and the Help window will draw from that.

Assume GameState has a dict {situation: keybindings[]} and a string
situation which tells you which value to pull from the dict. Then
render that list.

The window will be 1 row and 120-2 = 118 columns.
"""
from window import Window
from game_state import GameState, GameMode
from asset_loader import AssetLoader
from global_vars import Globals

class HelpWindow(Window):

    def __init__(self, width, height):
        super().__init__(width, height)
        self.config = None
        self.mode = None

    def load(self):
        self.config = AssetLoader().getConfig(Globals.KeybindingsConfigPath)

    def update(self, timestep, keypresses):
        self.mode = GameState().gameMode.name


    def draw(self):
        if self.mode is None:
            return self.pixels
        dictionaryList = self.config[self.mode]
        i = 0
        j = 0
        for index, dictionary in enumerate(dictionaryList):
            key, value = list(dictionary.items())[0]
            for char in key:
                self.pixels[i][j] = char
                j += 1
            self.pixels[i][j] = ':'
            j += 1
            self.pixels[i][j] = ' '
            j += 1
            for char in value:
                self.pixels[i][j] = char
                j += 1
            j = self.width//4 + (index * self.width//4)
            #self.width/4 in order to have 4 stationary columns
        return self.pixels
