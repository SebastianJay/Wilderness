"""
Contains routines for executing the game's custom language.
"""

from global_vars import Globals
from game_state import GameState, GameMode
from lang_parser import BodyNode, LangNode, FuncNode
from asset_loader import AssetLoader
from random import randint
from enum import Enum

class Interpreter:

    # Specifies the exit conditions for executeBody
    class ExitCode(Enum):
        empty   = 0     # caller should empty the call stack
        pop     = 1     # caller should pop topmost stack frame
        push    = 2     # caller should executed newest stack frame
        halt    = 3     # caller should pause for user input

    def __init__(self):
        self.callStack = []

    # helper method to extract an argument's presence as a true/false value
    def extractFlag(self, args, argname):
        if args[0] == argname:
            return args[1:], True
        else:
            return args, False

    def extractInventory(self, args):
        return self.extractFlag(args, 'inventory')

    def extractNot(self, args):
        return self.extractFlag(args, 'not')

    # helper method to execute a BodyNode
    def executeBody(self, bodyNode, nodeInd, val=None):
        gs = GameState()
        while nodeInd < len(bodyNode.nodes):
            node = bodyNode.nodes[nodeInd]  # grab that node
            if isinstance(node, FuncNode):
                if node.title in ['if', 'elif']:
                    cond = self.evaluateCondition(node.args)
                    if cond:
                        # calculate where body should pick up
                        nodeInd += 1
                        while nodeInd < len(bodyNode.nodes) and \
                        isinstance(bodyNode.nodes[nodeInd], FuncNode) and \
                        bodyNode.nodes[nodeInd].title in ['elif', 'else']:
                            nodeInd += 1
                        # add to call stack and return to manager
                        self.callStack[-1][1] = nodeInd
                        self.callStack.append([node.inner, 0])
                        return Interpreter.ExitCode.push
                elif node.title == 'else':
                    self.callStack[-1][1] = nodeInd + 1
                    self.callStack.append([node.inner, 0])
                    return Interpreter.ExitCode.push
                elif node.title == 'choice':
                    if val is not None:
                        gs.gameMode = GameMode.inAreaCommand
                        pick = int(val)
                        self.callStack[-1][1] = nodeInd + 1
                        self.callStack.append([node.inner[pick][1], 0])
                        return Interpreter.ExitCode.push
                    else:
                        gs.gameMode = GameMode.inAreaChoice
                        # populate choice list in GameState
                        lstChoices = []
                        for choice in node.inner:
                            lstChoices.append(choice[0].text)
                        gs.choices = lstChoices
                        self.callStack[-1][1] = nodeInd
                        return Interpreter.ExitCode.halt
                elif node.title == 'random':
                    self.callStack[-1][1] = nodeInd + 1
                    self.callStack.append([node.inner[pick], 0])
                    return Interpreter.ExitCode.push
                elif node.title == 'init':
                    args, inventoryFlag = self.extractInventory(node.args)
                    gs.touchVar(args[0], inventoryFlag)
                elif node.title == 'unset':
                    args, inventoryFlag = self.extractInventory(node.args)
                    gs.delVar(args[0], inventoryFlag)
                elif node.title in ['set', 'inc', 'add', 'dec', 'sub']:
                    args, inventoryFlag = self.extractInventory(node.args)
                    # if command specifies amount to increment by use that, otherwise use 1
                    incVal = 1
                    if len(args) == 2:
                        incVal = int(args[1])
                    gs.touchVar(args[0], inventoryFlag)
                    # whether to add to an existing total
                    addVal = int(gs.getVar(args[0], inventoryFlag))
                    if node.title == 'set':
                        addVal = 0
                    # which direction to increment in
                    multiple = 1
                    if node.title in ['dec', 'sub']:
                        multiple = -1
                    gs.setVar(args[0], str(addVal + multiple * incVal), inventoryFlag)
                elif node.title == 'input':
                    if val is not None:
                        gs.gameMode = GameMode.inAreaCommand
                        gs.touchVar(node.args[0])
                        gs.setVar(node.args[0], str(val))
                    else:
                        gs.gameMode = GameMode.inAreaInput
                        self.callStack[-1][1] = nodeInd
                        return Interpreter.ExitCode.halt
                elif node.title == 'goto':
                    gs.roomId = node.args[0]
                elif node.title == 'exit':
                    return Interpreter.ExitCode.empty
                elif node.title == 'gameover':
                    pass    #TODO
                elif node.title == 'switchcharacter':
                    gs.switchCharacter()
                    return Interpreter.ExitCode.empty
                elif node.title == 'fragment':
                    self.callStack[-1][1] = nodeInd + 1
                    path = AssetLoader().getConfig(Globals.FragmentsConfigPath)[node.args[0]]['path']
                    frag = AssetLoader().getScriptFragment(path)
                    self.callStack.append([frag, 0])
                    return Interpreter.ExitCode.push
            elif isinstance(node, LangNode):
                gs.addLangNode(node)
            else:
                raise Exception('Unexpected type in BodyNode nodes ' + str(node))
            nodeInd += 1
            val = None  # invalidate passed in value as soon as it is used
        return Interpreter.ExitCode.pop

    def drainCallStack(self, val=None):
        """ Simulates a stack machine executing a tree of function calls """
        while len(self.callStack) > 0:
            body, ind = self.callStack[-1]
            exitCode = self.executeBody(body, ind, val)
            val = None  # invalidate passed in value as soon as it is used
            if exitCode == Interpreter.ExitCode.push:
                # body added new stack frame, so execute the newly pushed one
                continue
            elif exitCode == Interpreter.ExitCode.pop:
                # topmost stack frame is finished
                self.callStack.pop()
            elif exitCode == Interpreter.ExitCode.empty:
                # remove all existing stack frames
                self.callStack.clear()
            elif exitCode == Interpreter.ExitCode.halt:
                # keep stack as is and go back to get user input
                return False
            else:
                raise Exception('Unknown return value from executeBody: ' + str(exitCode))
        return True

    def evaluateCondition(self, args):
        """ returns True if the condition specified by args is true """
        gs = GameState()
        # return inverse of following condition if prefixed with 'not'
        args, notFlag = self.extractNot(args)
        # default to variables, but use inventory if it is first arg
        args, inventoryFlag = self.extractInventory(args)
        varname = args[0]
        gs.touchVar(varname, inventoryFlag)
        varval = gs.getVar(varname, inventoryFlag)
        retval = None
        if len(args) == 1:
            # no comparator -> check if var exists in mapping as nonzero value
            retval = varval != '0'
        else:
            # check variables or inventory with given key
            comparator = args[1]
            compare = args[2]
            # consult mappings to allow var to var comparisons
            if gs.getVar(compare, inventoryFlag) is not None:
                compare = gs.getVar(compare, inventoryFlag)
            # do the comparison
            if comparator in ['eq', '=', '==']:
                retval = varval == compare
            elif comparator in ['gt', '>']:
                retval = int(varval) > int(compare)
            elif comparator in ['lt', '<']:
                retval = int(varval) < int(compare)
            else:
                raise Exception('unknown comparator ' + str(comparator))
        # reverse the retval if notFlag is true
        return retval if not notFlag else not retval

    def evaluateConditionTree(self, obj):
        if isinstance(obj, dict):
            # if dict, then we 'and' or 'or' multiple subtrees together
            if len(obj) != 1:
                raise Exception('malformed argument in evaluateConditionTree: ' + str(obj))
            op = list(obj.keys())[0]
            children = []
            for val in obj[op]:
                children.append(self.evaluateConditionTree(val))
            if op == 'or':
                retval = False
                for child in children:
                    retval = retval or child
                return retval
            elif op == 'and':
                retval = True
                for child in children:
                    retval = retval and child
                return retval
            else:
                raise Exception('malformed argument in evaluateConditionTree: ' + str(obj))
        elif isinstance(obj, str):
            return self.evaluateConditionTree(obj.split('_'))  # leaf of tree, convert to list
        elif isinstance(obj, list):
            return self.evaluateCondition(obj)  # parse list of tokens normally
        raise Exception('malformed argument in evaluateConditionTree: ' + str(obj))

    def refreshCommandList(self):
        """ Updates GameState cmdMap to contain all commands player can type """
        # Helper method to see if rooms or objects are visible in game
        def isVisible(self, obj):
            # if parameter is part of config possibly containing showIf
            if isinstance(obj, dict):
                if 'showIf' in obj:
                    conditionVal = obj['showIf']
                    return self.evaluateConditionTree(conditionVal)
            # if parameter is tuple of (verb, reaction, condition)
            if isinstance(obj, tuple):
                if obj[2] is not None:
                    return self.evaluateCondition(obj[2].split('_'))
            return True # visible by default

        # locate the rooms and objects configs
        loader = AssetLoader()
        gs = GameState()
        area = loader.getConfig(Globals.AreasConfigPath)[gs.areaId]
        items = loader.getConfig(Globals.ItemsConfigPath)
        rooms = loader.getConfig(area['roomsConfig'])
        objects = loader.getConfig(area['objectsConfig'])
        # locate the relevant scripts
        cmdMap = {}
        roomScript = loader.getScript(rooms[gs.roomId]['script'])
        objectNames = []
        objectScripts = []
        for obj in rooms[gs.roomId]['objects']:
            if not isVisible(self, objects[obj]):
                continue    # do not show the object if conditions not met
            objectNames.append(objects[obj]['name'])
            objectScripts.append(loader.getScript(objects[obj]['script']))
        # fill out the mapping, starting with 'go to'
        cmdMap['go to'] = {}
        for neighbor in rooms[gs.roomId]['neighbors']:
            if not isVisible(self, rooms[neighbor]):
                continue    # do not show the room if conditions not met
            neighborName = rooms[neighbor]['name']
            neighborScript = loader.getScript(rooms[neighbor]['script'])
            neighborReaction = None
            for action in neighborScript:
                if not isVisible(self, action):
                    continue
                if action[0] == 'go to':
                    neighborReaction = action[1]
            cmdMap['go to'][neighborName] = neighborReaction
        # go through actions to take on room
        for action in roomScript:
            # ignore 'go to' current room (not possible)
            if action[0] == 'go to' or not isVisible(self, action):
                continue
            cmdMap[action[0]] = action[1]
        # prefill 'use <item>', 'give <item>', 'show <item>'
        itemActionPhrases = [('use', 'on'), ('give', 'to'), ('show', 'to')]
        # go through actions to take on objects
        for i in range(len(objectScripts)):
            objScript = objectScripts[i]
            objName = objectNames[i]
            for action in objScript:
                if not isVisible(self, action):
                    continue
                verbWords = action[0].split()
                # "use .. on", "give ... to", "show ... to" needs special treatment for inventory items
                for prefix, suffix in itemActionPhrases:
                    if verbWords[0] == prefix and verbWords[-1] == suffix:
                        itemWord = ' '.join(verbWords[1:-1])
                        itemKey = loader.reverseItemLookup(itemWord)
                        targetPhrase = suffix + ' ' + objName
                        if itemKey == '':
                            raise Exception('script item name', itemWord ,'not found in items configuration file')
                        if itemKey in gs.inventory and int(gs.inventory[itemKey]) > 0:
                            if prefix not in cmdMap:
                                cmdMap[prefix] = {}
                            if itemWord not in cmdMap[prefix]:
                                cmdMap[prefix][itemWord] = {}
                            cmdMap[prefix][itemWord][targetPhrase] = action[1]
                        break
                # all other verbs are straightforward
                else:
                    if action[0] not in cmdMap:
                        cmdMap[action[0]] = {}
                    cmdMap[action[0]][objName] = action[1]
        gs.cmdMap = cmdMap

    def resume(self, val):
        """ completes a choice or input function with a value """
        self.drainCallStack(val)
        self.refreshCommandList()

    def executeAction(self, body):
        """ wrapper around stack manipulation to execute a BodyNode """
        self.callStack.append([body, 0])
        self.drainCallStack()
        self.refreshCommandList()

if __name__ == '__main__':
    i = Interpreter()
