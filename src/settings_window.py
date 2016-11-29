"""
Allows for the customization of some basic options.
Displayed on first run and can also be accessed
through the title screen.
"""
from window import Window
from asset_loader import AssetLoader
import sys
import yaml

class SettingsWindow(Window):
    def __init__(self, width, height):
        super().__init__(width, height)
        self.pointingTo = [0, 0] # index of option player is looking at
        # Format: {Option name: ((option values), default value)}
        self.options = {'Font size': (('Small', 'Medium', 'Large'), 'Medium'),
                        'Scroll speed': (('Slow', 'Normal', 'Fast'), 'Normal'),
                        'Styled text': (('On', 'Off'), 'On')}
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

            self.numOptions.append(0)
            self.optionPositions.append([])

            # Draw the individual option values
            for value in self.options[option][0]:
                self.numOptions[row] += 1
                self.optionPositions[row].append((col, col + len(value) - 1))
                for char in list(value):
                    self.pixels[row][col] = char
                    col += 1
                self.pixels[row][col] = ' '
                col += 1
            row += 1

    def load(self):
        self.settings = AssetLoader().getConfig('settings.yml')
        settingsPath = AssetLoader().joinAndNorm('config', 'settings.yml')
        # We can't work on the actual dictionary as deleting keys during iteration isn't allowed,
        # so act on the list of the keys instead
        for setting in list(self.settings.keys()):
            if setting not in self.options:
                print(setting + ' is not in options, deleting')
                del self.settings[setting]
            else:
                pass # TODO: figure out the default value

    def update(self, timestep, keypresses):
        for key in keypresses:
            if key == "Up":
                self.pointingTo[0] = (self.pointingTo[0] - 1) % len(self.options)
                if self.numOptions[self.pointingTo[0]] <= self.pointingTo[1]:
                    self.pointingTo[1] = self.numOptions[self.pointingTo[0]] - 1
            elif key == "Down":
                self.pointingTo[0] = (self.pointingTo[0] + 1) % len(self.options)
                if self.numOptions[self.pointingTo[0]] <= self.pointingTo[1]:
                    self.pointingTo[1] = self.numOptions[self.pointingTo[0]] - 1
            elif key == "Left":
                self.pointingTo[1] = (self.pointingTo[1] - 1) % self.numOptions[self.pointingTo[0]]
            elif key == "Right":
                self.pointingTo[1] = (self.pointingTo[1] + 1) % self.numOptions[self.pointingTo[0]]
            elif key == "Return":
                continue

    def draw(self):
        self.formatting = [] # Clear any previous formatting
        # Beautiful.
        self.formatting.append(('underline', (self.pointingTo[0] * self.width + self.optionPositions[self.pointingTo[0]][self.pointingTo[1]][0], self.pointingTo[0] * self.width + self.optionPositions[self.pointingTo[0]][self.pointingTo[1]][1])))
        return self.pixels

if __name__ == '__main__':
    window = SettingsWindow(120, 35)
    window.debugDraw()
