"""
Window containing the world map.
"""
from window import Window
from game_state import GameState, GameMode
from asset_loader import AssetLoader
from global_vars import Globals

class MapWindow(Window):

    ColorCodes = {
        'w': 'white',
        'r': 'red',
        'g': 'green',
        'b': 'blue',
        'v': 'purple',
        'y': 'yellow',
        'o': 'orange',
        'n': 'brown',
    }

    def reset(self):
        self.maps = []
        self.colorMasks = []
        self.travelMasks = []

    def load(self):
        self.maps = []
        self.colorMasks = []
        self.travelMasks = []
        loader = AssetLoader()
        for (mapPath, colorPath, travelPath) in Globals.MapsPaths:
            self.maps.append(loader.getMap(mapPath))
            self.colorMasks.append(loader.getMap(colorPath))
            self.travelMasks.append(loader.getMap(travelPath))

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

    def update(self, timestep, keypresses):
        if not AssetLoader().isLoaded:
            return

        # identify the current map we are looking at
        gs = GameState()
        currentMap = self.maps[gs.activeProtagonistInd]
        currentTravel = self.travelMasks[gs.activeProtagonistInd]

        val = self.overEntrance(gs.mapLocation[0], gs.mapLocation[1])
        if val:
            gs.gameMode = GameMode.WorldMapOverArea
        else:
            gs.gameMode = GameMode.WorldMap

        # process keystrokes to move player position
        for key in keypresses:
            if key == "Up" or key == "w":
                if gs.mapLocation[0] > 0 and len(currentMap[gs.mapLocation[0] - 1]) - 1 >= gs.mapLocation[1]:
                    if currentTravel[gs.mapLocation[0] - 1][gs.mapLocation[1]] == '0':
                        gs.mapLocation[0] -= 1
            elif key == "Left" or key == "a":
                if gs.mapLocation[1] > 0:
                    if currentTravel[gs.mapLocation[0]][gs.mapLocation[1] - 1] == '0':
                        gs.mapLocation[1] -= 1
            elif key == "Down" or key == "s":
                if gs.mapLocation[0] < len(currentMap) - 1 and len(currentMap[gs.mapLocation[0] + 1]) - 1 >= gs.mapLocation[1]:
                    if currentTravel[gs.mapLocation[0] + 1][gs.mapLocation[1]] == '0':
                        gs.mapLocation[0] += 1
            elif key == "Right" or key == "d":
                if gs.mapLocation[1] < len(currentMap[gs.mapLocation[0]]) - 1:
                    if currentTravel[gs.mapLocation[0]][gs.mapLocation[1] + 1] == '0':
                        gs.mapLocation[1] += 1
            elif key == "Return" and val:
                GameState().gameMode = GameMode.InAreaCommand
                GameState().enterArea(val[0], val[1], True)

    def draw(self):
        if not AssetLoader().isLoaded:
            return
        self.clear()

        # identify the current map we are looking at
        gs = GameState()
        currentMap = self.maps[gs.activeProtagonistInd]
        colorMask = self.colorMasks[gs.activeProtagonistInd]
        entrances = self.entrances[gs.activeProtagonistInd]

        mapHeight = self.height - 2
        startMapRow = min(max(gs.mapLocation[0] - mapHeight // 2, 0),
            len(currentMap) - mapHeight - (mapHeight % 2))
        startMapCol = min(max(gs.mapLocation[1] - self.width // 2, 0),
            len(currentMap[gs.mapLocation[0]]) - self.width - (self.width % 2))

        # draw the map
        mapString = '\n'.join([line[startMapCol:startMapCol + self.width] \
            for line in currentMap[startMapRow:startMapRow + mapHeight]])
        self.writeText(mapString, 1, 0)

        # draw the character's position
        self.setPixel('@', gs.mapLocation[0] - startMapRow + 1, gs.mapLocation[1] - startMapCol)

        # add formatting based on the color mask
        # to reduce number of tkinter insert calls, look for runs of the same color on same row
        colorLines = [line[startMapCol:startMapCol + self.width] \
            for line in colorMask[startMapRow:startMapRow + mapHeight]]
        for i, colorLine in enumerate(colorLines):
            # replace color mask value where character position is
            colorLineFormatted = colorLine[:gs.mapLocation[1] - startMapCol] \
                + 'w' + colorLine[gs.mapLocation[1] - startMapCol + 1:] \
                if i == gs.mapLocation[0] - startMapRow else colorLine
            # calculate indices where the color code changes
            colorChangeIndices = [0]
            for j in range(1, len(colorLineFormatted)):
                if colorLineFormatted[j] != colorLineFormatted[j - 1]:
                    colorChangeIndices.append(j)
            # add formatters for each color run
            for x, ind in enumerate(colorChangeIndices):
                self.addFormatting(MapWindow.ColorCodes[colorLineFormatted[ind]],
                    i + 1, ind, (colorChangeIndices[x + 1] if x < len(colorChangeIndices) - 1 else self.width) - ind)

        # if over an area entrance, draw header title and footer subtitle
        val = self.overEntrance(gs.mapLocation[0], gs.mapLocation[1])
        if val:
            title, subtitle = self.areaInfo[val[0]]
            self.writeText(title, 0, (self.width - len(title)) // 2, False, 'bold')
            self.writeText(subtitle, self.height - 1, (self.width - len(subtitle)) // 2)

    def overEntrance(self, r, c):
        for er, ec, areaId, roomId in self.entrances[GameState().activeProtagonistInd]:
            if er == r and ec == c:
                return (areaId, roomId)
        return False
