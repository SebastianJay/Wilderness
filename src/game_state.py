"""
Definition of game state, which is the model in our MVC framework.
"""

from global_vars import Globals
from asset_loader import AssetLoader
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

        class GameSubState:
            """ state variables that each protagonist will maintain separately """
            def __init__(self):
                self.areaId = ""            # area ID, where player is located
                self.roomId = ""            # room ID, where player is located
                self.mapLocation = [0,0]    # coordinates of player location on world map
                self.inventory = {}         # inventory, represented as {string itemId: int numberOfItem}
                self.historyBuffer = ''     # string containing contents for  history window
                self.historyFormatting = {} # dict containing formatting info for historyBuffer

            def __str__(self):
                return self.dumps()
            def dumps():
                return json.dumps(self.__dict__)
            def loads(self, jsonstr):
                dct = json.loads(jsonstr)
                for key in dct:
                    setattr(self, key, dct[key])

        def __init__(self):
            self.init()

        def __str__(self):
            return self.dumps()

        def init(self):
            """ Wipes out the existing GameState (called on New Game) """
            # game specific savable info
            self.name = ""              # player name, entered at start of new game
            self.playtime = 0           # playtime, in seconds
            self.variables = {}         # variables created through script files {string key: string/int value}
                                        # value is a string by default, but can be converted to int on the fly

            # character specific savable info
            self.subStates = [
                GameState.__GameState.GameSubState(),
                GameState.__GameState.GameSubState(),
            ]
            self.activeProtagonistInd = 0   # which protagonist is active (0=Lore, 1=Kipp)

            # non-savable info (refreshes on reset)
            self.cmdBuffer = ""         # command that player is currently typing
            self.cmdMap = {}            # "trie" of commands player can type
            self.choiceList = []        # list of strings of choices player can make
            self.gameMode = GameMode.titleScreen    # the "mode" of game player is in

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

        def touchVar(self, varname):
            if varname not in self.variables:
                self.variables[varname] = '0'

        def touchInventory(self, varname):
            if varname not in self.inventory:
                self.inventory[varname] = '0'

        def debugAddHistoryLine(self, line):
            ## DEBUG1 adds a specific langnode
            self.areaId = "aspire"
            self.roomId = "library"
            self.refreshCommandList()
            self.addLangNode(self.cmdMap['look around'].nodes[0])
            ## end DEBUG1

        def addLangNode(self, node):
            prevBufferLen = len(self.historyBuffer) # offset for formatting indices
            self.historyBuffer += node.text # append the LangNode text
            # append the LangNode formatting
            for key in node.formatting:
                val = node.formatting[key]
                if key not in self.historyFormatting:
                    self.historyFormatting[key] = []
                for indices in val:
                    self.historyFormatting[key].append((indices[0]+prevBufferLen, indices[1]+prevBufferLen))
            self.historyBuffer += "\n"  # add trailing newline to separate new text from old

        @property
        def historyBuffer(self):
            return self.subStates[self.activeProtagonistInd].historyBuffer
        @historyBuffer.setter
        def historyBuffer(self, val):
            self.subStates[self.activeProtagonistInd].historyBuffer = val

        @property
        def historyFormatting(self):
            return self.subStates[self.activeProtagonistInd].historyFormatting
        @historyFormatting.setter
        def historyFormatting(self, val):
            self.subStates[self.activeProtagonistInd].historyFormatting = val

        @property
        def inventory(self):
            return self.subStates[self.activeProtagonistInd].inventory

        @property
        def roomId(self):
            return self.subStates[self.activeProtagonistInd].roomId
        @roomId.setter
        def roomId(self, val):
            self.subStates[self.activeProtagonistInd].roomId = val

        @property
        def areaId(self):
            return self.subStates[self.activeProtagonistInd].areaId
        @areaId.setter
        def areaId(self, val):
            self.subStates[self.activeProtagonistInd].areaId = val

        @property
        def mapLocation(self):
            return self.subStates[self.activeProtagonistInd].mapLocation
        @mapLocation.setter
        def mapLocation(self, val):
            self.subStates[self.activeProtagonistInd].mapLocation = val

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
            roomScript = loader.getScript(rooms[self.roomId]['script'])
            objectNames = []
            objectScripts = []
            for obj in rooms[self.roomId]['objects']:
                objectNames.append(objects[obj]['name'])
                objectScripts.append(loader.getScript(objects[obj]['script']))
            # fill out the mapping, starting with 'go to'
            cmdMap['go to'] = {}
            for neighbor in rooms[self.roomId]['neighbors']:
                neighborName = rooms[neighbor]['name']
                neighborScript = loader.getScript(rooms[neighbor]['script'])
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
            inventory = self.inventory
            for item in inventory:
                if inventory[item] == 0:
                    continue
                itemName = items[item]['name']
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
                        if itemKey in inventory and int(inventory[itemKey]) > 0:
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
            # GameSubState and GameMode need special treatment as Python classes
            for i in range(len(obj['subStates'])):
                obj['subStates'][i] = obj['subStates'][i].__dict__
            # do not save non-persistent fields
            deleteFields = ['cmdMap', 'cmdBuffer', 'gameMode', 'choiceList']
            for field in deleteFields:
                del obj[field]
            return json.dumps(obj)

        def loads(self, jsonstr):
            """ Initialize the GameState from a Json string """
            # start all fields from scratch
            self.init()
            # "join" dct manually so omitted members of dct do not carry over
            dct = json.loads(jsonstr)
            for key in dct:
                if key == 'subStates':
                    self.subStates = []
                    for i in range(len(dct[key])):
                        substate = GameState.__GameState.GameSubState()
                        substate.__dict__ = dct[key][i]
                        self.subStates.append(substate)
                else:
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

    AssetLoader().loadAssets()
    g.areaId = "aspire"
    g.roomId = "library"
    g.mapLocation = [1, 0]
    g.refreshCommandList()
    print(g.cmdMap)
    print(g.cmdMap['look around'])
    print(g)
