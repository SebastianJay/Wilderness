"""
Allows for the customization of some basic options.
Displayed on first run and can also be accessed
through the title screen.
"""
from window import Window
import sys

class SettingsWindow(Window):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.pointingTo = [0, 0] # index of option player is looking at
        self.options = {'Font size': ('Small', 'Medium', 'Large'),
                        'Scroll speed': ('Slow', 'Normal', 'Fast'),
                        'Styled text': ('On', 'Off')}
        self.numOptions = []
        self.optionPositions = []
        row = 0
        for option in self.options:
            col = 0
            # Draw the option names (eg Font size)
            for char in option:
                self.pixels[row][col] = char
                col += 1
            self.pixels[row][col] = ':'
            col += 1
            self.pixels[row][col] = ' '
            col += 1

            # Draw the individual option values
            for value in self.options[option]:
                for char in list(value):
                    self.pixels[row][col] = char
                    col += 1
                self.pixels[row][col] = ' '
                col += 1
            row += 1

    def update(self, timestep, keypresses):
        for key in keypresses:
            if key == "Up":
                self.pointingTo = (self.pointingTo - 1) % len(self.options)
            elif key == "Down":
                self.pointingTo = (self.pointingTo + 1) % len(self.options)
            elif key == "Return":
                continue

    def draw(self):
        # Clear previous cursor
        for row, temp in enumerate(self.options):
            self.pixels[row][0] = " "
        # Draw current cursor
        self.pixels[self.pointingTo][0] = ">"
        return self.pixels

if __name__ == '__main__':
    window = SettingsWindow(120, 35)
    window.debugDraw()
