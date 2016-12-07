"""
Window containing the world map.
"""
from window import Window
from game_state import GameState
from asset_loader import AssetLoader
from global_vars import Globals
import yaml
import os.path

class InAreaWindow(Window):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.art = []
        self.maps = []
        self.details = []
        self.names = []

    def load(self):       
        artslst = Globals.InAreaPaths
        loader = AssetLoader()
        self.maps = []
        self.details = []
        self.names = []
        for element in artslst:
            self.maps.append(loader.getMap(element[0]).splitlines())
            self.details.append(loader.getConfig(os.path.join('rooms', element[1])))
        for item in self.details[0]:            
            self.names.append(item)

    def update(self, timestep, keypresses):
        # make sure we have loaded
        if len(self.maps) == 0:
            return
            
        # identify the current map we are looking at
        g = GameState()
        currentMap = self.maps[g.activeProtagonistInd]
        #currentTravel = self.travelMasks[g.activeProtagonistInd]

        for c in range(self.width):
             self.pixels[10][c] = " "
        for x in self.names:
             if (g.mapLocation[0] == self.details[0][x]['r']) and (g.mapLocation[1] == self.details[0][x]['c']):
                 for c in range(len(x)):
                     self.pixels[10][c] = x[c]  
                     
        # process keystrokes to move player position
        for key in keypresses:
            if key == "Up" or key == "w":
                if g.mapLocation[0] > 0 and len(currentMap[g.mapLocation[0] - 1]) - 1 >= g.mapLocation[1]:
                    g.mapLocation[0] -= 1
            elif key == "Left" or key == "a":
                if g.mapLocation[1] > 0:
                    g.mapLocation[1] -= 1
            elif key == "Down" or key == "s":
                if g.mapLocation[0] < len(currentMap) - 1 and len(currentMap[g.mapLocation[0] + 1]) - 1 >= g.mapLocation[1]:
                    g.mapLocation[0] += 1
            elif key == "Right" or key == "d":
                if g.mapLocation[1] < len(currentMap[g.mapLocation[0]]) - 1:
                    g.mapLocation[1] += 1
            elif key == "m":
                for x in self.names:
                    if (g.mapLocation[0] == self.details[0][x]['r']) and (g.mapLocation[1] == self.details[0][x]['c']):
                        print(x)
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
    inareawindow = InAreaWindow(120, 35)
    inareawindow.draw()
