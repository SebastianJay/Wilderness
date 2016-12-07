from window import Window
from game_state import GameState
from asset_loader import AssetLoader
from global_vars import Globals
import os

class SavesWindow(Window):

    def __init__(self, width, height):
        super().__init__(width, height)

    def reset(self):
        self.marginRow = 2
        self.pointingTo = 0
        self.fileinfo = []

    def load(self):
        self.fileinfo = []
        for path in Globals.SavePaths:
            obj = AssetLoader().getSave(path)
            if obj:
                self.fileinfo.append(obj)
            else:
                self.fileinfo.append(None)
        # draw the loaded file info once
        startCol = 3
        for i in range(len(self.fileinfo)):
            if self.fileinfo[i] is None:
                continue
            row = (self.height - self.marginRow * 2) // len(Globals.SavePaths) * i + self.marginRow
            name = self.fileinfo[i]['name']
            playtime = int(self.fileinfo[i]['playtime'])
            infoStr = name + (' ' * (12 - len(name))) \
                + '{:02}{:02}{:02}'.format(playtime // 3600, (playtime % 3600) // 60, (playtime % 60))
            for j, ch in enumerate(infoStr):
                self.pixels[row][startCol + j] = ch

    def draw(self):
        # draw the cursor
        cursorCol = 1
        for i in range (0,4):
            row = (self.height - self.marginRow * 2) // len(Globals.SavePaths) * i + self.marginRow
            if i == self.pointingTo:
                self.pixels[row][cursorCol] = ">"
            else:
                self.pixels[row][cursorCol] = " "
        return self.pixels

    def update(self, timestep, keypresses):
        for x in range (0, len(keypresses)):
            if keypresses[x] == "Up":
                self.pointingTo = (self.pointingTo - 1) % len(Globals.SavePaths)
            elif keypresses[x] == "Down":
                self.pointingTo = (self.pointingTo - 1) % len(Globals.SavePaths)
            elif keypresses[x] == "Return":
                pass
