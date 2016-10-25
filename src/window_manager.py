"""
Definition for window manager, which takes care of multiple Windows.
"""

from window import Window
from loading_window import LoadingWindow
from input_window import InputWindow
from map_window import MapWindow

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
            height = len(pixels)
            width = len(pixels[0])
            # fill in content
            for r in range(height):
                for c in range(width):
                    self._screen[startr + r][startc + c] = pixels[r][c]
            # add border
            for r in range(height):
                self._screen[startr + r][startc-1] = '|'
                self._screen[startr + r][startc + width] = '|'
            for c in range(width):
                self._screen[startr-1][startc + c] = '-'
                self._screen[startr + height][startc + c] = '-'
            self._screen[startr-1][startc-1] = 'o'
            self._screen[startr + height][startc-1] = 'o'
            self._screen[startr + height][startc + width] = 'o'
            self._screen[startr-1][startc + width] = 'o'

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
