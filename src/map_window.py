"""
Window containing the world map.
"""
from window import Window
from game_state import GameState
from asset_loader import AssetLoader

class MapWindow(Window):
    def __init__(self, width, height):
        super().__init__(width, height)
        loader = AssetLoader()
        assets = loader.loadAssets('assets/maps')
        currentMap = 'assets\\maps\\test_map'   #TODO move this elsewhere
        self.map = assets[currentMap + '.txt'].splitlines()
        self.travelMask = assets[currentMap + '_travel_mask.txt'].splitlines()
        self.location = [0, 0] # TODO: Get this from GameState instead

    def update(self, timestep, keypresses):
        for key in keypresses:
            if key == "Up" or key == "w":
                if self.location[0] > 0 and len(self.map[self.location[0] - 1]) - 1 >= self.location[1]:
                    if self.travelMask[self.location[0] - 1][self.location[1]] == '0':
                        self.location[0] -= 1
            elif key == "Left" or key == "a":
                if self.location[1] > 0:
                    if self.travelMask[self.location[0]][self.location[1] - 1] == '0':
                        self.location[1] -= 1
            elif key == "Down" or key == "s":
                if self.location[0] < len(self.map) - 1 and len(self.map[self.location[0] + 1]) - 1 >= self.location[1]:
                    if self.travelMask[self.location[0] + 1][self.location[1]] == '0':
                        self.location[0] += 1
            elif key == "Right" or key == "d":
                if self.location[1] < len(self.map[self.location[0]]) - 1:
                    if self.travelMask[self.location[0]][self.location[1] + 1] == '0':
                        self.location[1] += 1
            elif key == "Return":
                # TODO
                pass

    def draw(self):
        for row in range(len(self.map)):
            for column in range(len(self.map[row])):
                self.pixels[row][column] = self.map[row][column]
        # TODO: Differentiate between Lore and Kipp maybe?
        self.pixels[self.location[0]][self.location[1]] = '@'
        return self.pixels

if __name__ == '__main__':
    mapWindow = MapWindow(1280, 720, 'assets\\maps\\test_map')
    mapWindow.draw()
