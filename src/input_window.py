"""
Window for processing a user's input and displaying it back as they are
typing. When a command is entered it is passed to the interpreter which
then modifies GameState.
"""
from window import Window
from game_state import GameState, GameMode
from asset_loader import AssetLoader
from global_vars import Globals
from lang_parser import BodyNode
from lang_interpreter import Interpreter
import threading

class InputWindow(Window):

    def __init__(self, width, height):
        super().__init__(width, height)
        GameState().onChoiceChange += self.choiceChangeHandler()
        GameState().onEnterArea += self.enterAreaHandler()
        GameState().onAddLangNode += self.langNodeAddedHandler()

    def reset(self):
        self.interpreter = Interpreter()
        self.choiceInd = 0

    def choiceChangeHandler(self):
        def _choiceChangeHandler(*args, **kwargs):
            self.choiceInd = 0
        return _choiceChangeHandler

    def enterAreaHandler(self):
        def _enterAreaHandler(*args, **kwargs):
            # run the startup script for an area
            (_, areaId), (_, roomId), fromWorldMap = args[0], args[1], args[2]
            startupverb = '_enter' if fromWorldMap else '_awake'
            areasConfig = AssetLoader().getConfig(Globals.AreasConfigPath)
            roomsConfig = AssetLoader().getConfig(areasConfig[areaId]['roomsConfig'])
            roomScript = AssetLoader().getScript(roomsConfig[roomId]['script'])
            for verb, action, _ in roomScript:
                if verb == startupverb:
                    self.interpreter.executeAction(action)
                    return
            # if startup script not found, refresh command list manually
            self.interpreter.refreshCommandList()
        return _enterAreaHandler

    def langNodeAddedHandler(self):
        def _langNodeAddedHandler(*args, **kwargs):
            if len(args) >= 2 and args[1]:
                self.interpreter.refreshCommandList()
        return _langNodeAddedHandler

    def update(self, timestep, keypresses):
        gs = GameState()
        if gs.gameMode == GameMode.inAreaChoice:
            for key in keypresses:
                if key == 'Up':
                    self.choiceInd = (self.choiceInd - 1) % len(gs.choices)
                elif key == 'Down':
                    self.choiceInd = (self.choiceInd + 1) % len(gs.choices)
                elif key == 'Return':
                    self.interpreter.resume(self.choiceInd)
        elif gs.gameMode == GameMode.inAreaCommand or gs.gameMode == GameMode.inAreaInput:
            for key in keypresses:
                # key is printable -> add it to buffer
                if len(key) == 1:
                    if len(gs.cmdBuffer) == 0 and key == ' ':
                        continue    # ignore 1st char spaces as that is used to advance text
                    gs.appendCmdBuffer(key)
                # key is backspace -> pop one char from buffer
                elif key == 'BackSpace':
                    gs.popCmdBuffer()
                # key is return -> commit command
                elif key == 'Return':
                    if gs.gameMode == GameMode.inAreaInput:
                        self.interpreter.resume(gs.cmdBuffer.strip())
                    else:   # GameMode.inAreaCommand
                        val = gs.traverseCmdMap()
                        if isinstance(val, BodyNode):   # valid normal command
                            # special logic for go to - change room ID TODO refactor
                            if gs.cmdBuffer.strip('. ')[0:5] == 'go to':
                                roomId = AssetLoader().reverseRoomLookup(gs.cmdBuffer.strip('. ')[5:].strip(), gs.areaId)
                                gs.enterRoom(roomId or gs.roomId)
                            self.interpreter.executeAction(val)
                        elif isinstance(val, str):      # valid metacommand
                            if val == 'view inventory':
                                gs.gameMode = GameMode.inAreaInventory
                            elif val == 'view map':
                                gs.gameMode = GameMode.inAreaMap
                            elif val == 'save game':
                                # write the save file in a separate thread and wait with loading screen
                                def writeFileFunc():
                                    gs.writeFile(Globals.SavePaths[gs.saveId])
                                    gs.pushMessage('Game saved to ' + Globals.SavePaths[gs.saveId] + '.')
                                    gs.unlockGameMode()
                                gs.lockGameMode(GameMode.isLoading)
                                t = threading.Thread(target=writeFileFunc)
                                t.daemon = True
                                t.start()
                            elif val == 'exit game':
                                gs.gameMode = GameMode.titleScreen
                        else:   # tuple or None - invalid command
                            if len(gs.cmdBuffer.strip('. ')) > 0:
                                gs.pushMessage('Command not recognized.')
                    gs.clearCmdBuffer()

    def draw(self):
        # clean pixels from last frame
        self.clear()

        gs = GameState()
        if gs.gameMode == GameMode.inAreaChoice:
            # display choices
            rStart = (self.height // 2) - (len(gs.choices) // 2)
            cStart = 3
            cursorOffset = 3
            r = 0
            for choice in gs.choices:
                for i, c in enumerate(choice):
                    self.pixels[rStart + r][cStart + cursorOffset + i] = c
                r += 1
            self.pixels[rStart + self.choiceInd][cStart] = '>'
            self.pixels[rStart + self.choiceInd][cStart+1] = '>'
        elif gs.gameMode == GameMode.inAreaCommand or gs.gameMode == GameMode.inAreaInput:
            midY = self.height // 2
            startCol = 3
            # add current command input
            cmdBuffer = gs.cmdBuffer
            fullLine = '>> ' + cmdBuffer + ('_' if len(cmdBuffer) < Globals.CmdMaxLength else '')
            col = 0
            for i, char in enumerate(fullLine):
                # Start a new line if necessary
                if startCol + col >= self.width:
                    midY += 1
                    col = startCol
                self.pixels[midY][startCol + col] = char
                col += 1

        return self.pixels
