"""
Definition for one window within game display. A window does not know
where it is within the game display; it simply formats its pixels based
on width and height fields
"""

class Window:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        #2D char array approach
        self.pixels = [['X' for x in range(self.width)] for y in range(self.height)]

    def update(self, timestep):
        pass

    def draw(self):

        return self.pixels
