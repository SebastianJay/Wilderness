"""
Definition of game state, which is the model in our MVC framework.
"""

from global_vars import Globals
from enum import Enum
import json
import copy
import os

class GameMode(Enum):
    titleScreen         =0
    selectFile          =1
    credits             =2
    inAreaCommand       =3
    inAreaChoice        =4
    inAreaInput         =5
    inAreaMap           =6
    inAreaInventory     =7
    worldMap            =8
    worldMapOverArea    =9

class GameState:
    # Python singleton implementation adapted from
    # http://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html
    class __GameState:

        class GameSubState(json.JSONEncoder):
            """ state variables that each protagonist will maintain separately """
            def __init__(self):
                self.areaId = ""            # area ID, where the player is located
                self.roomId = ""            # room ID, where player is located
                self.mapLocation = (0,0)    # coordinates of player location on world map
                self.inventory = {}         # inventory, represented as {string itemId: int numberOfItem}
                self.historyLines = []      # lines of strings for the history (feedback) window
                                            # TODO change to list of LangNodes
            def dumps():
                return json.dumps(self.__dict__)
            def loads(self, jsonstr):
                dct = json.loads(jsonstr)
                for key in dct:
                    setattr(self, key, dct[key])

        def __init__(self):
            self.init()

        def init(self):
            """ Wipes out the existing GameState (called on New Game) """
            self.name = ""              # player name, entered at start of new game
            self.playtime = 0           # playtime, in seconds
            self.variables = {}         # variables created through script files {string key: string/int value}
                                        # value is a string by default, but can be converted to int on the fly
            self.cmdBuffer = ""         # command that player is currently typing
            self.cmdMap = {}            # "trie" of commands player can type
            self.gameMode = GameMode.titleScreen    # the "mode" of game player is in

            self.subStates = [
                GameState.__GameState.GameSubState(),
                GameState.__GameState.GameSubState(),
            ]
            self.activeProtagonistInd = 0   # which protagonist is active (0=Lore, 1=Kipp)

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
            self.subStates[self.activeProtagonistInd].historyLines.append(line)

        def debugAddHistoryLine(self, line):
            if len(self.subStates[self.activeProtagonistInd].historyLines) == 0:
                self.subStates[self.activeProtagonistInd].historyLines.append('')
            self.subStates[self.activeProtagonistInd].historyLines[0] += line + ' '

        def getHistoryLines(self):
            return self.subStates[self.activeProtagonistInd].historyLines

        def refreshCommandList(self):
            """ Updates cmdMap to contain all commands player can type """
            # locate the rooms and objects configs
            loader = AssetLoader()
            area = loader.getConfig(Globals.AreasConfigPath)[self.areaId]
            items = loader.getConfig(Globals.ItemsConfigPath)
            rooms = loader.getConfig(area['roomsConfig'])
            objects = loader.getConfig(area['objectsConfig'])
            # locate the relevant scripts
            cmdMap = {}
            roomScript = loader.getConfig(rooms[self.roomId]['script'])
            objectNames = []
            objectScripts = []
            for obj in rooms[self.roomId]['objects']:
                objectNames.append(loader.getConfig(objects[obj]['name']))
                objectScripts.append(loader.getConfig(objects[obj]['script']))
            # fill out the mapping, starting with 'go to'
            cmdMap['go to'] = {}
            for neighbor in rooms[self.roomId]['neighbors']:
                # neighbor is a one mapping dict
                for key in neighbor:
                    neighborName = rooms[key]['name']
                    neighborScript = loader.getConfig(rooms[key]['script'])
                    neighborReaction = None
                    for action in neighborScript:
                        if action[0] == 'go to':
                            neighborReaction = action[1]
                    cmdMap['go to'][neighborName] = neighborReaction
            # go through actions to take on room
            for action in roomScript:
                # ignore 'go to' current room (not possible)
                if action[0] == 'go to':
                    continue
                cmdMap[action[0]] = action[1]
            # prefill 'use <item>'
            cmdMap['use'] = {}
            for item in self.inventory:
                if self.inventory[item] == 0:
                    continue
                itemName = loader.getConfig(items[item]['name'])
                cmdMap['use'][itemName] = None
            # go through actions to take on objects
            for i in range(len(objectScripts)):
                objScript = objectScripts[i]
                objName = objectNames[i]
                for action in objScript:
                    # "use .. on" needs special treatment for inventory items
                    verbWords = action[0].split()
                    if verbWords[0] == 'use' and verbWords[-1] == 'on':
                        itemWord = ' '.join(verbWords[1:-1])
                        itemKey = loader.reverseItemLookup(itemWord)
                        targetPhrase = 'on ' + objName
                        if itemKey == '':
                            raise Exception('script item name', itemWord ,'not found in items configuration file')
                        if itemKey in self.inventory and self.inventory[itemKey] > 0:
                            if cmdMap['use'][itemWord] is None:
                                cmdMap['use'][itemWord] = {}
                            cmdMap['use'][itemWord][targetPhrase] = action[1]
                    # all other verbs are straightforward
                    else:
                        if action[0] not in cmdMap:
                            cmdMap[action[0]] = {}
                        cmdMap[action[0]][objName] = action[1]
            self.cmdMap = cmdMap

        def dumps(self):
            """ Json stringifies the GameState """
            obj = copy.deepcopy(self.__dict__)
            # GameSubState and GameMode need special treatment
            obj['gameMode'] = obj['gameMode'].value
            for i in range(len(obj['subStates'])):
                obj['subStates'][i] = obj['subStates'][i].__dict__
            return json.dumps(obj)

        def loads(self, jsonstr):
            """ Initialize the GameState from a Json string """
            # "join" dct manually so omitted members of dct do not carry over
            dct = json.loads(jsonstr)
            for key in dct:
                if key == 'gameMode':
                    self.gameMode = GameMode(dct[key])
                elif key == 'subStates':
                    self.subStates = []
                    for i in range(len(dct[key])):
                        substate = GameState.__GameState.GameSubState()
                        substate.__dict__ = dct[key][i]
                        self.subStates.append(substate)
                else:
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
    g.writeFile(Globals.SavePaths[0])
    g.name = 'should not appear in print(g)!'
    g.readFile(Globals.SavePaths[0])
    print(g)
