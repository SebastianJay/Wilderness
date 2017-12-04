"""
Allows for the customization of some basic options.
Displayed on first run and can also be accessed
through the title screen.
"""
from window import Window
from game_state import GameState, GameMode
from asset_loader import AssetLoader
import sys
import yaml

class SettingsWindow(Window):
    def __init__(self, width, height):
        super().__init__(width, height)

    def reset(self):
        self.pointingTo = 0 # index of option (row) player is looking at
        # Format: (Option name, (option values))
        self.options = [('Font size', ('Tiny', 'Small', 'Medium', 'Large', 'Huge')),
                        ('Scroll speed', ('Slow', 'Normal', 'Fast')),
                        ('Styled text', ('On', 'Off')),
                        ('Background music', ('On', 'Off'))]
        self.optionIndices = [1, 1, 0, 0]      # default indices (columns) of each option
        self.optionPositions = []           # column locations of options
        self.startCol = self.width // 3
        self.marginRows = 3
        self.rowNum = lambda i: (self.height - self.marginRows * 2) // len(self.options) * i + self.marginRows

    def load(self):
        settings = AssetLoader().getSettings()
        if settings is not None:
            for setting in settings:
                if setting[0] == 'fontSize':
                    self.optionIndices[0] = setting[1]
                elif setting[0] == 'scrollSpeed':
                    self.optionIndices[1] = setting[1]
                elif setting[0] == 'styledText':
                    self.optionIndices[2] = setting[1]
                elif setting[0] == 'backgroundMusic':
                    self.optionIndices[3] = setting[1]

        for row, (option, values) in enumerate(self.options):
            col = self.startCol
            # Draw the option names (eg Font size)
            for char in option + ':  ':
                self.pixels[self.rowNum(row)][col] = char
                col += 1
            self.optionPositions.append([])

            # Draw the individual option values
            for value in values:
                self.optionPositions[row].append(col)
                for char in value + '  ':
                    self.pixels[self.rowNum(row)][col] = char
                    col += 1
        footer = '[Return] to exit'
        for c, ch in enumerate(footer):
            self.pixels[self.height - self.marginRows][(self.width - len(footer)) // 2 + c] = ch

    def update(self, timestep, keypresses):
        def camelCase(s):
            x = ''.join([word.capitalize() for word in s.split()])
            return x[0].lower() + x[1:]
        def packSettings():
            obj = []
            for i in range(len(self.options)):
                obj.append((camelCase(self.options[i][0]), self.optionIndices[i]))
            return obj
        def changeSetting(delta):
            self.optionIndices[self.pointingTo] = (self.optionIndices[self.pointingTo] + delta) \
                % len(self.options[self.pointingTo][1])
            option = camelCase(self.options[self.pointingTo][0])
            GameState().onSettingChange(option, self.optionIndices[self.pointingTo])

        for key in keypresses:
            if key == "Up":
                self.pointingTo = (self.pointingTo - 1) % len(self.options)
            elif key == "Down":
                self.pointingTo = (self.pointingTo + 1) % len(self.options)
            elif key == "Left":
                changeSetting(-1)
            elif key == "Right":
                changeSetting(1)
            elif key in [" ", "Return", "BackSpace"]:
                AssetLoader().writeSettings(packSettings()) # creates a file
                GameState().gameMode = GameMode.TitleScreen

    def draw(self):
        # draw cursor with arrow and option selections with brackets
        for i in range(len(self.options)):
            if i == self.pointingTo:
                self.pixels[self.rowNum(i)][self.startCol - 2] = ">"
            else:
                self.pixels[self.rowNum(i)][self.startCol - 2] = " "
            for j in range(len(self.options[i][1])):
                if j == self.optionIndices[i]:
                    self.pixels[self.rowNum(i)][self.optionPositions[i][j]-1] = "["
                    self.pixels[self.rowNum(i)][self.optionPositions[i][j]+len(self.options[i][1][j])] = "]"
                else:
                    self.pixels[self.rowNum(i)][self.optionPositions[i][j]-1] = " "
                    self.pixels[self.rowNum(i)][self.optionPositions[i][j]+len(self.options[i][1][j])] = " "
        return self.pixels

if __name__ == '__main__':
    window = SettingsWindow(120, 35)
    window.debugDraw()
