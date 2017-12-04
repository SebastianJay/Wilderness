"""
Window containing the world map.
"""
from window import Window
from game_state import GameState, GameMode
from asset_loader import AssetLoader
from global_vars import Globals
from lang_interpreter import Interpreter

class InAreaWindow(Window):
    def __init__(self, width, height):
        super().__init__(width, height)
        GameState().onEnterRoom += self.enterRoomHandler()

    def enterRoomHandler(self):
        def _enterRoomHandler(*args, **kwargs):
            gs = GameState()
            areaId = gs.areaId
            roomId = args[1]
            # set cursor to new room location
            if roomId in self.mapsData[areaId]:
                self.mapCursor = [self.mapsData[areaId][roomId][2], self.mapsData[areaId][roomId][3]]
        return _enterRoomHandler

    def load(self):
        self.mapCursor = [0, 0]

        loader = AssetLoader()
        self.maps = {}
        self.mapsData = {}
        areasConfig = loader.getConfig(Globals.AreasConfigPath)
        for area in areasConfig:
            self.maps[area] = loader.getMap(areasConfig[area]['inAreaMap'])
            self.mapsData[area] = {}
            roomsConfig = loader.getConfig(areasConfig[area]['roomsConfig'])
            for room in roomsConfig:
                # mapsData maps string area id * string room id ->
                # [0] string readable name of room
                # [1] string description of room
                # [2] int row number of room's tile on map
                # [3] int col number of room's tile on map
                # [4] string conditional if conditions must be fulfilled to show room, else None
                self.mapsData[area][room] = (
                    roomsConfig[room]['mapName'] if 'mapName' in roomsConfig[room] \
                        else roomsConfig[room]['name'],
                    roomsConfig[room]['description'],
                    roomsConfig[room]['r'],
                    roomsConfig[room]['c'],
                    roomsConfig[room]['showIf'] if 'showIf' in roomsConfig[room] else None,
                )

    def update(self, timestep, keypresses):
        # make sure we have loaded
        if len(self.mapsData) == 0:
            return

        # identify the current map we are looking at
        currentMap = self.maps[GameState().areaId]

        # process keystrokes to move player position
        # TODO DRY up with map_window.py
        for key in keypresses:
            newCursor = self.mapCursor[:]
            if key == "Up" or key == "w":
                if self.mapCursor[0] > 0 and len(currentMap[self.mapCursor[0] - 1]) - 1 >= self.mapCursor[1]:
                    newCursor[0] -= 1
            elif key == "Left" or key == "a":
                if self.mapCursor[1] > 0:
                    newCursor[1] -= 1
            elif key == "Down" or key == "s":
                if self.mapCursor[0] < len(currentMap) - 1 and len(currentMap[self.mapCursor[0] + 1]) - 1 >= self.mapCursor[1]:
                    newCursor[0] += 1
            elif key == "Right" or key == "d":
                if self.mapCursor[1] < len(currentMap[self.mapCursor[0]]) - 1:
                    newCursor[1] += 1
            elif key == "Return":
                # exit back to main game
                GameState().gameMode = GameMode.InAreaCommand
                break
            if currentMap[newCursor[0]][newCursor[1]] != '@':   # tile with @ cannot be hovered over
                self.mapCursor = newCursor

    def draw(self):
        # make sure we have loaded
        if len(self.mapsData) == 0:
            return self.pixels
        self.clear()
        areaId = GameState().areaId
        roomId = GameState().roomId

        # identify the current map we are looking at
        currentMap = self.maps[areaId]
        currentMapData = self.mapsData[areaId]

        # draw out the map
        startRow = (self.height - len(currentMap)) // 2 + 3
        startCol = (self.width - len(currentMap[0])) // 2
        for row in range(len(currentMap)):
            for column in range(len(currentMap[row])):
                if currentMap[row][column] == '@':  # the @ char is rendered as space
                    self.pixels[startRow + row][startCol + column] = ' '
                else:
                    self.pixels[startRow + row][startCol + column] = currentMap[row][column]

        # overlay the title and description if we are hovering over a room that is visible
        for room in currentMapData:
            if self.mapCursor[0] == currentMapData[room][2] and self.mapCursor[1] == currentMapData[room][3]:
                if currentMapData[room][4] is None or Interpreter().evaluateCondition(currentMapData[room][4].split('_')):
                    name = currentMapData[room][0]
                    desc = currentMapData[room][1]
                    titleCol = (self.width - len(name)) // 2
                    for j, ch in enumerate(name):
                        self.pixels[0][titleCol + j] = ch
                    # underline the title
                    self.formatting.append(('underline', (titleCol, titleCol+len(name)-1)))
                    lines = []
                    while True:
                        end_ind = len(desc) if len(desc) < self.width-2 else desc.rfind(' ', 0, self.width-2)
                        lines.append(desc[:end_ind])
                        desc = desc[end_ind+1:]
                        if desc == '':
                            break
                    for i, line in enumerate(lines):
                        for j, ch in enumerate(line):
                            self.pixels[1+i][1+j] = ch
                    break

        # overlay the cursor position
        self.pixels[startRow + self.mapCursor[0]][startCol + self.mapCursor[1]] = '@'

        # make character location a yellow tile on map
        if roomId in currentMapData:
            formatTile = (startRow+currentMapData[roomId][2])*self.width + (startCol+currentMapData[roomId][3])
            self.formatting.append(('yellow', (formatTile, formatTile)))
        return self.pixels

if __name__ == '__main__':
    AssetLoader().loadAssets()
    inareawindow = InAreaWindow(120, 35)
    inareawindow.draw()
