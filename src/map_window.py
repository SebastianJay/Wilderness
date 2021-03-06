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
        self.areaInfo = {}
        areaConfig = loader.getConfig(Globals.AreasConfigPath)
        for area in areaConfig:
            entranceList = areaConfig[area]['entrances']
            mapId = areaConfig[area]['mapId']
            for entrance in entranceList:
                roomId = entrance['roomId']
                r = entrance['r']
                c = entrance['c']
                # self.entrances has two lists, one per world, with tuples formatted as
                #  [0] int row of tile with entrance
                #  [1] int col of tile with entrance
                #  [2] string area id
                #  [3] string room id
                self.entrances[mapId].append((r, c, area, roomId))
                # self.areaInfo maps area id -> (string title, string subtitle)
                self.areaInfo[area] = (areaConfig[area]['name'], areaConfig[area]['subtitle'] \
                    if 'subtitle' in areaConfig[area] else '')

    def draw(self):
        # make sure we have loaded
        if len(self.maps) == 0:
            return self.pixels
        self.clear()

        # identify the current map we are looking at
        g = GameState()
        currentMap = self.maps[g.activeProtagonistInd]
        colorMask = self.colorMasks[g.activeProtagonistInd]
        entrances = self.entrances[g.activeProtagonistInd]

        mapHeight = self.height - 2
        startRow = min(max(g.mapLocation[0] - mapHeight // 2, 0), len(currentMap) - mapHeight - (mapHeight % 2))
        startCol = min(max(g.mapLocation[1] - self.width // 2, 0), len(currentMap[g.mapLocation[0]]) - self.width - (self.width % 2))

        # draw out the map and color it
        previousColorCode = "null"
        previousRow = -1
        for i, row in enumerate(range(startRow, startRow + mapHeight)):
            for j, column in enumerate(range(startCol, startCol + self.width)):
                mapRow = i + 1
                pixel = currentMap[row][column]
                colorCode = colorMask[row][column]
                color = "white"
                # Check to see if the character is at this position
                # If so, character should be a white "@"
                if (g.mapLocation[0] == row and g.mapLocation[1] == column):
                    pixel = '@'
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
                    self.formatting.append((color,(mapRow*self.width+j,mapRow*self.width+j)))
                self.pixels[mapRow][j] = pixel
                previousColorCode = colorCode
                previousRow = row

        # if over an area entrance, draw header title and footer subtitle
        val = self.overEntrance(g.mapLocation[0], g.mapLocation[1])
        if val:
            title, subtitle = self.areaInfo[val[0]]
            titleCol = (self.width - len(title)) // 2
            subtitleCol = (self.width - len(subtitle)) // 2
            for j, ch in enumerate(title):
                self.pixels[0][titleCol + j] = ch
            self.formatting = [('bold', (titleCol, titleCol+len(title)-1))] + self.formatting
            for j, ch in enumerate(subtitle):
                self.pixels[self.height-1][subtitleCol + j] = ch
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

        val = self.overEntrance(g.mapLocation[0], g.mapLocation[1])
        if val:
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
            elif key == "Return" and val:
                GameState().gameMode = GameMode.inAreaCommand
                GameState().enterArea(val[0], val[1], True)

if __name__ == '__main__':
    AssetLoader().loadAssets()
    mapWindow = MapWindow(1280, 720)
    mapWindow.draw()
