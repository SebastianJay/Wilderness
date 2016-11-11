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
                elif node.title == 'set':
                    if len(node.args) < 1 or len(node.args) > 3:
                        raise Exception('unexpected number of args in set')
                    if node.args[0] == 'inventory':
                        gs.touchInventory(node.args[1])
                        if len(node.args) == 2:
                            gs.inventory[node.args[1]] = '1'   #TODO
                        else:
                            gs.inventory[node.args[1]] = node.args[2]   #TODO
                    else:
                        gs.touchVar(node.args[0])
                        if len(node.args) == 1:
                            gs.variables[node.args[0]] = '1'
                        elif len(node.args) == 2:
                            gs.variables[node.args[0]] = node.args[1]
                elif node.title == 'init':
                    if len(node.args) < 1:
                        raise Exception('unexpected number of args in init')
                    gs.variables[node.args[0]] = '0'
                elif node.title in ['inc', 'add']:
                    if len(node.args) < 1 or len(node.args) > 3:
                        raise Exception('unexpected number of args in inc')
                    if node.args[0] == 'inventory':
                        gs.touchInventory(node.args[1])
                        if len(node.args) == 2:
                            gs.inventory[node.args[1]] = str(int(gs.inventory[node.args[1]]) + 1)   #TODO
                        else:
                            gs.inventory[node.args[1]] = str(int(gs.inventory[node.args[1]]) + int(node.args[2]))   #TODO
                    else:
                        gs.touchVar(node.args[0])
                        if len(node.args) == 1:
                            gs.variables[node.args[0]] = str(int(gs.variables[node.args[0]]) + 1)
                        elif len(node.args) == 2:
                            gs.variables[node.args[0]] = str(int(gs.variables[node.args[0]]) + int(node.args[1]))
                elif node.title in ['dec', 'sub']:
                    if len(node.args) < 1 or len(node.args) > 3:
                        raise Exception('unexpected number of args in dec')
                    if node.args[0] == 'inventory':
                        gs.touchInventory(node.args[1])
                        if len(node.args) == 2:
                            gs.inventory[node.args[1]] = str(int(gs.inventory[node.args[1]]) - 1)   #TODO
                        else:
                            gs.inventory[node.args[1]] = str(int(gs.inventory[node.args[1]]) - int(node.args[2]))   #TODO
                    else:
                        gs.touchVar(node.args[0])
                        if len(node.args) == 1:
                            gs.variables[node.args[0]] = str(int(gs.variables[node.args[0]]) - 1)
                        elif len(node.args) == 2:
                            gs.variables[node.args[0]] = str(int(gs.variables[node.args[0]]) - int(node.args[1]))
                elif node.title == 'input':
                    if val is not None:
                        gs.gameMode = GameMode.inAreaCommand
                        if len(node.args) != 1:
                            raise Exception('unexpected number of args in input')
                        gs.touchVar(node.args[0])
                        gs.variables[node.args[0]] = str(val)
                    else:
                        gs.gameMode = GameMode.inAreaInput
                        self.callStack[-1][1] = nodeInd
                        return False
                elif node.title == 'goto':
                    if len(node.args) != 1:
                        raise Exception('unexpected number of args in goto')
                    gs.roomId = node.args[0]
                elif node.title == 'unset':
                    if len(node.args) != 1:
                        raise Exception('unexpected number of args in unset')
                    if node.args[0] in gs.variables:
                        del gs.variables[node.args[0]]
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
        while len(self.callStack) > 0:
            body, ind = self.callStack[-1]
            lenStackBefore = len(self.callStack)
            noHalt = self.executeBody(body, ind, val)
            lenStackAfter = len(self.callStack)
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
        if len(args) == 0:
            raise Exception('no args found in evaluateCondition')

        gs = GameState()
        if len(args) == 1:
            varname = args[0]
            gs.touchVar(varname)
            return gs.variables[varname] != '0'
        else:
            inventoryFlag = False
            if args[0] == 'inventory':
                inventoryFlag = True
                args = args[1:]
            if len(args) != 3:
                raise Exception('unexpected num of args')
            varname = args[0]
            comparator = args[1]
            compare = args[2]
            mapToCheck = None
            if inventoryFlag:
                gs.touchInventory(varname)
                mapToCheck = gs.inventory
            else:
                gs.touchVar(varname)
                mapToCheck = gs.variables
            if comparator in ['eq', '=', '==']:
                return mapToCheck[varname] == compare
            elif comparator in ['gt', '>']:
                return int(mapToCheck[varname]) > int(compare)
            elif comparator in ['lt', '<']:
                return int(mapToCheck[varname]) < int(compare)
            else:
                raise Exception('unknown comparator ' + str(comparator))

    def resume(self, val):
        """ completes a choice or input function with a value """
        self.drainCallStack(val)
        self.refreshCommandList()

    def executeAction(self, body):
        """ wrapper around stack manipulation to execute a BodyNode """
        self.callStack.append([body, 0])
        self.drainCallStack()
        self.refreshCommandList()

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

if __name__ == '__main__':
    i = Interpreter()
