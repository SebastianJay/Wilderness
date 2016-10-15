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

class TitleWindow(Window):
    def __init__(self, width, height, art):
        super.__init__(width, height)
        self.pointingTo = 0
        self.art = art

    def update(self, timestep, keypresses):
        for x in range (0, len(keypresses)):
            if keypresses[x] == "Up":
                self.pointingTo = (self.pointingTo - 1) % 4
            elif keypresses[x] == "Down":
                self.pointingTo = (self.pointingTo - 1) % 4
            elif keypresses[x] == "Return":
                if self.pointingTo == 3:
                    sys.exit()

    def draw(self):
        startRow = 25
        column = 49
        for x in range (0,4):
            self.pixels[startRow + x][column] = " "
        self.pixels[startRow + pointingTo][column] = ">"
        return self.pixels
