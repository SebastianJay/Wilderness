from window import Window
from game_state import GameState, GameMode
from asset_loader import AssetLoader
from global_vars import Globals

class SavesWindow(Window):

    def __init__(self, width, height):
        super().__init__(width, height)
        self.fileinfo = []
        self.otherOptions = ['Delete File', 'Go Back']
        self.marginRows = 3  # space for header text and footer options
        self.rowNum = lambda i: (self.height - self.marginRows * 2) // len(self.fileinfo) * i + self.marginRows

    def reset(self):
        self.resetCursor()
        self.inDeleteMode = False

    def resetCursor(self):
        self.pointingTo = 0
        if hasattr(self, 'fileinfo'):
            while self.pointingTo < len(self.fileinfo) and self.fileinfo[self.pointingTo] is None:
                self.pointingTo += 1

    def load(self):
        self.fileinfo = []
        for path in Globals.SavePaths:
            obj = AssetLoader().getSave(path)
            if obj:
                self.fileinfo.append(obj)
            else:
                self.fileinfo.append(None)
        self.resetCursor()

    def draw(self):
        self.clear()
        # draw the header text
        header = 'Select which file?' if not self.inDeleteMode else 'Delete which file?'
        rHeader = 1
        cHeader = (self.width - len(header)) // 2
        for c, ch in enumerate(header):
            self.pixels[rHeader][cHeader + c] = ch

        # draw the option text
        cOption = (self.width - len(self.otherOptions[0])) // 2
        for i, optionText in enumerate(self.otherOptions):
            row = self.height - self.marginRows + i
            text = optionText
            if optionText == 'Delete File': # the delete option changes text
                text = 'Delete File' if not self.inDeleteMode else 'Cancel Delete'
            for c, ch in enumerate(text):
                self.pixels[row][cOption + c] = ch

        # draw the loaded file info
        startCol = self.width // 3
        for i in range(len(self.fileinfo)):
            if self.fileinfo[i] is None:
                continue
            name = self.fileinfo[i]['name']
            playtime = int(self.fileinfo[i]['playtime'])
            infoStr = name + (' ' * (16 - len(name))) \
                + '{:02}:{:02}:{:02}'.format(playtime // 3600, (playtime % 3600) // 60, (playtime % 60))
            for j, ch in enumerate(infoStr):
                self.pixels[self.rowNum(i)][startCol + j] = ch

        # draw the cursor
        cursorCol = self.width // 3 - 2
        for i in range(len(self.fileinfo)):
            row = self.rowNum(i)
            if i == self.pointingTo:
                self.pixels[row][cursorCol] = ">"
            else:
                self.pixels[row][cursorCol] = " "
        cursorCol = (self.width - len(self.otherOptions[0])) // 2 - 2
        for i in range(len(self.otherOptions)):
            row = self.height - self.marginRows + i
            if i+len(self.fileinfo) == self.pointingTo:
                self.pixels[row][cursorCol] = ">"
            else:
                self.pixels[row][cursorCol] = " "
        return self.pixels

    def update(self, timestep, keypresses):
        def updateCursor(delta):
            while True:
                self.pointingTo = (self.pointingTo + delta) % (len(self.fileinfo) + len(self.otherOptions))
                if self.pointingTo >= len(self.fileinfo) or self.fileinfo[self.pointingTo] is not None:
                    break

        for key in keypresses:
            if key == "Up":
                updateCursor(-1)
            elif key == "Down":
                updateCursor(1)
            elif key == "Return":
                if self.pointingTo < len(self.fileinfo):
                    if not self.inDeleteMode:
                        GameState().load(self.fileinfo[self.pointingTo])
                        GameState().saveId = self.pointingTo
                        GameState().gameMode = GameMode.inAreaCommand
                    else:
                        AssetLoader().deleteSave(self.pointingTo)
                        self.fileinfo[self.pointingTo] = None
                        self.inDeleteMode = False
                        updateCursor(1)
                else:
                    option = self.otherOptions[self.pointingTo - len(self.fileinfo)]
                    if option == 'Delete File':
                        self.inDeleteMode = not self.inDeleteMode
                        self.resetCursor()
                    elif option == 'Go Back':
                        GameState().gameMode = GameMode.titleScreen
                break
