"""
Definition for one window within game display. A window does not know
where it is within the game display; it simply formats its pixels based
on width and height fields
"""

class Window:
    def __init__(width, height):
        self._width = width
        self._height = height

        #2D char array approach
        self.pixels = [[' ' for y in range(self._height)] for x in range(self._width)]
