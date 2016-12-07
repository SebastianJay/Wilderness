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

    def reset(self):
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

    def draw(self):
        # make sure we have loaded
        if len(self.maps) == 0:
            return self.pixels

        # identify the current map we are looking at
        g = GameState()
        currentMap = self.maps[g.activeProtagonistInd]
        colorMask = self.colorMasks[g.activeProtagonistInd]

        # draw out the map and color it
        self.formatting = []
        previousColorCode = "null"
        previousRow = -1
        for row in range(min(len(currentMap),self.height)):
            for column in range(min(len(currentMap[row]),self.width)):
                self.pixels[row][column] = currentMap[row][column]
                colorCode = colorMask[row][column]
                color = "white"
                # Check to see if the character is at this position
                # If so, character should be a white "@"
                if (g.mapLocation[0] == row and g.mapLocation[1] == column):
                    self.pixels[g.mapLocation[0]][g.mapLocation[1]] = '@'
                    colorCode = "w"
                # To reduce the number if tkinter insert calls in display, look for runs of the same color on the same row
                if(previousColorCode == colorCode and row == previousRow):
                    c = self.formatting[len(self.formatting)-1][0]                  # sets c to be color of previous formatter
                    start_index = self.formatting[len(self.formatting)-1][1][0]
                    end_index = self.formatting[len(self.formatting)-1][1][1] + 1   # increase end_index by one
                    newFormatter = (c,(start_index,end_index))
                    self.formatting[len(self.formatting)-1] = newFormatter          # update previous formattter to apply for one additional index
                # Otherwise, add a new entry to formatting for this new color
                elif(colorCode == "r"):
                    color = "red"
                elif(colorCode == "g"):
                    color = "green"
                elif(colorCode == "b"):
                    color = "blue"
                elif(colorCode == "v"):
                    color = "purple"
                elif(colorCode == "y"):
                    color = "yellow"
                elif(colorCode == "o"):
                    color = "orange"
                elif(colorCode == "n"):
                    color = "brown"

                # add a new formatter to self.formatting only if this one is different than the previous one, or a new row
                if (previousColorCode != colorCode or row != previousRow):
                    self.formatting.append((color,(row*self.width+column,row*self.width+column)))
                previousColorCode = colorCode
                previousRow = row

        return self.pixels

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
            #    if (g.mapLocation[0] == 2 and g.mapLocation[1] == 2):
            #        GameState().enterArea('Aspire', 'townCenter')  # in place of the strings use values pulled from config files
            #        GameState().gameMode = GameMode.inAreaCommand


if __name__ == '__main__':
    AssetLoader().loadAssets()
    mapWindow = MapWindow(1280, 720)
    mapWindow.draw()
