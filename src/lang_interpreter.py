"""
Contains routines for executing the game's custom language.
"""

from global_vars import Globals
from game_state import GameState, GameMode
from lang_parser import BodyNode, LangNode, FuncNode
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
                    if len(node.args) < 1 or len(node.args) > 2:
                        raise Exception('unexpected number of args in inc')
                    gs.touchVar(node.args[0])
                    if len(node.args) == 1:
                        gs.variables[node.args[0]] = str(int(gs.variables[node.args[0]]) + 1)
                    elif len(node.args) == 2:
                        gs.variables[node.args[0]] = str(int(gs.variables[node.args[0]]) + int(node.args[1]))
                elif node.title in ['dec', 'sub']:
                    if len(node.args) < 1 or len(node.args) > 2:
                        raise Exception('unexpected number of args in dec')
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
                        gs.variables = str(val)
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
        varname = args[0]
        gs.touchVar(varname)
        if len(args) == 1:
            return gs.variables[varname] != '0'
        else:
            inventoryFlag = False
            if args[0] == 'inventory':
                inventoryFlag = True
                args = args[1:]
            if len(args) != 3:
                raise Exception('unexpected num of args')
            comparator = args[1]
            compare = args[2]
            mapToCheck = gs.variables
            if inventoryFlag:
                mapToCheck = gs.inventory
            if comparator in ['eq', '=', '==']:
                return mapToCheck[varname] == compare
            elif comparator in ['gt', '>']:
                return mapToCheck[varname] > int(compare)
            elif comparator in ['lt', '<']:
                return mapToCheck[varname] < int(compare)
            else:
                raise Exception('unknown comparator ' + str(comparator))

    def resume(self, val):
        """ completes a choice or input function with a value """
        self.drainCallStack(val)
        GameState().refreshCommandList()

    def executeAction(self, body):
        """ wrapper around stack manipulation to execute a BodyNode """
        self.callStack.append([body, 0])
        self.drainCallStack()
        GameState().refreshCommandList()

if __name__ == '__main__':
    i = Interpreter()
