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
        self.clear()

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

        self.writeTextLines(normalDisplayList, 0, 1)

    def update(self, timestep, keypresses):
        gs = GameState()
        displayList = []
        if gs.gameMode == GameMode.InAreaCommand:
            val = gs.traverseCmdMap()
            if isinstance(val, BodyNode) or isinstance(val, str):
                # reached valid command, nothing more to show
                displayList = ['.']
            elif isinstance(val, tuple):
                # partial path, get all options at that level of tree
                tree, pathFollowed = val
                cmdString = pathFollowed[-1]
                cmdList = list(tree.keys())
                # if at root of tree, add metacommands to list
                if tree == gs.cmdMap:
                    cmdList += list(GameState.cmdListMetaCommands)
                # filter possible commands based on what is in cmdBuffer
                for completion in cmdList:
                    if len(cmdString) <= len(completion) and completion.lower().startswith(cmdString.lower()):
                        displayList.append(completion)
            for key in keypresses:
                if key == 'Tab' and isinstance(val, tuple) and len(displayList) == 1:
                    # do autocomplete
                    _, pathFollowed = val
                    remainderLen = len(gs.cmdBuffer) - len(' '.join(pathFollowed[:-1]))
                    gs.popCmdBuffer(remainderLen)   # remove partial
                    if len(gs.cmdBuffer) > 0:
                        gs.appendCmdBuffer(' ')     # append delimiter space
                    gs.appendCmdBuffer(displayList[0]) # add completion
                    # add trailing space if more commands to be read
                    nextval = gs.traverseCmdMap()
                    if isinstance(nextval, tuple):
                        gs.appendCmdBuffer(' ')
                        displayList = list(nextval[0].keys())
                    elif isinstance(nextval, str) or isinstance(nextval, BodyNode):
                        displayList = ['.']
        self.displayList = displayList
