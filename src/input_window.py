"""
Window for processing a user's input and displaying it back as they are
typing. When a command is entered it is passed to the interpreter which
then modifies GameState.
"""
from window import Window
from game_state import GameState
from global_vars import Globals

class InputWindow(Window):

    def __init__(self, width, height):
        super().__init__(width, height)

    def update(self, timestep, keypresses):
        gs = GameState()
        for key in keypresses:
            # key is printable -> add it to buffer
            if len(key) == 1:
                gs.appendCmdBuffer(key)
            # key is backspace -> pop one char from buffer
            elif key == 'BackSpace':
                gs.popCmdBuffer()
            # key is return -> commit command
            elif key == 'Return':
                # TODO replace with actual functionality
                gs.debugAddHistoryLine(gs.cmdBuffer)
                gs.clearCmdBuffer()

    def draw(self):
        midY = self.height // 2
        startX = 3
        # clean pixels from last frame
        for i in range(3 + 32):
            self.pixels[midY][startX + i] = ' '
        # add current command input
        cmdBuffer = GameState().cmdBuffer
        fullLine = '>> ' + cmdBuffer + ('_' if len(cmdBuffer) < Globals.CmdMaxLength else '')
        for i, c in enumerate(fullLine):
            self.pixels[midY][startX + i] = c
        return self.pixels
