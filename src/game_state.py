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
    IsLoading           =0
    TitleScreen         =1
    SelectFile          =2
    Settings            =3
    Credits             =4
    InAreaCommand       =5
    InAreaChoice        =6
    InAreaInput         =7
    InAreaMap           =8
    InAreaInventory     =9
    InAreaAnimating     =10
    WorldMap            =11
    WorldMapOverArea    =12

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
                self.historyFormatting = [] # list containing formatting info for historyBuffer
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
            def load(self, dct):
                for key in dct:
                    setattr(self, key, dct[key])
            def loads(self, jsonstr):
                self.load(json.loads(jsonstr))

        def __init__(self):
            # event broadcasters - registered listeners persist after game reset
            #  so they are initialized in __init__ rather than init
            self.onChoiceChange = EventHook()   # called when choiceList changes
            self.onGameModeChange = EventHook() # called when gameMode changes
            self.onAddLangNode = EventHook()    # called when addLangNode is called
            self.onCharacterSwitch = EventHook()    # called when activeProtagonistInd changes
            self.onEnterArea = EventHook()      # called when enterArea is called
            self.onEnterRoom = EventHook()      # called when enterRoom is called
            self.onClearBuffer = EventHook()    # called when clearBuffer is called
            self.onSettingChange = EventHook()  # called when a setting changes
            self.onInventoryChange = EventHook()    # called when inventory changes
            self.init()

        def init(self):
            """ Wipes out the existing GameState (called on New Game) """
            # game specific savable info
            self.name = ""              # player name, entered at start of new game
            self.playtime = 0.0         # playtime, in seconds
            self.actionCount = 0        # number of actions the player has taken
            self.variables = {}         # variables created through script files {string key: string/int value}
                                        # value is a string by default, but can be converted to int on the fly
            self.timeSetVars = {}       # sets vars after certain time elapses
                                        # {string key: (int timeLeft, string/int targetValue)}
            self.actionSetVars = {}     # sets vars after certain number of actions taken
                                        # {string key: (int actionsLeft, string/int targetValue)}

            # character specific savable info
            self.subStates = [
                GameState.__GameState.GameSubState().initLore(),
                GameState.__GameState.GameSubState().initKipp(),
            ]
            self.activeProtagonistInd = 0   # which protagonist is active (0=Lore, 1=Kipp)

            # non-savable info (refreshes on reset)
            self.saveId = 0             # which save path this state would be written on
            self.cmdBuffer = ""         # command that player is currently typing
            self.cmdMap = {}            # "trie" of commands player can type
            self.choiceList = []        # list of strings of choices player can make
            self.gameModeLockedRequests = []    # set requests are queued if game state is locked
            self.gameModeActive = GameMode.TitleScreen    # the "mode" of game player is in
            self.gameMessages = deque()

        def incPlaytime(self, dt):
            self.playtime += dt
            for varname in list(self.timeSetVars.keys()):
                self.timeSetVars[varname][0] -= dt
                if self.timeSetVars[varname][0] <= 0.0:
                    self.setVar(varname, self.timeSetVars[varname][1])
                    del self.timeSetVars[varname]

        def incActionCount(self, delta=1):
            self.actionCount += delta
            for varname in list(self.actionSetVars.keys()):
                self.actionSetVars[varname][0] -= delta
                if self.actionSetVars[varname][0] <= 0:
                    self.setVar(varname, self.actionSetVars[varname][1])
                    del self.actionSetVars[varname]

        def pushMessage(self, message):
            self.gameMessages.append(message)

        def popMessage(self):
            return self.gameMessages.popleft()

        def hasMessage(self):
            return len(self.gameMessages) > 0

        def switchCharacter(self):
            """ Switch the active protagonist after text finishes animation """
            def _doSwitch(*args, **kwargs):
                old, new = args[0]
                if old == GameMode.InAreaAnimating: # when done with text animation..
                    self.activeProtagonistInd = 1 - self.activeProtagonistInd # flip index
                    self.enterArea(self.areaId, self.roomId)    # send signal to run _awake startup script
                    self.onGameModeChange -= _doSwitch  # deregister this handler after complete
                    self.onCharacterSwitch(self.activeProtagonistInd)   # send event
            self.onGameModeChange += _doSwitch

        def appendCmdBuffer(self, ch):
            """ Add to the command buffer, but do not overflow """
            if len(self.cmdBuffer) + len(ch) <= Globals.CmdMaxLength:
                self.cmdBuffer += ch

        def popCmdBuffer(self, numchars=1):
            """ Take numchar characters off command buffer """
            if numchars <= 0:
                return
            self.cmdBuffer = self.cmdBuffer[:-numchars]

        def clearCmdBuffer(self):
            """ Reset command buffer (e.g. if pressed Return) """
            self.cmdBuffer = ""

        def traverseCmdMap(self):
            """
            Travels the command tree cmdMap with cmdBuffer and returns what is at end of path
            If return val is:
             str -> valid metacommand, contains string from GameState.cmdListMetaCommands
             BodyNode -> valid normal command, contains behavior to execute
             (dict, str[]) tuple -> partial walk along tree, contains (level in tree, path taken including remainder)
             None -> extraneous command, bad characters after valid or between tree levels
            """
            cmdString = self.cmdBuffer.lstrip().rstrip('. ').lower()
            prefixTree = self.cmdMap
            if cmdString in GameState.cmdListMetaCommands:
                return cmdString    # complete metacommand
            val = prefixTree
            keepWalking = True
            pathFollowed = []
            while len(cmdString) > 0 and keepWalking:
                keepWalking = False
                for prefix in prefixTree:
                    if cmdString.startswith(prefix.lower()):
                        pathFollowed.append(prefix)
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
            pathFollowed.append(cmdString)
            # (dict of current layer in tree, string[] of tokenized pieces of walk)
            return (val, pathFollowed)

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
                self.onInventoryChange(varname, value)
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

        def actionSet(self, varname, value, numActions):
            if varname not in self.actionSetVars:
                self.actionSetVars[varname] = [int(numActions), value]

        def timeSet(self, varname, value, numTime):
            if varname not in self.timeSetVars:
                self.timeSetVars[varname] = [float(numTime), value]

        def addLangNode(self, node):
            # running buffer of text and variables in node
            fullText = ''
            # running buffer of new formatters
            outputFormatting = []
            # number of chars to adjust formatting by
            varCharCount = len(self.historyBuffer)
            formattingIndex = 0
            seekIndex = 0

            # interpolate variables into text
            for varName, varIndex in node.variables:
                while formattingIndex < len(node.formatting):
                    tag, (ind1, ind2) = node.formatting[formattingIndex]
                    if ind1 >= varIndex:
                        break
                    outputFormatting.append((tag, (ind1 + varCharCount, ind2 + varCharCount)))
                    formattingIndex += 1
                varVal = self.getVar(varName) if self.getVar(varName) is not None else ''
                fullText += node.text[seekIndex:varIndex] + varVal
                varCharCount += len(varVal)
                seekIndex = varIndex
            # handle text after last variable
            for (tag, (ind1, ind2)) in node.formatting[formattingIndex:]:
                outputFormatting.append((tag, (ind1 + varCharCount, ind2 + varCharCount)))
            fullText += node.text[seekIndex:]

            fullText = fullText + "\n"
            self.historyBuffer += fullText
            self.historyFormatting.extend(outputFormatting)
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

        def clearBuffer(self):
            self.historyBuffer = ''
            self.historyFormatting = []
            self.onClearBuffer()

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
            """ changes active character's area and room and fires event """
            oldArea = self.areaId
            oldRoom = self.roomId
            self.areaId = areaId
            self.enterRoom(roomId)
            if fromWorldMap:
                self.clearBuffer()
            self.onEnterArea((oldArea, areaId), (oldRoom, roomId), fromWorldMap)

        def enterRoom(self, roomId):
            """ changes just active character's room and fires event """
            oldRoom = self.roomId
            self.roomId = roomId
            self.onEnterRoom(oldRoom, roomId)

        @property
        def mapLocation(self):
            return self.subStates[self.activeProtagonistInd].mapLocation
        @mapLocation.setter
        def mapLocation(self, val):
            self.subStates[self.activeProtagonistInd].mapLocation = val

        def gotoWorldMap(self, r, c):
            """ transitions to world map and sets character position to (r, c) """
            def _gotoWorldMap(*args, **kwargs):
                old, new = args[0]
                if old == GameMode.InAreaAnimating:         # when done with text animation..
                    self.mapLocation = [int(r), int(c)]     # change player coordinates
                    self.gameMode = GameMode.WorldMap       # window manager changes active windows
                    self.onGameModeChange -= _gotoWorldMap  # deregister handler
            self.onGameModeChange += _gotoWorldMap

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
                'gameModeLockedRequests', 'onChoiceChange', 'onSettingChange', 'onClearBuffer',
                'onGameModeChange', 'onAddLangNode', 'onEnterArea', 'onEnterRoom',
                'onCharacterSwitch', 'onInventoryChange', 'gameMessages', 'saveId']
            for field in deleteFields:
                del obj[field]
            return json.dumps(obj)

        def __str__(self):
            return self.dumps()

        def load(self, dct):
            """ Initialize the GameState from a dictionary """
            # start all fields from scratch
            self.init()
            # "join" dct manually so omitted members of dct do not carry over
            activeInd = 0
            for key in dct:
                if key == 'subStates':
                    self.subStates = []
                    for i in range(len(dct[key])):
                        substate = GameState.__GameState.GameSubState()
                        substate.load(dct[key][i])
                        self.subStates.append(substate)
                elif key == 'activeProtagonistInd':
                    activeInd = int(dct[key])
                else:
                    setattr(self, key, dct[key])
            # TODO refactor event signalling
            # send lang node add signal to load both buffers of HistoryWindow
            # the active protagonist is done last so correct commands will be shown
            self.activeProtagonistInd = 1 - activeInd
            self.onAddLangNode(self.historyBuffer, True)
            self.activeProtagonistInd = activeInd
            self.onAddLangNode(self.historyBuffer, True)
            # send inventory change signal to load InventoryWindow
            self.onInventoryChange()
            # send room enter signal to load InAreaWindow
            self.onEnterRoom(self.roomId, self.roomId)

        def loads(self, jsonstr):
            """ Initialize the GameState from a Json string """
            self.load(json.loads(jsonstr))

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

    # When GameMode is InAreaCommand, some generally available game commands
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
