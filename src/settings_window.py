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

    def reset(self):
        # index of option (row) player is looking at
        self.pointingTo = 0
        # options to render on screen
        # Format: (Option name, (option values))
        self.options = [('Font size', ('Tiny', 'Small', 'Medium', 'Large', 'Huge')),
                        ('Scroll speed', ('Slow', 'Normal', 'Fast')),
                        ('Styled text', ('On', 'Off')),
                        ('Background music', ('On', 'Off'))]
        # default indices (columns) of each option
        self.optionIndices = [1, 1, 0, 0]
        # number of rows to leave at margin on top and bottom
        self.marginRows = 3

    def load(self):
        settings = AssetLoader().getSettings()
        if settings is None:
            return

        optionNames = [SettingsWindow.CamelCase(option) for (option, _) in self.options]
        for setting in settings:
            if setting[0] not in optionNames:
                continue
            self.optionIndices[optionNames.index(setting[0])] = setting[1]

    def update(self, timestep, keypresses):
        def changeSetting(delta):
            self.optionIndices[self.pointingTo] = (self.optionIndices[self.pointingTo] + delta) \
                % len(self.options[self.pointingTo][1])
            option = SettingsWindow.CamelCase(self.options[self.pointingTo][0])
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
                # create a file with the packed settings before leaving settings
                settings = [(SettingsWindow.CamelCase(self.options[i][0]), self.optionIndices[i])
                    for i in range(len(self.options))]
                AssetLoader().writeSettings(settings)
                GameState().gameMode = GameMode.TitleScreen

    def draw(self):
        self.clear()

        startCol = self.width // 3
        optionRowFunc = lambda i: (self.height - self.marginRows * 2) // len(self.options) * i + self.marginRows

        # draw options with selections in brackets
        for i, (option, values) in enumerate(self.options):
            formattedValues = [' ' + value + ' ' for value in values]
            formattedValues[self.optionIndices[i]] = '[' + formattedValues[self.optionIndices[i]].strip() + ']'
            fullLine = option + ': ' + ''.join(formattedValues)
            self.writeText(fullLine, optionRowFunc(i), startCol)

        # draw cursor
        self.setPixel('>', optionRowFunc(self.pointingTo), startCol - 2)

        # draw footer
        footer = '[Return] to exit'
        self.writeText(footer, self.height - self.marginRows, (self.width - len(footer)) // 2)

    # helper for settings serialization
    def CamelCase(s):
        x = ''.join([word.capitalize() for word in s.split()])
        return x[0].lower() + x[1:]
