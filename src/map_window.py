"""
Window containing the world map.
"""
from window import Window
from game_state import GameState
from asset_loader import AssetLoader
from global_vars import Globals

class MapWindow(Window):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.maps = []
        self.colorMasks = []
        self.travelMasks = []

    def load(self):
        self.maps = []
        self.colorMasks = []
        self.travelMasks = []
        mapslst = Globals.MapsPaths
        loader = AssetLoader()
        for threetup in mapslst:
            self.maps.append(loader.getMap(threetup[0]).splitlines())
            self.colorMasks.append(loader.getMap(threetup[1]).splitlines())
            self.travelMasks.append(loader.getMap(threetup[2]).splitlines())

    def update(self, timestep, keypresses):
        # make sure we have loaded
        if len(self.maps) == 0:
            return

        # identify the current map we are looking at
        g = GameState()
        currentMap = self.maps[g.activeProtagonistInd]
        currentTravel = self.travelMasks[g.activeProtagonistInd]

        # process keystrokes to move player position
        for key in keypresses:
            if key == "Up" or key == "w":
                if g.mapLocation[0] > 0 and len(currentMap[g.mapLocation[0] - 1]) - 1 >= g.mapLocation[1]:
                    if currentTravel[g.mapLocation[0] - 1][g.mapLocation[1]] == '0':
                        g.mapLocation[0] -= 1
            elif key == "Left" or key == "a":
                if g.mapLocation[1] > 0:
                    if currentTravel[g.mapLocation[0]][g.mapLocation[1] - 1] == '0':
                        g.mapLocation[1] -= 1
            elif key == "Down" or key == "s":
                if g.mapLocation[0] < len(currentMap) - 1 and len(currentMap[g.mapLocation[0] + 1]) - 1 >= g.mapLocation[1]:
                    if currentTravel[g.mapLocation[0] + 1][g.mapLocation[1]] == '0':
                        g.mapLocation[0] += 1
            elif key == "Right" or key == "d":
                if g.mapLocation[1] < len(currentMap[g.mapLocation[0]]) - 1:
                    if currentTravel[g.mapLocation[0]][g.mapLocation[1] + 1] == '0':
                        g.mapLocation[1] += 1
            elif key == "Return":
                # TODO
                pass

    def draw(self):
        # make sure we have loaded
        if len(self.maps) == 0:
            return self.pixels

        # identify the current map we are looking at
        g = GameState()
        currentMap = self.maps[g.activeProtagonistInd]

        # draw out the map
        for row in range(len(currentMap)):
            for column in range(len(currentMap[row])):
                self.pixels[row][column] = currentMap[row][column]

        # overlay the character's position
        self.pixels[g.mapLocation[0]][g.mapLocation[1]] = '@'
        return self.pixels

if __name__ == '__main__':
    AssetLoader().loadAssets()
    mapWindow = MapWindow(1280, 720)
    mapWindow.draw()
