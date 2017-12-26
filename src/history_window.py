"""
Window containing the history/feedback of a player's actions. The content of
the game is exposed through this window.
"""
from window import Window
from game_state import GameState, GameMode
from global_vars import Globals

class HistoryWindow(Window):

    class SubState:
        """ History Window vars specific to one protagonist's history buffer """
        def __init__(self):
            # The current number of characters (exclude newlines) that can be displayed
            self.charLimit = 0
            # Index of line to start displaying in window
            self.startingLine = 0
            # Mappings of char indices in history buffer for particular rows
            self.rowIndices = []

    def __init__(self, width, height):
        super().__init__(width, height)
        # register handler for additions to history buffer
        GameState().onAddLangNode += self.langNodeAddedHandler()
        # register handler for clearing out buffer vars when area resets
        GameState().onClearBuffer += self.clearBufferHandler()
        # register handler for game settings change
        GameState().onSettingChange += self.settingsChangeHandler()

    def reset(self):
        # Tracks the time since the last character was displayed
        self.timestep = 0.0
        # Delay in seconds before each character appears on-screen
        self.threshold = 0.025
        # Speedup factor for the text animation when "speed" button pressed
        self.speedButtonFactor = 5.0
        # Factor for additional time special chars like period take
        self.speedPeriodFactor = 0.15
        # flag indicating animation completion on next draw
        self.unlockOnNextUpdate = False

        # State is maintained in window for each protagonist
        self.subStates = [
            HistoryWindow.SubState(),
            HistoryWindow.SubState(),
        ]

    def langNodeAddedHandler(self):
        def _langNodeAddedHandler(*args, **kwargs):
            # do word wrapping logic whenever an update has been made to history buffer
            addedText = args[0]
            outputIndices = []
            seekIndex = 0
            previousBufferLength = len(GameState().historyBuffer) - len(addedText)

            # record the start of each new line in the window
            while seekIndex < len(addedText):
                outputIndices.append(seekIndex + previousBufferLength)
                newlineIndex = addedText.find('\n', seekIndex)
                wordBreakIndex = len(addedText) if len(addedText[seekIndex:]) < self.width \
                    else max(addedText.rfind(' ', seekIndex, seekIndex + self.width + 1),
                        addedText.rfind('\n', seekIndex, seekIndex + self.width + 1))
                seekIndex = (newlineIndex if newlineIndex != -1 and newlineIndex < wordBreakIndex \
                    else (wordBreakIndex if wordBreakIndex != -1 else (seekIndex + self.width - 1))) + 1

            self.rowIndices.extend(outputIndices)

            # second arg indicates whether to animate
            if len(args) == 1 or not args[1]:
                # switch out game mode until animation finished
                GameState().lockGameMode(GameMode.InAreaAnimating)
            else:
                # advance pointers as if animation complete
                self.charLimit = len(GameState().historyBuffer)
                self.startingLine = max(len(self.rowIndices) - self.height, 0)
        return _langNodeAddedHandler

    def clearBufferHandler(self):
        def _clearBufferHandler(*args, **kwargs):
            self.subStates[GameState().activeProtagonistInd] = HistoryWindow.SubState()
        return _clearBufferHandler

    def settingsChangeHandler(self):
        speedMapping = {
            0: Globals.DefaultScrollThreshold + 0.015,
            1: Globals.DefaultScrollThreshold,
            2: Globals.DefaultScrollThreshold - 0.015,
        }
        def _settingsChangeHandler(*args, **kwargs):
            if args[0] == 'scrollSpeed':
                self.threshold = speedMapping[args[1]]
        return _settingsChangeHandler

    def update(self, timestep, keypresses):
        # increment charLimit in certain time increments to advance scrolling animation
        if GameState().gameMode == GameMode.InAreaAnimating:
            if self.unlockOnNextUpdate:
                self.unlockOnNextUpdate = False
                GameState().unlockGameMode()
                return

            self.timestep += timestep
            speedFlag = False
            skipFlag = False
            historyBuffer = GameState().historyBuffer

            # scan for keys that speed up animation
            for key in keypresses:
                if key == ' ':
                    speedFlag = True
                elif key == 'Next' and Globals.IsDev:
                    skipFlag = True
                    break
            if not skipFlag:
                # add as many characters as possibly allowed by new timestep
                while True:
                    speedMultiple = 1.0 if not speedFlag else self.speedButtonFactor
                    ch = historyBuffer[self.charLimit-1] if 0 < self.charLimit < len(historyBuffer) else ''
                    if ch == '.':
                        speedMultiple *= self.speedPeriodFactor
                    if self.timestep > self.threshold / speedMultiple:
                        self.timestep -= self.threshold / speedMultiple
                        self.charLimit += 1
                    else:
                        break

            # check if animation is complete
            if self.charLimit >= len(historyBuffer) or skipFlag:
                self.charLimit = len(historyBuffer)
                self.unlockOnNextUpdate = True

            # update starting line based on where the animation index is at
            lineIndex = 0
            while lineIndex < len(self.rowIndices) and self.rowIndices[lineIndex] < self.charLimit:
                lineIndex += 1
            self.startingLine = max(lineIndex - self.height, 0)
        else:
            # Only allow scrolling if we're not writing text to the screen
            for key in keypresses:
                if key == "Prior":
                    if self.startingLine > 0:
                        self.startingLine -= 1
                elif key == "Next":
                    if self.startingLine + self.height < len(self.rowIndices):
                        self.startingLine += 1

    def draw(self):
        self.clear()

        # wrap text based on the calculated indices and write lines to screen
        windowRowIndices = self.rowIndices[self.startingLine : self.startingLine + self.height]
        wrappedText = []
        for i, rowStartIndex in enumerate(windowRowIndices):
            rowEndIndex = self.rowIndices[self.startingLine + i + 1] \
                if self.startingLine + i < len(self.rowIndices) - 1 \
                else len(GameState().historyBuffer)
            lineEndIndex = min(rowEndIndex, self.charLimit)
            wrappedText.append(GameState().historyBuffer[rowStartIndex:lineEndIndex].rstrip())
            if lineEndIndex == self.charLimit:
                break
        self.writeTextLines(wrappedText, 0, 0)

        # take a subset of the formatting which is shown on screen
        row = 0
        for (tag, (ind1, ind2)) in GameState().historyFormatting:
            # ignore formatters outside of range of window
            if ind1 >= self.charLimit:
                break
            if ind2 < self.rowIndices[self.startingLine]:
                continue
            # adjust running counter of line the formatter is on
            while self.startingLine + row + 1 < len(self.rowIndices) \
                and self.rowIndices[self.startingLine + row + 1] <= ind1:
                row += 1
            # stop when going outside the window
            if row >= self.height:
                break
            # clip to range of window
            clippedInd1 = max(ind1, windowRowIndices[0])
            clippedInd2 = min(ind2, self.charLimit - 1)
            startCol = clippedInd1 - windowRowIndices[row]
            formatterLength = clippedInd2 - clippedInd1 + 1
            # if formatter extends across two lines, adjust length for spaces in between
            if row < len(windowRowIndices) - 1 and clippedInd2 >= windowRowIndices[row + 1]:
                formatterLength = (clippedInd2 - windowRowIndices[row + 1] + 1) \
                    + (self.width - (clippedInd1 - windowRowIndices[row]))
            self.addFormatting(tag, row, startCol, formatterLength)

    @property
    def charLimit(self):
        return self.subStates[GameState().activeProtagonistInd].charLimit
    @charLimit.setter
    def charLimit(self, val):
        self.subStates[GameState().activeProtagonistInd].charLimit = val

    @property
    def wrappedLines(self):
        return self.subStates[GameState().activeProtagonistInd].wrappedLines

    @property
    def rowIndices(self):
        return self.subStates[GameState().activeProtagonistInd].rowIndices

    @property
    def startingLine(self):
        return self.subStates[GameState().activeProtagonistInd].startingLine
    @startingLine.setter
    def startingLine(self, val):
        self.subStates[GameState().activeProtagonistInd].startingLine = val
