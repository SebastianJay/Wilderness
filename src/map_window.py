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

    def update(self, timestep, keypresses):
        pass

    def draw(self):
        pass

if __name__ == '__main__':
    mapWindow = MapWindow('test_map.txt', 1280, 720)
