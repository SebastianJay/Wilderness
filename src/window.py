"""
Definition for one window within game display. A window does not know
where it is within the game display; it simply formats its pixels based
on width and height fields
"""

class Window:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        #initialize 2D char array
        self.pixels = [[' ' for x in range(self.width)] for y in range(self.height)]

    def update(self, timestep, keypresses):
        """
        Given a timestep in seconds and a list of keystrokes during this update,
        make changes to GameState or the window state itself
        """
        pass

    def draw(self):
        """
        Pull from GameState (if needed) to update 2D pixel array
        """
        return self.pixels

    def debugDraw(self):
        """
        Displays the pixels matrix to shell using print()
        """
        self.draw() #refresh the pixels state
        for i in range(0, self.height):
            if not i == 0: print()
            for j in range(0, self.width):
                print(self.pixels[i][j], end="")
        print()
