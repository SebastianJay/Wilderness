"""
Definition for one window within game display. A window does not know
where it is within the game display; it simply formats its pixels based
on width and height fields
"""

class Window:
    def __init__(self, width, height):
        """
        Any onetime setup (e.g. registering event handlers) goes in __init__.
        Initializing fields which may be reinitialized on restarting game goes in reset()
        """
        self.width = width
        self.height = height

        # initialize 2D char array
        self.pixels = [[' ' for x in range(self.width)] for y in range(self.height)]
        # initialize color/style formatting info
        self.formatting = []    # each element is (tag, (start_index, end_index))
        # degree of transparency (0 = opaque, Globals.AlphaMax = transparent)
        # NOTE as of now, only used in WindowManager
        self.alphaLevel = 0
        # initialize other fields
        self.reset()

    def __hash__(self):
        """
        Hash used for dirty checking a window on a draw call
        """
        return hash(('\n'.join([''.join(row) for row in self.pixels]), tuple(self.formatting), self.alphaLevel))

    def reset(self):
        """
        Initialize pointers and other window specific state data which gets reset on game restart
        """
        pass

    def load(self):
        """
        Any initialization that requires AssetLoader should be deferred to this method
        """
        pass

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

    def clear(self):
        """
        Utility method to clear pixels to blank (' ') strings and empty formatting
        """
        self.formatting = []
        for i in range(self.height):
            for j in range(self.width):
                self.pixels[i][j] = ' '

    def refresh(self):
        """
        A helper method for resetting and reloading the Window
        """
        self.clear()
        self.reset()
        self.load()

    def debugDraw(self):
        """
        Displays the pixels matrix to shell using print()
        """
        self.draw() #refresh the pixels state
        for i in range(0, self.height):
            if not i == 0: print()
            for j in range(0, self.width):
                print(self.pixels[i][j], end= "")
        print()
