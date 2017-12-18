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
        pass

    def writeTextLines(self, lines, startRow, startCol):
        """
        Writes multiple strings as consecutive lines to the pixels array
        """
        for i in range(len(lines)):
            self.writeText(lines[i], startRow + i, startCol, False, None)

    def writeText(self, text, startRow, startCol, wordWrap=None, tag=None):
        """
        Writes a string as one line to the pixels array.
        Optionally word wrap the text to fit in the window by breaking it
         on spaces to proceeding lines (either set wordWrap to True to wrap
         until the edge of the window, or set to an int value to define the right-side
         boundary). Newline characters are taken as line breaks and will go to
         the next row regardless of wordWrap param.
        Optionally add a string tag to format the text.
        """

        # split on newlines, which cause line breaks in the formatting
        lineGroups = text.split('\n')
        # split on whitespace if word wrapping
        lineTokenLists = [group.split(' ') for group in lineGroups] if wordWrap \
            else [[group] for group in lineGroups]
        # calculate indices where line breaks happen due to newlines (presums of length of token groups)
        lineBreakIndices = [len(tokenList) for tokenList in lineTokenLists]
        for i in range(1, len(lineBreakIndices)):
            lineBreakIndices[i] += lineBreakIndices[i-1]
        # flatten token list - credit https://stackoverflow.com/a/952952 for one-liner
        tokens = [token for tokenList in lineTokenLists for token in tokenList]

        wrapBorder = wordWrap if type(wordWrap) is int and wordWrap != 0 else self.width
        rowOffset = 0
        colOffset = 0
        for i, token in enumerate(tokens):
            if (wordWrap and startCol + colOffset + len(token) > wrapBorder) or (i in lineBreakIndices):
                # move to next line
                colOffset = 0
                rowOffset += 1
                if rowOffset >= self.height:
                    # cannot write any more on the window
                    return

            for c, ch in enumerate(token):
                # write token (note that token will be clipped if it cannot fit on window)
                self.setPixel(ch, startRow + rowOffset, startCol + colOffset + c)
            if i < len(tokens) - 1 and i not in lineBreakIndices:
                # write space between tokens
                self.setPixel(" ", startRow + rowOffset, startCol + colOffset + len(token))
            colOffset += len(token) + 1

        if tag is not None:
            # add formatter to cover the length of the full text
            self.addFormatting(str(tag), startRow, startCol, len(text) - text.count('\n'))

    def fillRect(self, ch, left, up, right, down):
        """
        Fills a rect within the window with a given character
        """
        for i in range(max(up, 0), min(down, self.height)):
            for j in range(max(left, 0), min(right, self.width)):
                self.setPixel(ch, i, j)

    def setPixel(self, ch, row, col):
        """
        Set one pixel in the window
        """
        if row < 0 or row >= self.height or col < 0 or col >= self.width:
            return # ignore setting out of bounds
        self.pixels[row][col] = ch[0]

    def addFormatting(self, tag, startRow, startCol, length):
        """
        Adds a formatter to the given region of the window
        """
        self.formatting.append((tag, (startRow * self.width + startCol, startRow * self.width + startCol + length - 1)))

    def clear(self):
        """
        Clear formatting tags and reset all pixels to blank (' ')
        """
        self.clearPixels()
        self.clearFormatting()

    def clearPixels(self, left = 0, up = 0, right = None, down = None):
        """
        Clear pixels to blank (' ') characters and empty formatting
        """
        right = self.width if right is None else right
        down = self.height if down is None else down
        self.fillRect(' ', left, up, right, down)

    def clearFormatting(self):
        """
        Remove all formatting tags on the pixels
        """
        self.formatting = []

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
