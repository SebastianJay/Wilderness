"""
Window containing the world map.
"""
from window import Window
from game_state import GameState, GameMode
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
            self.maps.append(loader.getMap(threetup[0]))
            self.colorMasks.append(loader.getMap(threetup[1]))
            self.travelMasks.append(loader.getMap(threetup[2]))

        self.entrances = ([], [])
        areaConfig = loader.getConfig(Globals.AreasConfigPath)
        for area in areaConfig:
            entranceList = areaConfig[area]['entrances']
            mapId = areaConfig[area]['mapId']
            for entrance in entranceList:
                roomId = entrance['roomId']
                r = entrance['r']
                c = entrance['c']
                self.entrances[mapId].append((r, c, area, roomId))

    def draw(self):
        # make sure we have loaded
        if len(self.maps) == 0:
            return self.pixels

        # identify the current map we are looking at
        g = GameState()
        currentMap = self.maps[g.activeProtagonistInd]
        colorMask = self.colorMasks[g.activeProtagonistInd]
        entrances = self.entrances[g.activeProtagonistInd]

        startRow = min(max(g.mapLocation[0] - self.height // 2, 0), len(currentMap) - self.height - (self.height % 2))
        startCol = min(max(g.mapLocation[1] - self.width // 2, 0), len(currentMap[g.mapLocation[0]]) - self.width - (self.width % 2))

        # draw out the map and color it
        self.formatting = []
        previousColorCode = "null"
        previousRow = -1
        for i, row in enumerate(range(startRow, startRow + self.height)):
            for j, column in enumerate(range(startCol, startCol + self.width)):
                self.pixels[i][j] = currentMap[row][column]
                colorCode = colorMask[row][column]
                color = "white"
                # Check to see if the character is at this position
                # If so, character should be a white "@"
                if (g.mapLocation[0] == row and g.mapLocation[1] == column):
                    self.pixels[i][j] = '@'
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
                    self.formatting.append((color,(i*self.width+j,i*self.width+j)))
                previousColorCode = colorCode
                previousRow = row

        return self.pixels

    def overEntrance(self, r, c):
        for er, ec, areaId, roomId in self.entrances[GameState().activeProtagonistInd]:
            if er == r and ec == c:
                return (areaId, roomId)
        return False

    def update(self, timestep, keypresses):
        # make sure we have loaded
        if len(self.maps) == 0:
            return

        # identify the current map we are looking at
        g = GameState()
        currentMap = self.maps[g.activeProtagonistInd]
        currentTravel = self.travelMasks[g.activeProtagonistInd]

        if self.overEntrance(g.mapLocation[0], g.mapLocation[1]):
            g.gameMode = GameMode.worldMapOverArea
        else:
            g.gameMode = GameMode.worldMap

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
                val = self.overEntrance(g.mapLocation[0], g.mapLocation[1])
                if val:
                    GameState().enterArea(val[0], val[1], True)
                    GameState().gameMode = GameMode.inAreaCommand

if __name__ == '__main__':
    AssetLoader().loadAssets()
    mapWindow = MapWindow(1280, 720)
    mapWindow.draw()
