"""
PaletteWindow is shown on the right hand side of the screen and displays
a list of possible completions to commands a player is typing.
"""

from game_state import GameState, GameMode
from lang_parser import BodyNode
from window import Window

class PaletteWindow(Window):

    def __init__(self, width, height):
        super().__init__(width, height)
        self.displayList = []

    def draw(self):
        # clean pixels from last frame
        for i in range(self.height):
            for j in range(self.width):
                self.pixels[i][j] = ' '

        # separate normal commands and metacommands
        normalDisplayList = []
        metaDisplayList = []
        for completion in self.displayList:
            if completion in GameState.cmdListMetaCommands:
                metaDisplayList.append(completion)
            else:
                normalDisplayList.append(completion)
        # sort normal list by alpha
        normalDisplayList.sort()
        if len(normalDisplayList) > 0:
            normalDisplayList.append('')    # empty element lets window skip a line
        # join two lists
        normalDisplayList.extend(metaDisplayList)

        rStart = 0
        cStart = 1
        r = 0
        for completion in normalDisplayList:
            for i, c in enumerate(completion):
                if cStart + i >= self.width:
                    break
                self.pixels[rStart + r][cStart + i] = c
            r += 1
        return self.pixels

    def update(self, timestep, keypresses):
        gs = GameState()
        displayList = []
        if gs.gameMode == GameMode.inAreaCommand:
            val = gs.traverseCmdMap()
            if isinstance(val, BodyNode) or isinstance(val, str):
                # reached valid command, nothing more to show
                displayList = ['.']
            elif isinstance(val, tuple):
                # partial path, get all options at that level of tree
                tree, cmdString = val
                cmdList = list(tree.keys())
                # if at root of tree, add metacommands to list
                if tree == gs.cmdMap:
                    cmdList += list(GameState.cmdListMetaCommands)
                # filter possible commands based on what is in cmdBuffer
                for completion in cmdList:
                    if len(cmdString) <= len(completion) and completion.startswith(cmdString):
                        displayList.append(completion)
            # otherwise no valid command, so display nothing
        self.displayList = displayList
