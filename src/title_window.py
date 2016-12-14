"""
Window for Title screen of game - contains some ASCII art and a list of options
that pull up other windows and/or start up the game.
"""
from game_state import GameState, GameMode
from global_vars import Globals
from lang_interpreter import Interpreter
from asset_loader import AssetLoader
from window import Window
import sys

class TitleWindow(Window):
    def __init__(self, width, height):
        super().__init__(width, height)

    def reset(self):
        self.pointingTo = 0 # index of option player is looking at
        # options to be selected on screen
        self.options = ['New game', 'Load game', 'Options', 'Credits', 'Exit']
        self.art = None     # set in load()
        self.startRow = 0   # set in load()
        self.startCol = 0   # set in load()
        self.freeFileInd = 0    # set in load()
        self.isPromptingName = False    # on new game, whether window is asking for player name
        self.nameBuffer = ''            # holds name that player is typing

    def load(self):
        # grab the title art
        self.art = AssetLoader().getArt('title_window.txt')

        # do one-time drawing of title and options onto pixels
        maxLength = 0
        row = self.height // 6 # Looks better than starting at 0
        col = 0
        # Find the longest line...
        for char in self.art:
            if char == "\n":
                if col > maxLength:
                    maxLength = col
                col = 0
            else:
                col += 1

        # So that we know where to center the ASCII art
        startCol = (self.width - maxLength) // 2
        for char in self.art:
            if char == "\n":
                row += 1
                col = 0
            else:
                self.pixels[row][col + startCol] = char
                col += 1

        # Check if New Game or Load Game options are visible
        self.freeFileInd = AssetLoader().freeSaveFileInd()
        if self.freeFileInd < 0:
            self.options[0] = ''  # remove new game option
            self.pointingTo = 1   # move cursor
        if AssetLoader().lenSaveFiles() == 0:
            self.options[1] = ''  # remove load game option

        # Same as above, but for the options instead.
        # Note that the options are all left-aligned based on the center
        # of the first option.
        self.startRow = row + (self.height - row - len(self.options)) // 2
        self.startCol = (self.width // 2 - len(self.options[self.pointingTo]) // 2)
        row = 0
        for option in self.options:
            col = 0
            for char in list(option):
                self.pixels[row + self.startRow][col + self.startCol] = char
                col += 1
            row += 1

    def update(self, timestep, keypresses):
        if self.isPromptingName:
            for key in keypresses:
                if len(key) == 1 and len(self.nameBuffer) < Globals.NameMaxLength:
                    self.nameBuffer += key
                elif key == "BackSpace" and len(self.nameBuffer) > 0:
                    self.nameBuffer = self.nameBuffer[:-1]
                elif key == "Return" and len(self.nameBuffer.strip()) > 0:
                    # set game startup info
                    gs = GameState()
                    gs.init()   # clear out any old data
                    gs.name = self.nameBuffer.strip()
                    gs.saveId = self.freeFileInd
                    gs.gameMode = GameMode.inAreaCommand
                    gs.enterArea(gs.areaId, gs.roomId)  # send signal to run startup script
        else:
            for key in keypresses:
                if key == "Up":
                    while True:
                        self.pointingTo = (self.pointingTo - 1) % len(self.options)
                        if self.options[self.pointingTo]:
                            break
                elif key == "Down":
                    while True:
                        self.pointingTo = (self.pointingTo + 1) % len(self.options)
                        if self.options[self.pointingTo]:
                            break
                elif key == "Return":
                    cmd = self.options[self.pointingTo]
                    if cmd == 'New game':
                        # switch to name prompt mode before starting game
                        self.isPromptingName = True
                    elif cmd == 'Load game':
                        GameState().gameMode = GameMode.selectFile
                    elif cmd == 'Options':
                        # TODO: Figure out how to get this to launch the settings window
                        continue
                    elif cmd == 'Credits':
                        GameState().gameMode = GameMode.credits
                    elif cmd == 'Exit':
                        sys.exit()

    def draw(self):
        # ensure we are loaded
        if not self.art:
            return self.pixels

        if self.isPromptingName:
            # Clear previous screen
            for i, r in enumerate(range(self.startRow, self.startRow+len(self.options))):
                for c in range(self.startCol, self.startCol+len(self.options[i])):
                    self.pixels[r][c] = ' '
            # Fill where options used to be with prompt
            promptString = 'What is your name?'
            col = self.width // 2 - len(promptString) // 2
            for i, c in enumerate(range(col, col + len(promptString))):
                self.pixels[self.startRow][c] = promptString[i]
            col = self.width // 2 - Globals.NameMaxLength // 2
            for i, c in enumerate(range(col, col + Globals.NameMaxLength)):
                if i < len(self.nameBuffer):
                    self.pixels[self.startRow+1][c] = self.nameBuffer[i]
                elif i == len(self.nameBuffer):
                    self.pixels[self.startRow+1][c] = '_'
                else:
                    self.pixels[self.startRow+1][c] = ' '
        else:
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
