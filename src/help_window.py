"""
HelpWindow is shown at the bottom of the screen in-game and displays keybindings
and occasionally helpful feedback pushed from other windows to GameState
"""
from window import Window
from game_state import GameState, GameMode
from asset_loader import AssetLoader
from global_vars import Globals

class HelpWindow(Window):

    def reset(self):
        self.config = None  # set in load()
        self.inMessageMode = False
        self.messageText = ''
        self.messageTimer = 0.0

    def load(self):
        self.config = AssetLoader().getConfig(Globals.KeybindingsConfigPath)

    def update(self, timestep, keypresses):
        if self.inMessageMode:
            self.messageTimer += timestep
            if self.messageTimer >= Globals.HelpMessageTimespan:
                self.messageTimer = 0.0
                self.inMessageMode = False
        if not self.inMessageMode and GameState().hasMessage():
            self.inMessageMode = True
            self.messageText = GameState().popMessage()

    def draw(self):
        self.clear()
        if self.inMessageMode:
            self.writeText(self.messageText, 0, 0)
        else:
            dictionaryList = self.config[GameState().gameMode.name]
            # print the keybindings in 4 column format
            for i, dictionary in enumerate(dictionaryList):
                keybindingEntry = ': '.join(list(dictionary.items())[0])
                self.writeText(keybindingEntry, 0, i * self.width // 4)
