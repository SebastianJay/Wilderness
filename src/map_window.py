"""
Window containing the world map.
"""
from window import Window
from game_state import GameState

class MapWindow(Window):
    def __init__(self, width, height):
        super().__init__(width, height)

    def update(self, timestep, keypresses):
        pass

    def draw(self):
        pass
