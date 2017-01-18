"""
Window containing the world map.
"""
from window import Window
from game_state import GameState, GameMode
from asset_loader import AssetLoader
from global_vars import Globals

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
                self.mapsData[area][room] = (
                    roomsConfig[room]['name'],
                    roomsConfig[room]['description'],
                    roomsConfig[room]['r'],
                    roomsConfig[room]['c'],
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
            if key == "Up" or key == "w":
                if self.mapCursor[0] > 0 and len(currentMap[self.mapCursor[0] - 1]) - 1 >= self.mapCursor[1]:
                    self.mapCursor[0] -= 1
            elif key == "Left" or key == "a":
                if self.mapCursor[1] > 0:
                    self.mapCursor[1] -= 1
            elif key == "Down" or key == "s":
                if self.mapCursor[0] < len(currentMap) - 1 and len(currentMap[self.mapCursor[0] + 1]) - 1 >= self.mapCursor[1]:
                    self.mapCursor[0] += 1
            elif key == "Right" or key == "d":
                if self.mapCursor[1] < len(currentMap[self.mapCursor[0]]) - 1:
                    self.mapCursor[1] += 1
            elif key == "Return":
                GameState().gameMode = GameMode.inAreaCommand

    def draw(self):
        # make sure we have loaded
        if len(self.mapsData) == 0:
            return self.pixels
        self.clear()

        # identify the current map we are looking at
        currentMap = self.maps[GameState().areaId]
        currentMapData = self.mapsData[GameState().areaId]

        # draw out the map
        startRow = (self.height - len(currentMap)) // 2
        startCol = (self.width - len(currentMap[0])) // 2
        for row in range(len(currentMap)):
            for column in range(len(currentMap[row])):
                self.pixels[startRow + row][startCol + column] = currentMap[row][column]

        # overlay the title and description
        for room in currentMapData:
            if self.mapCursor[0] == currentMapData[room][2] and self.mapCursor[1] == currentMapData[room][3]:
                name = currentMapData[room][0]
                desc = currentMapData[room][1]
                for j, ch in enumerate(name):
                    self.pixels[0][(self.width - len(name)) // 2 + j] = ch
                lines = []
                while True:
                    end_ind = len(desc) if len(desc) < self.width else desc.rfind(' ', 0, self.width)
                    lines.append(desc[:end_ind])
                    desc = desc[end_ind+1:]
                    if desc == '':
                        break
                for i, line in enumerate(lines):
                    for j, ch in enumerate(line):
                        self.pixels[1+i][j] = ch
                break

        # overlay the character's position
        self.pixels[startRow + self.mapCursor[0]][startCol + self.mapCursor[1]] = '@'
        return self.pixels

if __name__ == '__main__':
    AssetLoader().loadAssets()
    inareawindow = InAreaWindow(120, 35)
    inareawindow.draw()
