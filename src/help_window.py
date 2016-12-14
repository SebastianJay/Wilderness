"""
HelpWindow is shown at the bottom of the screen in-game and displays keybindings
and occasionally helpful feedback pushed from other windows to GameState
"""
from window import Window
from game_state import GameState, GameMode
from asset_loader import AssetLoader
from global_vars import Globals

class HelpWindow(Window):

    def __init__(self, width, height):
        super().__init__(width, height)
        self.config = None  # set in load()
        self.inMessageMode = False
        self.messageText = ''
        self.messageTimer = 0.0
        self.messageThreshold = 2.0

    def load(self):
        self.config = AssetLoader().getConfig(Globals.KeybindingsConfigPath)

    def update(self, timestep, keypresses):
        if self.inMessageMode:
            self.messageTimer += timestep
            if self.messageTimer >= self.messageThreshold:
                self.messageTimer = 0.0
                self.inMessageMode = False
        if not self.inMessageMode and GameState().hasMessage():
            self.inMessageMode = True
            self.messageText = GameState().popMessage()

    def draw(self):
        self.clear()
        if self.inMessageMode:
            for c, ch in enumerate(self.messageText):
                self.pixels[0][c] = ch
        else:
            dictionaryList = self.config[GameState().gameMode.name]
            # print the keybindings in 4 column format
            for i, dictionary in enumerate(dictionaryList):
                key, value = list(dictionary.items())[0]
                cStart = i * self.width // 4
                fullColumn = key + ': ' + value
                for c, ch in enumerate(fullColumn):
                    self.pixels[0][cStart + c] = ch
        return self.pixels
