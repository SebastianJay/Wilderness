"""
Window for processing a user's input and displaying it back as they are
typing. When a command is entered it is passed to the interpreter which
then modifies GameState.
"""
from window import Window
from game_state import GameState, GameMode
from asset_loader import AssetLoader
from global_vars import Globals
from lang_parser import BodyNode
from lang_interpreter import Interpreter

class InputWindow(Window):

    def __init__(self, width, height):
        super().__init__(width, height)
        self.interpreter = Interpreter()
        self.choiceInd = 0

    def update(self, timestep, keypresses):
        gs = GameState()
        if gs.gameMode == GameMode.inAreaChoice:
            for key in keypresses:
                if key == 'Up':
                    self.choiceInd = (self.choiceInd - 1) % len(gs.choiceList)
                elif key == 'Down':
                    self.choiceInd = (self.choiceInd + 1) % len(gs.choiceList)
                elif key == 'Return':
                    self.interpreter.resume(self.choiceInd)
        else:
            for key in keypresses:
                # key is printable -> add it to buffer
                if len(key) == 1:
                    gs.appendCmdBuffer(key)
                # key is backspace -> pop one char from buffer
                elif key == 'BackSpace':
                    gs.popCmdBuffer()
                # key is return -> commit command
                elif key == 'Return':
                    if gs.gameMode == GameMode.inAreaInput:
                        self.interpreter.resume(gs.cmdBuffer)
                    else:   # TODO if inAreaCommand
                        cmdString = gs.cmdBuffer.strip()
                        prefixTree = gs.cmdMap
                        while cmdString:
                            val = None
                            for prefix in prefixTree:
                                if cmdString[:len(prefix)] == prefix:
                                    val = prefixTree[prefix]
                                    if isinstance(val, BodyNode):
                                        # special logic for go to - change room ID
                                        if gs.cmdBuffer.strip()[0:5] == 'go to':
                                            roomId = AssetLoader().reverseRoomLookup(gs.cmdBuffer.strip()[5:].strip(), gs.areaId)
                                            gs.roomId = roomId or gs.roomId
                                        self.interpreter.executeAction(val)
                                        val = None  # make outer loop break out
                                        break
                                    elif isinstance(val, dict):
                                        prefixTree = val
                                        cmdString = cmdString[len(prefix):].strip()
                                        break
                            if val is None:
                                break

                    #gs.debugAddHistoryLine(gs.cmdBuffer)
                    gs.clearCmdBuffer()

    def draw(self):
        # clean pixels from last frame
        for i in range(self.height):
            for j in range(self.width):
                self.pixels[i][j] = ' '

        gs = GameState()
        if gs.gameMode == GameMode.inAreaChoice:
            # display choices
            rStart = 0
            cStart = 3
            cursorOffset = 3
            r = 0
            for choice in gs.choiceList:
                for i, c in enumerate(choice):
                    self.pixels[rStart + r][cStart + cursorOffset + i] = c
                r += 1
            self.pixels[rStart + self.choiceInd][cStart] = '>'
            self.pixels[rStart + self.choiceInd][cStart+1] = '>'
        else:
            midY = self.height // 2
            startCol = 3
            # add current command input
            cmdBuffer = gs.cmdBuffer
            fullLine = '>> ' + cmdBuffer + ('_' if len(cmdBuffer) < Globals.CmdMaxLength else '')
            col = 0
            for i, char in enumerate(fullLine):
                # Start a new line if necessary
                if startCol + col >= self.width:
                    midY += 1
                    col = startCol
                self.pixels[midY][startCol + col] = char
                col += 1

        return self.pixels
