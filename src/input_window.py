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
        self.choiceIndex = 0

    def choiceChangeHandler(self):
        def _choiceChangeHandler(*args, **kwargs):
            self.choiceIndex = 0
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
        if gs.gameMode == GameMode.InAreaChoice:
            # move cursor between options
            for key in keypresses:
                if key == 'Up':
                    self.choiceIndex = (self.choiceIndex - 1) % len(gs.choices)
                elif key == 'Down':
                    self.choiceIndex = (self.choiceIndex + 1) % len(gs.choices)
                elif key == 'Return':
                    self.interpreter.resume(self.choiceIndex)
        elif gs.gameMode == GameMode.InAreaCommand or gs.gameMode == GameMode.InAreaInput:
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
                    if gs.gameMode == GameMode.InAreaInput:
                        self.interpreter.resume(gs.cmdBuffer.strip())
                    else:   # GameMode.InAreaCommand
                        val = gs.traverseCmdMap()
                        if isinstance(val, BodyNode):   # valid normal command
                            # special logic for go to - change room ID TODO refactor
                            if gs.cmdBuffer.strip('. ')[0:5] == 'go to':
                                roomId = AssetLoader().reverseRoomLookup(gs.cmdBuffer.strip('. ')[5:].strip(), gs.areaId)
                                gs.enterRoom(roomId or gs.roomId)
                            self.interpreter.executeAction(val)
                        elif isinstance(val, str):      # valid metacommand
                            if val == 'view inventory':
                                gs.gameMode = GameMode.InAreaInventory
                            elif val == 'view map':
                                gs.gameMode = GameMode.InAreaMap
                            elif val == 'save game':
                                # write the save file in a separate thread and wait with loading screen
                                def writeFileFunc():
                                    gs.writeFile(Globals.SavePaths[gs.saveId])
                                    gs.pushMessage('Game saved to ' + Globals.SavePaths[gs.saveId] + '.')
                                    gs.unlockGameMode()
                                gs.lockGameMode(GameMode.IsLoading)
                                t = threading.Thread(target=writeFileFunc)
                                t.daemon = True
                                t.start()
                            elif val == 'exit game':
                                gs.gameMode = GameMode.TitleScreen
                        else:   # tuple or None - invalid command
                            if len(gs.cmdBuffer.strip('. ')) > 0:
                                gs.pushMessage('Command not recognized.')
                    gs.clearCmdBuffer()

    def draw(self):
        self.clear()
        gs = GameState()
        cursor = '>> '
        startCol = 3
        if gs.gameMode == GameMode.InAreaChoice:
            startRow = (self.height // 2) - (len(gs.choices) // 2)
            # display choices
            self.writeTextLines(gs.choices, startRow, startCol + len(cursor))
            self.writeText(cursor, startRow + self.choiceIndex, startCol)
        elif gs.gameMode == GameMode.InAreaCommand or gs.gameMode == GameMode.InAreaInput:
            startRow = self.height // 2
            # add current command input
            fullLine = cursor + gs.cmdBuffer + ('_' if len(gs.cmdBuffer) < Globals.CmdMaxLength else '')
            self.writeText(fullLine, startRow, startCol, True)
