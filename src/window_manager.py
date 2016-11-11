"""
Definition for window manager, which is itself a Window that contains
multiple sub-Windows and arranges when each is displayed/updated.
"""

from window import Window
from loading_window import LoadingWindow
from input_window import InputWindow
from map_window import MapWindow
from history_window import HistoryWindow
from title_window import TitleWindow
from palette_window import PaletteWindow
from global_vars import Globals

class WindowManager(Window):

    def __init__(self, width, height):
        super().__init__(width, height)
        #list of all the windows that the window manager is going to draw
        self.windowList = []
        #list of locations (top-left coordinate) of corresponding windows in windowList
        self.windowPos = []

        # list of list of indices that represent the windows that are part of one possible screen
        self.windowGroups = []
        # stack of indices into windowGroups representing the active groups (what is on screen now)
        self.activeWindowGroups = []

        # create instances of all the Windows
        self.initWindows(self.height, self.width)

    def addWindow(self, windowcls, startr, startc, numrows, numcols):
        """ Creates a Window of a certain width and height at a certain location """
        # adjust the row, col, width, and height values for the border
        self.windowList.append(windowcls(numcols - 2, numrows - 2))
        self.windowPos.append((startr + 1, startc + 1))

    def initWindows(self, screenrows, screencols):
        """ Instantiates all Windows needed in game at the start """
        #self.addWindow(LoadingWindow, 0, Globals.NumCols * 19 // 24 - 1, Globals.NumRows, Globals.NumCols * 5 // 24)
        # add help window
        # add credits window
        # add select file window

        splitCol = Globals.NumCols * 19 // 24
        splitRow = Globals.NumRows * 5 // 7
        self.addWindow(HistoryWindow, 0, 0, splitRow, splitCol)
        self.addWindow(InputWindow, splitRow - 1, 0, Globals.NumRows - (splitRow - 1), splitCol)
        self.addWindow(PaletteWindow, 0, splitCol - 1, Globals.NumRows, Globals.NumCols - (splitCol - 1))

        self.addWindow(MapWindow, 0, 0, Globals.NumRows, Globals.NumCols * 3 // 4)
        # add in-area map window
        # add inventory window
        self.addWindow(TitleWindow, 0, 0, Globals.NumRows, Globals.NumCols)

        # create History/Input/Palette/Help group
        self.windowGroups = [
            (1, 0, 2),    #NOTE the ordering here is specific as Input gets updated before History
            (3,),
            (4,)
        ]
        # initially the first window group is on screen
        self.activeWindowGroups = [0]

    def draw(self):
        """ stitches together multiple Windows from active group into the screen """
        formatting = []
        for groupind in self.activeWindowGroups:
            for winind in self.windowGroups[groupind]:
                pixels = self.windowList[winind].draw()
                startr, startc = self.windowPos[winind]
                height = len(pixels)
                width = len(pixels[0])
                # fill in content
                for r in range(height):
                    for c in range(width):
                        self.pixels[startr + r][startc + c] = pixels[r][c]
                # add border
                for r in range(height):
                    self.pixels[startr + r][startc-1] = '|'
                    self.pixels[startr + r][startc + width] = '|'
                for c in range(width):
                    self.pixels[startr-1][startc + c] = '-'
                    self.pixels[startr + height][startc + c] = '-'
                self.pixels[startr-1][startc-1] = 'o'
                self.pixels[startr + height][startc-1] = 'o'
                self.pixels[startr + height][startc + width] = 'o'
                self.pixels[startr-1][startc + width] = 'o'
                # add to formatting
                for formatter in self.windowList[winind].formatting:
                    style, (start_index, end_index) = formatter
                    r1 = start_index // width
                    c1 = start_index % width
                    r2 = end_index // width
                    c2 = end_index % width
                    # if the start and end rows are different, add multiple formatter entries
                    # that way the rows are broken up
                    c = c1
                    for r in range(r1, r2):
                        f1 = (r + startr) * self.width + (c + startc)
                        f2 = (r + startr) * self.width + (width - 1 + startc)
                        formatting.append((style, (f1, f2)))
                        c = 0
                    f1 = (r2 + startr) * self.width + (c + startc)
                    f2 = (r2 + startr) * self.width + (c2 + startc)
                    formatting.append((style, (f1, f2)))
        self.formatting = sorted(formatting, key=lambda tup: tup[1][0])
        return self.pixels

    def update(self, timestep, keypresses):
        """ sends update signal to Windows in the active group """
        # update is only send to activeWindowGroups[-1], so the foreground windows
        for winind in self.windowGroups[self.activeWindowGroups[-1]]:
            self.windowList[winind].update(timestep, keypresses)
