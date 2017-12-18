"""
A window displaying save file data and allowing the player to select a file
to load or delete files
"""
from window import Window
from game_state import GameState, GameMode
from asset_loader import AssetLoader
from global_vars import Globals

class SavesWindow(Window):

    def reset(self):
        self.fileData = []
        self.pointingTo = 0
        self.otherOptions = ['Delete File', 'Go Back']
        self.marginRows = 3  # space for header text and footer options
        self.inDeleteMode = False

    def resetCursor(self):
        self.pointingTo = 0
        while self.pointingTo < len(self.fileData) and self.fileData[self.pointingTo] is None:
            self.pointingTo += 1

    def load(self):
        self.fileData = []
        for path in Globals.SavePaths:
            obj = AssetLoader().getSave(path)
            if obj:
                self.fileData.append(obj)
            else:
                self.fileData.append(None)
        self.resetCursor()

    def update(self, timestep, keypresses):
        def updateCursor(delta):
            while True:
                self.pointingTo = (self.pointingTo + delta) % (len(self.fileData) + len(self.otherOptions))
                if self.pointingTo >= len(self.fileData) or self.fileData[self.pointingTo] is not None:
                    break

        for key in keypresses:
            if key == "Up":
                updateCursor(-1)
            elif key == "Down":
                updateCursor(1)
            elif key == "Return":
                if self.pointingTo < len(self.fileData):
                    if not self.inDeleteMode:
                        GameState().load(self.fileData[self.pointingTo])
                        GameState().saveId = self.pointingTo
                        GameState().gameMode = GameMode.InAreaCommand
                    else:
                        AssetLoader().deleteSave(self.pointingTo)
                        self.fileData[self.pointingTo] = None
                        self.inDeleteMode = False
                        updateCursor(1)
                else:
                    option = self.otherOptions[self.pointingTo - len(self.fileData)]
                    if option == 'Delete File':
                        self.inDeleteMode = not self.inDeleteMode
                        self.resetCursor()
                    elif option == 'Go Back':
                        GameState().gameMode = GameMode.TitleScreen
                break

    def draw(self):
        self.clear()
        # draw the header text
        header = 'Select which file?' if not self.inDeleteMode else 'Delete which file?'
        self.writeText(header, 1, (self.width - len(header)) // 2)

        # draw the option text
        optionText = self.otherOptions[:]
        if self.inDeleteMode:
            optionText[optionText.index('Delete File')] = 'Cancel Delete'
        optionCol = (self.width - len(self.otherOptions[0])) // 2
        self.writeTextLines(optionText, self.height - self.marginRows, optionCol)

        # draw the loaded file info
        fileRowFunc = lambda i: (self.height - self.marginRows * 2) // len(self.fileData) * i + self.marginRows
        fileCol = self.width // 4
        for i, finfo in enumerate(self.fileData):
            if finfo is None:
                continue
            name = finfo['name']
            playtime = int(finfo['playtime'])
            ind = finfo['activeProtagonistInd']
            substate = finfo['subStates'][ind]
            areasConfig = AssetLoader().getConfig(Globals.AreasConfigPath)
            roomsConfig = AssetLoader().getConfig(areasConfig[substate['areaId']]['roomsConfig'])
            timeStr = '{:02}:{:02}:{:02}'.format(playtime // 3600, (playtime % 3600) // 60, (playtime % 60))
            progressStr = '{}.{}.{}'.format('Lore' if ind == 0 else 'Kipp',
                areasConfig[substate['areaId']]['name'],
                roomsConfig[substate['roomId']]['mapName'] \
                    if 'mapName' in roomsConfig[substate['roomId']] else roomsConfig[substate['roomId']]['name'])
            infoStr = name + (' ' * (16 - len(name))) \
                + timeStr + (' ' * (16 - len(timeStr))) \
                + progressStr
            self.writeText(infoStr, fileRowFunc(i), fileCol, False,
                'overstrike' if self.inDeleteMode and i == self.pointingTo else None)

        # draw the cursor
        if self.pointingTo < len(self.fileData):
            cursorCol = fileCol - 2
            self.setPixel('>', fileRowFunc(self.pointingTo), cursorCol)
        else:
            cursorRow = self.height - self.marginRows + (self.pointingTo - len(self.fileData))
            cursorCol = optionCol - 2
            self.setPixel('>', cursorRow, cursorCol)
