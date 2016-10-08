"""
Definition for window manager, which takes care of multiple Windows.
"""

from window import Window
from loading_window import LoadingWindow
from input_window import InputWindow

# TODO inherit from Window
class WindowManager:

    def __init__(self, screenWidth, screenHeight):
        self._screenWidth =  screenWidth #the width of the entire screen
        self._screenHeight = screenHeight #the height of the entire screen

        #list of all the windows that the window manager is going to draw
        self._windowList = []
        #list of locations (top-left coordinate) of corresponding windows in windowList
        self._windowPos = []

        #this is the full 2D-array of chars that contains all the content from all the windows.
        #this is what will display on the screen
        self._screen = [[' ' for x in range(self._screenWidth)] for y in range(self._screenHeight)]

    def stitch(self):
        """ stitches together multiple windows into the screen """
        #traverse the window list and determine the order that the windows will be added to the screen
        #must figure out how we will find locations of individual windows
        for x in range(len(self._windowList)):
            pixels = self._windowList[x].draw()
            startr, startc = self._windowPos[x]
            for r in range(len(pixels)):
                for c in range(len(pixels[0])):
                    self._screen[startr + r][startc + c] = pixels[r][c]
            # TODO border

    def draw(self):
        self.stitch()
        return self._screen

    def addWindow(self, window, r, c):
        #possible sorting of windows when adding them
        self._windowList.append(window)
        self._windowPos.append((r, c))

    def update(self, timestep, keypresses):
        # TODO more sophisticated update relaying
        for win in self._windowList:
            win.update(timestep, keypresses)

    def border(self):
        """
        Creates a border of asterisks around the window
        """
        for i in range(0, self.width):
            self.pixels[0][i] = "*",
            self.pixels[self.height - 1][i] = "*"

        for i in range(1, self.height - 1):
            self.pixels[i][0] = "*"
            self.pixels[i][self.width - 1] = "*"
