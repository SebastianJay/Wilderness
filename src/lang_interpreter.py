"""
Contains routines for executing the game's custom language.
"""

from global_vars import Globals
from game_state import GameState, GameMode
from lang_parser import BodyNode, LangNode, FuncNode
from asset_loader import AssetLoader
from random import randint

class Interpreter:
    """ Contains parsing and execution routines for the game's custom scripting language. """

    def __init__(self):
        self.callStack = []

    # helper method to extract the 'inventory' arg as a true/false value
    def extractInventory(self, args):
        if args[0] == 'inventory':
            return args[1:], True
        else:
            return args, False

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
                        return True
                elif node.title == 'else':
                    self.callStack[-1][1] = nodeInd + 1
                    self.callStack.append([node.inner, 0])
                    return True
                elif node.title == 'choice':
                    if val is not None:
                        gs.gameMode = GameMode.inAreaCommand
                        pick = int(val)
                        self.callStack[-1][1] = nodeInd + 1
                        self.callStack.append([node.inner[pick][1], 0])
                        return True
                    else:
                        gs.gameMode = GameMode.inAreaChoice
                        # populate choice list in GameState
                        lstChoices = []
                        for choice in node.inner:
                            lstChoices.append(choice[0].text)
                        gs.choiceList = lstChoices
                        self.callStack[-1][1] = nodeInd
                        return False
                elif node.title == 'random':
                    self.callStack[-1][1] = nodeInd + 1
                    self.callStack.append([node.inner[pick], 0])
                    return True
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
                        return False
                elif node.title == 'goto':
                    gs.roomId = node.args[0]
                elif node.title == 'gameover':
                    pass    #TODO
                elif node.title == 'switchcharacter':
                    pass    #TODO
            elif isinstance(node, LangNode):
                GameState().addLangNode(node)
            else:
                raise Exception('Unexpected type in BodyNode nodes ' + str(node))
            nodeInd += 1
        return True

    def drainCallStack(self, val=None):
        """ Simulates a stack machine executing a tree of function calls """
        while len(self.callStack) > 0:
            body, ind = self.callStack[-1]
            lenStackBefore = len(self.callStack)
            noHalt = self.executeBody(body, ind, val)
            lenStackAfter = len(self.callStack)
            val = None  # invalidate passed in value as soon as it is used
            if lenStackAfter > lenStackBefore:
                # body added new stack frame, so execute the newly enqueued one
                continue
            else:
                if noHalt:
                    self.callStack.pop()
                else:
                    return False
        return True

    def evaluateCondition(self, args):
        """ returns True if the condition specified by args is true """
        gs = GameState()
        # default to variables, but use inventory if it is first arg
        args, inventoryFlag = self.extractInventory(args)
        varname = args[0]
        gs.touchVar(varname, inventoryFlag)
        varval = gs.getVar(varname, inventoryFlag)
        # if no comparator, check if var exists in mapping as nonzero value
        if len(args) == 1:
            return varval != '0'
        comparator = args[1]
        compare = args[2]
        # consult mappings to allow var to var comparisons
        if gs.getVar(compare, inventoryFlag) is not None:
            compare = gs.getVar(compare, inventoryFlag)
        # do the comparison
        if comparator in ['eq', '=', '==']:
            return varval == compare
        elif comparator in ['gt', '>']:
            return int(varval) > int(compare)
        elif comparator in ['lt', '<']:
            return int(varval) < int(compare)
        else:
            raise Exception('unknown comparator ' + str(comparator))

    def refreshCommandList(self):
        """ Updates GameState cmdMap to contain all commands player can type """
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
            objectNames.append(objects[obj]['name'])
            objectScripts.append(loader.getScript(objects[obj]['script']))
        # fill out the mapping, starting with 'go to'
        cmdMap['go to'] = {}
        for neighbor in rooms[gs.roomId]['neighbors']:
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
        for item in gs.inventory:
            if int(gs.inventory[item]) == 0:
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
                    if itemKey in gs.inventory and int(gs.inventory[itemKey]) > 0:
                        if cmdMap['use'][itemWord] is None:
                            cmdMap['use'][itemWord] = {}
                        cmdMap['use'][itemWord][targetPhrase] = action[1]
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
