"""
We will need a title screen, from which a new game, load game, credits, and
exit options can be selected. Suppose we have 35 rows and 120 columns of
characters -- some ASCII art of "Wilderness" will be at the top of the screen
(suppose 25 rows x 120 cols), and the bottom of the screen
(suppose 10 rows x 120 cols) will have the four options.
The player will be able to select between options with arrow keys and select one
 with Enter/Return. Some visual indicator (arrows or color) will show which
 option is being hovered over.

Accounting for borders, this window is 33 rows and 118 columns.

New game - on same window, prompt player for name. Then spawn "Game window"
and do initialization sequence (needs more detail)
Load game - spawn new SelectFile window (#16)
Credits - spawn new Credits window (#15)
Exit - use sys.exit() to kill the program
"""
from asset_loader import AssetLoader
from window import Window
import sys

class TitleWindow(Window):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.pointingTo = 0
        self.art = AssetLoader().getArt('title_window.txt')
        self.options = ('New game', 'Load game', 'Options', 'Credits', 'Exit')

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
                if self.pointingTo == len(self.options) - 1:
                    sys.exit()

    def draw(self):
        # Clear any previous >
        for row, temp in enumerate(self.options):
            self.pixels[self.startRow + row][self.startCol - 4] = " "
        self.pixels[self.startRow + self.pointingTo][self.startCol - 4] = ">"
        return self.pixels

if __name__ == '__main__':
    AssetLoader().loadAssets()
    window = TitleWindow(120, 35)
    window.debugDraw()
