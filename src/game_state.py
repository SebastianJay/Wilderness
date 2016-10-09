"""
Definition of game state, which is the model in our MVC framework.
"""

from global_vars import Globals
import json
import os

class GameState:
    # Python singleton implementation adapted from
    # http://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html
    class __GameState:
        def __init__(self):
            self.init()

        def init(self):
            """ Wipes out the existing GameState (called on New Game) """
            self.name = ""              # player name, entered at start of new game
            self.playtime = 0           # playtime, in seconds
            self.roomId = ""            # room ID, where player is located
            self.mapLocation = (0,0)    # coordinates of player location on world map
            self.inventory = {}         # inventory, represented as {string itemId: int numberOfItem}
            self.variables = {}         # variables created through script files {string key: string/int value}
                                        # value is a string by default, but can be converted to int on the fly
            self.historyLines = []      # lines of strings for the history (feedback) window
                                        # TODO change to list of LangNodes
            self.cmdBuffer = ""         # command that player is currently typing

        def appendCmdBuffer(self, ch):
            """ Add to the command buffer, but do not overflow """
            if len(self.cmdBuffer) < Globals.CmdMaxLength:
                self.cmdBuffer += ch

        def popCmdBuffer(self):
            """ Take one character off command buffer, to implement BackSpace """
            self.cmdBuffer = self.cmdBuffer[:-1]

        def clearCmdBuffer(self):
            """ Reset command buffer (e.g. if pressed Return) """
            self.cmdBuffer = ""

        def addHistoryLine(self, line):
            self.historyLines.append(line)

        def debugAddHistoryLine(self, line):
            if len(self.historyLines) == 0:
                self.historyLines.append('')
            self.historyLines[0] += line + ' '

        def dumps(self):
            """ Json stringifies the GameState """
            return json.dumps(self.__dict__)

        def loads(self, jsonstr):
            """ Initialize the GameState from a Json string """
            # "join" dct manually so omitted members of dct do not carry over
            dct = json.loads(jsonstr)
            for key in dct:
                # NOTE no copies made - dct should persist in memory
                setattr(self, key, dct[key])

        def writeFile(self, fpath):
            """ Write GameState to file """
            # create the directory to the save files if it does not exist
            fdir = os.path.dirname(fpath)
            if not os.path.exists(fdir):
                os.makedirs(fdir)
            with open(fpath, 'w') as f:
                f.write(self.dumps())

        def readFile(self, fpath):
            """ Load GameState from file """
            with open(fpath, 'r') as f:
                self.loads(f.read())

        def __str__(self):
            return self.dumps()

    instance = None
    def __new__(cls):
        if not GameState.instance:
            GameState.instance = GameState.__GameState()
        return GameState.instance
    def __getattr__(self, name):
        return getattr(self.instance, name)
    def __setattr__(self, name):
        return setattr(self.instance, name)

if __name__ == '__main__':
    g = GameState()
    g.name = 'testing'
    print(g)
    jsonstr = '{"gender": "??", "inventory": {"fork": 0}, "id_number": 5, \
        "name": "unknown", "status": [], "location": ""}'
    g.loads(jsonstr)
    print(g)

    g.writeFile(Globals.SavePaths[0])
    g.name = 'should not appear in print(g)!'
    g.readFile(Globals.SavePaths[0])
    print(g)
