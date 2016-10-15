"""
Window containing the world map.
"""
from window import Window
from game_state import GameState
from asset_loader import AssetLoader

class MapWindow(Window):
    def __init__(self, currentMap, width, height):
        super().__init__(width, height)
        loader = AssetLoader()
        assets = loader.loadAssets('assets/maps')
        self.map = assets[currentMap].splitlines()

    def update(self, timestep, keypresses):
        for key in keypresses:
            if key == "Up" or key == "w":
                pass
            elif key == "Left" or key == "a":
                pass
            elif key == "Down" or key == "s":
                pass
            elif key == "Right" or key == "d":
                pass
            elif key == "Return":
                pass

    def draw(self):
        for row in range(len(self.map)):
            for column in range(len(self.map[row])):
                self.pixels[row][column] = self.map[row][column]
        return self.pixels

if __name__ == '__main__':
    mapWindow = MapWindow('assets\\maps\\test_map.txt', 1280, 720)
    mapWindow.draw()
