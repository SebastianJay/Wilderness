"""
Definition for window manager, which takes care of multiple Windows.
"""

from window import Window
from loading_window import LoadingWindow
from input_window import InputWindow
from map_window import MapWindow
from history_window import HistoryWindow

# TODO inherit from Window
class WindowManager:

    def __init__(self, screenWidth, screenHeight):
        self._screenWidth =  screenWidth #the width of the entire screen
        self._screenHeight = screenHeight #the height of the entire screen

        #list of all the windows that the window manager is going to draw
        self._windowList = []
        #list of locations (top-left coordinate) of corresponding windows in windowList
        self._windowPos = []

        # list of list of indices that represent the windows that are part of one possible screen
        self._windowGroups = []
        # stack of indices into windowGroups representing the active groups (what is on screen now)
        self._activeWindowGroups = []

        #this is the full 2D-array of chars that contains all the content from all the windows.
        #this is what will display on the screen
        self._screen = [[' ' for x in range(self._screenWidth)] for y in range(self._screenHeight)]

        # create instances of all the Windows
        self.initWindows(self._screenHeight, self._screenWidth)

    def addWindow(self, windowcls, startr, startc, numrows, numcols):
        """ Creates a Window of a certain width and height at a certain location """
        self._windowList.append(windowcls(numcols - 2, numrows - 2))
        self._windowPos.append((startr + 1, startc + 1))

    def initWindows(self, screenrows, screencols):
        """ Instantiates all Windows needed in game at the start """
        # add help window
        # add title window
        # add credits window
        # add select file window
        self.addWindow(HistoryWindow, 0, 0, 25, 95)
        self.addWindow(InputWindow, 24, 0, 11, 95)
        # add palette window
        self.addWindow(LoadingWindow, 0, 94, 35, 25)
        self.addWindow(MapWindow, 0, 0, 35, 120)
        # add in-area map window
        # add inventory window

        # create History/Input/Palette/Help group
        self._windowGroups = [
            (0, 1, 2),    #TODO change
            (3,)
        ]
        # initially the first window group is on screen
        self._activeWindowGroups = [0, 1]

    def draw(self):
        """ stitches together multiple Windows from active group into the screen """
        for groupind in self._activeWindowGroups:
            for winind in self._windowGroups[groupind]:
                pixels = self._windowList[winind].draw()
                startr, startc = self._windowPos[winind]
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
        return self._screen

    def update(self, timestep, keypresses):
        """ sends update signal to Windows in the active group """
        # update is only send to activeWindowGroups[-1], so the foreground windows
        for winind in self._windowGroups[self._activeWindowGroups[-1]]:
            self._windowList[winind].update(timestep, keypresses)
