from window import Window
from game_state import GameState

class savesWindow(Window):

    def draw(self):
        g = GameState().readfile(self, fpath)
        info = []

        info[0] = g['name'] + g['id number'] + g['playtime']
        info[1] = g['name'] + g['id number'] + g['playtime']
        info[2] = g['name'] + g['id number'] + g['playtime']
        info[3] = g['name'] + g['id number'] + g['playtime']

        midY = self.height // 2
        startX = 3
        # clean pixels from last frame
        for i in range(3 + 32):
            self.pixels[midY][startX + i] = ' '

        # print the saves
        startRow = 25
        column = 49
        for x in range (0,4):
            self.pixels[startRow + x][column] = " " + info[x]
        self.pixels[startRow + self.pointingTo][column] = ">"
        return self.pixels

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
                #TODO load a file