
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

        rStart = 1
        cStart = 1
        r = 0
        for completion in self.displayList:
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
            cmdString = gs.cmdBuffer.strip()
            prefixTree = gs.cmdMap
            cmdMatch = False
            while cmdString:
                val = None
                for prefix in prefixTree:
                    if cmdString[:len(prefix)] == prefix:
                        val = prefixTree[prefix]
                        if isinstance(val, BodyNode):
                            cmdMatch = True
                            break
                        elif isinstance(val, dict):
                            prefixTree = val
                            cmdString = cmdString[len(prefix):].strip()
                            break
                if val is None or cmdMatch:
                    break
            if cmdMatch:
                displayList = ['.']
            else:
                cmdList = list(prefixTree.keys())
                displayList=[]
                for j in range(0,len(cmdList)):
                    if len(cmdString) <= len(cmdList[j]) and cmdString == cmdList[j][:len(cmdString)]:
                        displayList.append(cmdList[j])
        self.displayList = displayList
