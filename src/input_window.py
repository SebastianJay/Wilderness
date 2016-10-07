"""
Window for processing a user's input and displaying it back as they are
typing. When a command is entered it is passed to the interpreter which
then modifies GameState.
"""
from window import Window

class InputWindow(Window):

    def __init__(self, width, height):
        super().__init__(width, height)

    def update(self, timestep, keypresses):
        pass

    def draw(self):
        midY = height // 2
        return self.pixels
