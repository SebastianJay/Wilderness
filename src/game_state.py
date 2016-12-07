"""
Definition of game state, which is the model in our MVC framework.
"""

from global_vars import Globals
from event_hook import EventHook
from lang_parser import BodyNode
from enum import Enum
from collections import deque
import json
import copy
import os

class GameMode(Enum):
    isLoading           =0
    titleScreen         =1
    selectFile          =2
    credits             =3
    inAreaCommand       =4
    inAreaChoice        =5
    inAreaInput         =6
    inAreaMap           =7
    inAreaInventory     =8
    inAreaAnimating     =9
    worldMap            =10
    worldMapOverArea    =11

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
            def initLore(self):
                self.areaId = 'suburbs'
                self.roomId = 'bedroom'
                return self
            def initKipp(self):
                self.areaId = 'farm'
                self.roomId = 'bedroom'
                return self

            def __str__(self):
                return self.dumps()
            def dumps():
                return json.dumps(self.__dict__)
            def loads(self, jsonstr):
                dct = json.loads(jsonstr)
                for key in dct:
                    setattr(self, key, dct[key])

        def __init__(self):
            # event broadcasters - registered listeners persist after game reset
            #  so they are initialized in __init__ rather than init
            self.onChoiceChange = EventHook()   # called when choiceList changes
            self.onGameModeChange = EventHook() # called when gameMode changes
            self.onAddLangNode = EventHook()    # called when addLangNode is called
            self.onCharacterSwitch = EventHook() # called when activeProtagonistInd changes
            self.onEnterArea = EventHook() # called when enterArea is called
            self.onSettingChange = EventHook()  # called when a setting changes
            self.init()

        def init(self):
            """ Wipes out the existing GameState (called on New Game) """
            # game specific savable info
            self.name = ""              # player name, entered at start of new game
            self.playtime = 0           # playtime, in seconds
            self.variables = {}         # variables created through script files {string key: string/int value}
                                        # value is a string by default, but can be converted to int on the fly

            # character specific savable info
            self.subStates = [
                GameState.__GameState.GameSubState().initLore(),
                GameState.__GameState.GameSubState().initKipp(),
            ]
            self.activeProtagonistInd = 0   # which protagonist is active (0=Lore, 1=Kipp)

            # non-savable info (refreshes on reset)
            self.cmdBuffer = ""         # command that player is currently typing
            self.cmdMap = {}            # "trie" of commands player can type
            self.choiceList = []        # list of strings of choices player can make
            self.gameModeLockedRequests = []    # set requests are queued if game state is locked
            self.gameModeActive = GameMode.titleScreen    # the "mode" of game player is in
            self.gameMessages = deque()

        def pushMessage(self, message):
            self.gameMessages.append(message)

        def popMessage(self):
            return self.gameMessages.popleft()

        def messageExists(self):
            return len(self.gameMessages) != 0

        def switchCharacter(self):
            """ Switch the active protagonist after text finishes animation """
            def _doSwitch(*args, **kwargs):
                old, new = args[0]
                if old == GameMode.inAreaAnimating: # when done with text animation..
                    self.activeProtagonistInd = 1 - self.activeProtagonistInd # flip index
                    self.enterArea(self.areaId, self.roomId)    # send signal to run startup script
                    self.onGameModeChange -= _doSwitch  # deregister this handler after complete
                    self.onCharacterSwitch(self.activeProtagonistInd)   # send event
            self.onGameModeChange += _doSwitch

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

        def traverseCmdMap(self):
            """
            Travels the command tree cmdMap with cmdBuffer and returns what is at end of path
            If return val is:
             str -> valid metacommand, contains string from GameState.cmdListMetaCommands
             BodyNode -> valid normal command, contains behavior to execute
             (dict, str) tuple -> partial walk along tree, contains (level in tree, remaining cmdBuffer)
             None -> extraneous command, bad characters after valid or between tree levels
            """
            cmdString = self.cmdBuffer.lstrip().rstrip('. ')
            prefixTree = self.cmdMap
            if cmdString in GameState.cmdListMetaCommands:
                return cmdString    # complete metacommand
            val = prefixTree
            keepWalking = True
            while len(cmdString) > 0 and keepWalking:
                keepWalking = False
                for prefix in prefixTree:
                    if cmdString.startswith(prefix):
                        val = prefixTree[prefix]
                        if isinstance(val, BodyNode):
                            if len(cmdString) > len(prefix):
                                return None # too many chars at end
                            return val  # correct command
                        elif isinstance(val, dict):
                            prefixTree = val
                            cmdString = cmdString[len(prefix):]
                            if len(cmdString) == 0 or cmdString[0] == ' ':
                                cmdString = cmdString.lstrip()
                                keepWalking = True
                                break   # continue walking tree
                            else:
                                return None # invalid chars in between
            # (dict of current layer in tree, string of cmd buffer remaining after walk)
            return (val, cmdString)

        def touchVar(self, varname, inventoryFlag = False):
            """ Sets a variable or inventory item to 0 in mapping if it doesn't exist """
            if inventoryFlag:
                if varname not in self.inventory:
                    self.inventory[varname] = '0'
            else:
                if varname not in self.variables:
                    self.variables[varname] = '0'

        def getVar(self, varname, inventoryFlag = False):
            """ Returns a variable value or item count, or None if it doesn't exist """
            if inventoryFlag:
                return self.inventory.get(varname)
            else:
                return self.variables.get(varname)

        def setVar(self, varname, value, inventoryFlag = False):
            """ Sets a variable or item count """
            if inventoryFlag:
                self.inventory[varname] = value
            else:
                self.variables[varname] = value

        def delVar(self, varname, inventoryFlag = False):
            """ Removes an existing mapping """
            if inventoryFlag:
                if varname in self.inventory:
                    del self.inventory[varname]
            else:
                if varname in self.variables:
                    del self.variables[varname]

        def addLangNode(self, node):
            # helper for adding correct indices to historyFormatting
            def appendToHistoryFormatting(self, formatting):
                nonlocal fullText
                for key in formatting:
                    if key not in self.historyFormatting:
                        self.historyFormatting[key] = []
                    for start, end in formatting[key]:
                        # offset formatting indices by constant previous history buffer length
                        #  and variable current text + interpolated variables length
                        self.historyFormatting[key].append((start+len(self.historyBuffer)+len(fullText),
                            end+len(self.historyBuffer)+len(fullText)))

            fullText = ''   # running buffer of text and variables in node
            seekInd = 0
            i = 0
            # interpolate variables into text
            for varname, varindex in node.variables:
                appendToHistoryFormatting(self, node.formatting[i])
                varval = self.getVar(varname) if self.getVar(varname) is not None else ''
                fullText += node.text[seekInd:varindex] + varval
                seekInd = varindex
                i += 1
            if i < len(node.formatting):
                # any remaining formatting after last interpolated variable
                appendToHistoryFormatting(self, node.formatting[i])
            fullText += node.text[seekInd:]
            fullText += "\n" # add trailing newline to separate new text from old
            self.historyBuffer += fullText
            self.onAddLangNode(fullText)

        @property
        def choices(self):
            return self.choiceList
        @choices.setter
        def choices(self, val):
            oldval = self.choiceList[:] # shallow copy
            self.choiceList = val
            self.onChoiceChange((oldval, val))

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

        def enterArea(self, areaId, roomId, fromWorldMap=False):
            oldArea = self.areaId
            self.areaId = areaId
            oldRoom = self.roomId
            self.roomId = roomId
            self.onEnterArea((oldArea, areaId), (oldRoom, roomId), fromWorldMap)

        @property
        def mapLocation(self):
            return self.subStates[self.activeProtagonistInd].mapLocation
        @mapLocation.setter
        def mapLocation(self, val):
            self.subStates[self.activeProtagonistInd].mapLocation = val

        # the gameMode property exposed by the GameState has a notion of locking
        # which is useful for animations like text scrolling and loading windows
        @property
        def gameMode(self):
            return self.gameModeActive
        @gameMode.setter
        def gameMode(self, val):
            if len(self.gameModeLockedRequests) > 0:
                self.gameModeLockedRequests.append(val)
            else:
                oldval = self.gameModeActive
                self.gameModeActive = val
                if oldval != val:
                    self.onGameModeChange((oldval, val))
        def lockGameMode(self, val):
            if len(self.gameModeLockedRequests) > 0:
                return  # ignore if already locked
            oldMode = self.gameMode
            self.gameMode = val
            self.gameModeLockedRequests = [oldMode]
        def unlockGameMode(self):
            if len(self.gameModeLockedRequests) == 0:
                return  # ignore if already unlocked
            newMode = self.gameModeLockedRequests.pop()
            self.gameModeLockedRequests = []
            self.gameMode = newMode

        def dumps(self):
            """ Json stringifies the GameState """
            obj = copy.deepcopy(self.__dict__)
            # GameSubState and GameMode need special treatment as Python classes
            for i in range(len(obj['subStates'])):
                obj['subStates'][i] = obj['subStates'][i].__dict__
            # do not save non-persistent fields
            deleteFields = ['cmdMap', 'cmdBuffer', 'gameModeActive', 'choiceList',
                'gameModeLockedRequests', 'onChoiceChange', 'onSettingChange',
                'onGameModeChange', 'onAddLangNode', 'onEnterArea', 'onCharacterSwitch']
            for field in deleteFields:
                del obj[field]
            return json.dumps(obj)

        def __str__(self):
            return self.dumps()

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

    # singleton instance - created once per program run
    instance = None

    # When GameMode is inAreaCommand, some generally available game commands
    cmdListMetaCommands = (
        'view inventory',
        'view map',
        'save game',
        'exit game',
    )

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

    from asset_loader import AssetLoader
    AssetLoader().loadAssets()
    g.areaId = "aspire"
    g.roomId = "library"
    g.mapLocation = [1, 0]
    g.refreshCommandList()
    print(g.cmdMap)
    print(g.cmdMap['look around'])
    print(g)
