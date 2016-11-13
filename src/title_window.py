"""
Window for Title screen of game - contains some ASCII art and a list of options
that pull up other windows and/or start up the game.
"""
from game_state import GameState, GameMode
from lang_interpreter import Interpreter
from asset_loader import AssetLoader
from window import Window
import sys

class TitleWindow(Window):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.pointingTo = 0 # index of option player is looking at
        # options to be selected on screen
        self.options = ('New game', 'Load game', 'Options', 'Credits', 'Exit')
        self.art = None     # set in load()
        self.startRow = 0   # reset in load()
        self.startCol = 0   # reset in load()

    def load(self):
        # grab the title art
        self.art = AssetLoader().getArt('title_window.txt')

        # do one-time drawing of title and options onto pixels
        maxLength = 0
        row = self.height // 6 # Looks better than starting at 0
        col = 0
        # Find the longest line...
        for i, char in enumerate(self.art):
            if char == "\n":
                if col > maxLength:
                    maxLength = col
                col = 0
            else:
                col += 1

        # So that we know where to center the ASCII art
        startCol = (self.width - maxLength) // 2
        for i, char in enumerate(self.art):
            if char == "\n":
                row += 1
                col = 0
            else:
                self.pixels[row][col + startCol] = char
                col += 1

        # Same as above, but for the options instead.
        # Note that the options are all left-aligned based on the center
        # of the first option.
        self.startRow = row + (self.height - row - len(self.options)) // 2
        self.startCol = (self.width - len(self.options[0])) // 2
        row = 0
        for option in self.options:
            col = 0
            for char in list(option):
                self.pixels[row + self.startRow][col + self.startCol] = char
                col += 1
            row += 1

    def update(self, timestep, keypresses):
        for key in keypresses:
            if key == "Up":
                self.pointingTo = (self.pointingTo - 1) % len(self.options)
            elif key == "Down":
                self.pointingTo = (self.pointingTo + 1) % len(self.options)
            elif key == "Return":
                cmd = self.options[self.pointingTo]
                if cmd == 'New game':
                    # set game startup info
                    GameState().areaId = 'aspire'
                    GameState().roomId = 'townCenter'
                    GameState().gameMode = GameMode.inAreaCommand
                    i = Interpreter()
                    i.executeAction(AssetLoader().getScript('aspire/Rooms/town center.txt')[0][1])
                    i.refreshCommandList()
                if cmd == 'Exit':
                    sys.exit()

    def draw(self):
        # ensure we are loaded
        if not self.art:
            return self.pixels

        # Clear previous cursor
        for row, temp in enumerate(self.options):
            self.pixels[self.startRow + row][self.startCol - 4] = " "
        # Draw current cursor
        self.pixels[self.startRow + self.pointingTo][self.startCol - 4] = ">"
        return self.pixels

if __name__ == '__main__':
    AssetLoader().loadAssets()
    window = TitleWindow(120, 35)
    window.debugDraw()
