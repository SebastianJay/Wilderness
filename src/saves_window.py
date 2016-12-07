from window import Window
from game_state import GameState, GameMode
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
        startCol = 10
        for i in range(len(self.fileinfo)):
            if self.fileinfo[i] is None:
                continue
            row = (self.height - self.marginRow * 2) // len(self.fileinfo) * i + self.marginRow
            name = self.fileinfo[i]['name']
            playtime = int(self.fileinfo[i]['playtime'])
            infoStr = name + (' ' * (16 - len(name))) \
                + '{:02}:{:02}:{:02}'.format(playtime // 3600, (playtime % 3600) // 60, (playtime % 60))
            for j, ch in enumerate(infoStr):
                self.pixels[row][startCol + j] = ch

    def draw(self):
        # draw the cursor
        cursorCol = 8
        for i in range(4):
            row = (self.height - self.marginRow * 2) // len(self.fileinfo) * i + self.marginRow
            if i == self.pointingTo:
                self.pixels[row][cursorCol] = ">"
            else:
                self.pixels[row][cursorCol] = " "
        return self.pixels

    def update(self, timestep, keypresses):
        for key in keypresses:
            if key == "Up":
                while True:
                    self.pointingTo = (self.pointingTo - 1) % len(self.fileinfo)
                    if self.fileinfo[self.pointingTo]:
                        break
            elif key == "Down":
                while True:
                    self.pointingTo = (self.pointingTo + 1) % len(self.fileinfo)
                    if self.fileinfo[self.pointingTo]:
                        break
            elif key == "Return":
                GameState().load(self.fileinfo[self.pointingTo])
                GameState().saveId = self.pointingTo
                GameState().gameMode = GameMode.inAreaCommand
                break
