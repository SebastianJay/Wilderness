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

    def reset(self):
        # main menu options
        self.options = ['New game', 'Load game', 'Options', 'Credits', 'Exit']
        # list of indices of inaccessible options
        self.blockedOptions = []
        # index of option player is looking at
        self.pointingTo = 0
        # which index the save file of the game to be played goes to
        self.freeFileIndex = 0
        # on new game, whether window is asking for player name
        self.isPromptingName = False
        # on new game, holds name that player is typing
        self.nameBuffer = ''

    def load(self):
        # grab the title art and do one-time draw
        art = AssetLoader().getArt('title_window.txt')
        maxLength = max([len(line) for line in art.split('\n')])
        self.writeText(art, self.height // 6, (self.width - maxLength) // 2)

        # refresh which options are enabled
        self.freeFileIndex = AssetLoader().freeSaveFileInd()
        self.blockedOptions = []
        if self.freeFileIndex < 0:
            # remove 'new game' option
            self.blockedOptions.append(0)
        if AssetLoader().lenSaveFiles() == 0:
            # remove 'load game' option
            self.blockedOptions.append(1)

        # reset cursor to first option
        self.pointingTo = 0
        if len(self.blockedOptions) >= len(self.options):
            # this should not happen
            return
        while self.pointingTo in self.blockedOptions:
            self.pointingTo += 1

        self.isLoaded = True

    def update(self, timestep, keypresses):
        def updateCursor(delta):
            while True:
                self.pointingTo = (self.pointingTo + delta) % len(self.options)
                if self.pointingTo not in self.blockedOptions:
                    break

        if self.isPromptingName:
            for key in keypresses:
                if len(key) == 1 and len(self.nameBuffer) < Globals.NameMaxLength:
                    self.nameBuffer += key
                elif key == "BackSpace" and len(self.nameBuffer) > 0:
                    self.nameBuffer = self.nameBuffer[:-1]
                elif key == "Return" and len(self.nameBuffer.strip()) > 0:
                    # clear out old data, fill name and save id, send signal to run startup script
                    gs = GameState()
                    gs.init()
                    gs.name = self.nameBuffer.strip()
                    gs.saveId = self.freeFileIndex
                    gs.gameMode = GameMode.InAreaCommand
                    gs.enterArea(gs.areaId, gs.roomId)
        else:
            for key in keypresses:
                if key == "Up":
                    updateCursor(-1)
                elif key == "Down":
                    updateCursor(1)
                elif key == "Return":
                    cmd = self.options[self.pointingTo]
                    if cmd == 'New game':
                        # switch to name prompt mode before starting game
                        self.isPromptingName = True
                    elif cmd == 'Load game':
                        GameState().gameMode = GameMode.SelectFile
                    elif cmd == 'Options':
                        GameState().gameMode = GameMode.Settings
                    elif cmd == 'Credits':
                        GameState().gameMode = GameMode.Credits
                    elif cmd == 'Exit':
                        sys.exit()

    def draw(self):
        if not AssetLoader().isLoaded:
            return

        # clear bottom half of window
        startRow = self.height * 4 // 7
        startCol = (self.width - len(self.options[0])) // 2
        self.clearPixels(0, startRow, self.width, self.height)

        if self.isPromptingName:
            # draw prompt for name
            promptString = 'What is your name?'
            self.writeText(promptString, startRow, (self.width - len(promptString)) // 2)
            nameBufferFormatted = self.nameBuffer + ('_' if len(self.nameBuffer) < Globals.NameMaxLength else '')
            self.writeText(nameBufferFormatted, startRow, (self.width - Globals.NameMaxLength) // 2)
        else:
            # draw options
            for row, option in enumerate(self.options):
                if row in self.blockedOptions:
                    continue
                self.writeText(option, startRow + row, startCol)
            # draw current cursor
            self.setPixel('>', startRow + self.pointingTo, startCol - 4)
