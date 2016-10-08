"""
Window for processing a user's input and displaying it back as they are
typing. When a command is entered it is passed to the interpreter which
then modifies GameState.
"""
from window import Window
from game_state import GameState

class InputWindow(Window):

    def __init__(self, width, height):
        super().__init__(width, height)
        self.cmdBuffer = ''
        self.cmdBufferLimit = 32

    def update(self, timestep, keypresses):
        for key in keypresses:
            # key is printable -> add it to buffer
            if len(key) == 1 and len(self.cmdBuffer) < self.cmdBufferLimit:
                self.cmdBuffer += key
            # key is backspace -> pop one char from buffer
            elif key == 'BackSpace':
                self.cmdBuffer = self.cmdBuffer[:-1]
            # key is return -> commit command
            elif key == 'Return':
                # TODO replace with actual functionality
                GameState().debugAddHistoryLine(self.cmdBuffer)
                self.cmdBuffer = ''

    def draw(self):
        midY = self.height // 2
        startX = 3
        # clean pixels from last frame
        for i in range(3 + 32):
            self.pixels[midY][startX + i] = ' '
        # add current command input
        fullLine = '>> ' + self.cmdBuffer + ('_' if len(self.cmdBuffer) < self.cmdBufferLimit else '')
        for i, c in enumerate(fullLine):
            self.pixels[midY][startX + i] = c
        return self.pixels
