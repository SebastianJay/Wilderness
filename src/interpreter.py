"""
Contains routines for parsing and executing the game's custom language.
"""

from global_vars import Globals
from game_state import GameState, GameMode
from random import randint

class BodyNode:
    """ Node containing a mixture of natural language and functions as child nodes """

    def __init__(self, nodes=[]):
        """ contains a sequence of LangNodes and FuncNodes """
        self.nodes = nodes

    def __str__(self):
        ret = "BodyNode[\n"
        for a in self.nodes:
            ret += str(a)
        ret += "]\n"
        return ret

class LangNode:
    """ Node that contains natural language to be displayed in game """

    def __init__(self, text='', formatting={}):
        """ text to be displayed in game """
        self.text = text
        # remove beginning forward slash (syntax for preserving leading spaces)
        lines = self.text.split('\n')
        lines = [(line[1:] if len(line) > 0 and line[0] == '\\' else line) for line in lines]
        self.text = '\n'.join(lines)

        """ formatting for text to modify color or style """
        self.formatting = formatting

    def __str__(self):
        ret = "LangNode(text: " + self.text.replace("\n"," \\n ") + ", formatting: {"
        for c in self.formatting.keys():
            ret += c + ": " + str(self.formatting[c]) + ", "
        ret += "})\n"
        return ret

class FuncNode:
    """ Node that contains a function to be evaluated during runtime """

    def __init__(self, title='', args=[], inner=None):
        """ a string of the function name """
        self.title = title.lower()
        """ a list of strings of function parameters (other tokens separated by underscores) """
        self.args = args
        """
        type of self.inner depends on self.title:
            if, elif, else -> BodyNode - gets executed if condition in args is true
            choice -> (LangNode, BodyNode)[] - the BodyNode result for the chosen LangNode option is executed
            random -> BodyNode[] - one from list gets randomly executed
        for other functions without {}, self.inner is None
        """
        self.inner = inner

    def __str__(self):
        ret = "FuncNode(title: " + self.title + ", args: " + str(self.args)
        if self.inner is not None:
            ret += ", inner: [\n"
            if self.title == 'if' or self.title == 'elif' or self.title == 'else':
                ret += str(self.inner)
            elif self.title == 'choice':
                for a in self.inner:
                    ret += "("
                    ret += "choice: " + str(a[0])
                    ret += "result: " + str(a[1])[:-1]
                    ret += "),\n"
            elif self.title == 'random':
                for a in self.inner:
                    ret += str(a)
            ret += "])\n"
        else:
            ret += ")\n"
        return ret

class Interpreter:
    """ Contains parsing and execution routines for the game's custom scripting language. """

    def __init__(self):
        self.callStack = []

    def matchingBraceIndex(self, string, startInd=0):
        """ identify index of matching close brace """
        nextInd = startInd
        openCount = 1
        while True:
            openInd = string.find('{', nextInd)
            closeInd = string.find('}', nextInd)
            if closeInd == -1:
                raise Exception('No matching brace in string:\n' + string)
            elif openInd != -1 and openInd < closeInd:
                openCount += 1
                nextInd = openInd + 1
            else:
                openCount -= 1
                if openCount == 0:
                    return closeInd
                nextInd = closeInd + 1

    def splitByPipe(self, string, startInd=0):
        """ performs a split by vertical pipe, accounting for functions """
        # remainingInd represents where unprocessed string starts
        remainingInd = startInd
        # seekInd indicates where to start looking for a pipe
        seekInd = startInd
        # results contains the split substrings
        results = []
        while remainingInd < len(string):
            # find the pipe
            pipeInd = string.find('|', seekInd)
            # no more pipes -> done
            if pipeInd == -1:
                break
            # find the opening of a function
            openInd = string.find('{', seekInd)
            # if function opens before pipe, the pipe might be part of subfunction inner
            if openInd != -1 and openInd < pipeInd:
                # skip past the function and retry
                closeInd = self.matchingBraceIndex(string, openInd+1)
                seekInd = closeInd + 1
            # otherwise the pipe is part of this function inner
            else:
                # capture the substring and continue
                results.append(string[remainingInd:pipeInd])
                seekInd = pipeInd + 1
                remainingInd = pipeInd + 1
        # append element between last pipe and end of string
        if remainingInd < len(string):
            results.append(string[remainingInd:])
        return results

    def parseFormat(self, text):
        """
        Reads color/style formatted text and returns
        LangNode(text, {formatter1 : [(index1,index2), (index3, index4)], formatter2 : ...})
        """
        #index_of_at will track the last instance of the "@" character in the text
        index_of_at = 0
        index_close_bracket = -1
        previous_close_bracket = -1
        index_open_bracket = -1
        formatting = {} # dictionary of formation {string : tuple} of formatters and where they apply
        text_without_formatters = ""

        #While there are remaining "@"s in the string, format into a LangNode
        while text.find("@", index_of_at) != -1:
            index_of_at = text.find("@", index_of_at)
            index_open_bracket = text.find("{", index_of_at)
            index_close_bracket = text.find("}", index_of_at)

            #if no close or open bracket exists, exit the method and return error message
            if index_open_bracket == -1:
                raise Exception("The formatter is missing an opening bracket: \n" + text)
            if index_close_bracket == -1:
                raise Exception("The formatter is missing an closing bracket: \n" + text)

            # the formatted text looks like @formatter{formatted_text}
            formatter = text[index_of_at + 1 : index_open_bracket].strip()
            formatted_text = text[index_open_bracket + 1 : index_close_bracket]

            # text_without_formatters will hold the text with the @formatter{formattted_text} replaced with just formatted_text
            text_without_formatters += text[previous_close_bracket + 1 : index_of_at]
            text_without_formatters += formatted_text

            if Globals.IsDev:
                print("index_of_at: " + str(index_of_at))
                print("index_open_bracket: " + str(index_open_bracket))
                print("index_close_bracket: " + str(index_close_bracket))
                print("formatter: " + formatter)
                print("formatted_text: " + formatted_text + "\n")

            # Remember where in the text_without_formatters string each formatter applies
            if formatter not in formatting:
                formatting[formatter] = []
            formatting[formatter].append((len(text_without_formatters)-len(formatted_text), len(text_without_formatters) -1))

            previous_close_bracket = index_close_bracket # remember where the previous } was
            index_of_at = index_of_at + 1   # start searching for the next @ after the previous @

        # capture remaining unformatted text
        text_without_formatters += text[previous_close_bracket+1:]
        return LangNode(text_without_formatters, formatting)

    def parseBody(self, scriptStr):
        """ Converts a string into a BodyNode """
        remainingInd = 0
        nodes = []
        while remainingInd < len(scriptStr):
            # locate a function by searching for $
            funcInd = scriptStr.find('$', remainingInd)
            # function not found -> all content can be captured in LangNode
            functionExists = funcInd != -1
            # if content exists between current index and function, store in LangNode
            if not functionExists:
                langStr = scriptStr[remainingInd:].strip()
            else:
                langStr = scriptStr[remainingInd:funcInd].strip()
            if langStr != "":
                langNode = self.parseFormat(langStr)
                nodes.append(langNode)
            # only proceed with function parsing if function exists
            if not functionExists:
                break
            # determine if function has inner (part surrounded by {})
            braceOpenInd = scriptStr.find('{', funcInd)
            innerExists = (braceOpenInd != -1 and len(scriptStr[funcInd:braceOpenInd].split()) == 1)
            # index where function name ends
            funcNameEndInd = 0
            # string containing function inner, if it exists
            funcInnerStr = None
            # function has inner -> parse that portion
            if innerExists:
                braceCloseInd = self.matchingBraceIndex(scriptStr, braceOpenInd + 1)
                funcInnerStr = scriptStr[braceOpenInd+1:braceCloseInd]
                funcNameEndInd = braceOpenInd
                remainingInd = braceCloseInd + 1
            # function has no inner
            else:
                # function description ends on newline
                newlineInd = scriptStr.find('\n', funcInd)
                if newlineInd == -1:
                    newlineInd = len(scriptStr) - 1
                funcNameEndInd = newlineInd
                remainingInd = newlineInd + 1
            # parse function title and args
            funcAllArgs = scriptStr[funcInd+1:funcNameEndInd].strip().split('_')
            funcTitle = funcAllArgs[0]
            funcArgs = funcAllArgs[1:]
            funcInner = None
            # parse inner based on title
            if funcTitle == 'if' or funcTitle == 'elif' or funcTitle == 'else':
                funcInner = self.parseBody(funcInnerStr.strip())
            elif funcTitle == 'choice':
                choices = self.splitByPipe(funcInnerStr.strip())
                funcInner = []
                option = None
                result = None
                for i in range(len(choices)):
                    if i % 2 == 0:
                        option = self.parseFormat(choices[i].strip())
                    else:
                        result = self.parseBody(choices[i].strip())
                        funcInner.append((option, result))
            elif funcTitle == 'random':
                funcInner = []
                choices = self.splitByPipe(funcInnerStr.strip())
                for a in choices:
                    funcInner.append(self.parseBody(a.strip()))
            funcNode = FuncNode(funcTitle, funcArgs, funcInner)
            nodes.append(funcNode)
        return BodyNode(nodes)

    def parseScript(self, scriptStr):
        """ Converts file contents string into a list of (string verb, BodyNode reaction) tuples """
        # split bodyStr into lines
        lines = scriptStr.split('\n')
        # remove indenting by stripping leading/trailing spaces from lines
        lines = [line.strip() for line in lines]
        # remove single line comments
        lines = [line for line in lines if len(line) == 0 or line[0] != '#']
        # remove end of line comments
        lines = [(line[:line.index('#')] if '#' in line else line) for line in lines]
        # join back into one string
        scriptStr = '\n'.join(lines)
        remainingInd = 0
        tuples = []
        while remainingInd < len(scriptStr):
            braceLoc = scriptStr.find("{", remainingInd)
            if braceLoc == -1:
                break
            verb = scriptStr[remainingInd:braceLoc].strip().lower()
            closeInd = self.matchingBraceIndex(scriptStr, braceLoc + 1)
            reaction = self.parseBody(scriptStr[braceLoc+1:closeInd].strip())
            tuples.append((verb, reaction))
            remainingInd = closeInd + 1
        return tuples

    def evaluateCondition(self, args):
        if len(args) == 0:
            raise Exception('no args found in evaluateCondition')

        gs = GameState()
        varname = args[0]
        gs.touchVar(varname)
        if len(args) == 1:
            return gs.variables[varname] != '0'
        else:
            if len(args) != 3:
                raise Exception('unexpected num of args')
            comparator = args[1]
            compare = args[2]
            if comparator in ['eq', '=', '==']:
                return gs.variables[varname] == compare
            elif comparator in ['gt', '>']:
                return gs.variables[varname] > int(compare)
            elif comparator in ['lt', '<']:
                return gs.variables[varname] < int(compare)
            else:
                raise Exception('unknown comparator ' + str(comparator))

    def executeBody(self, bodyNode, nodeInd, val=None):
        gs = GameState()
        while nodeInd < len(bodyNode.nodes):
            node = bodyNode.nodes[nodeInd]  # grab that node
            if isinstance(node, FuncNode):
                if node.title in ['if', 'elif']:
                    cond = evaluateCondition(node.args)
                    if cond:
                        # calculate where body should pick up
                        nodeInd += 1
                        while nodeInd < len(bodyNode.nodes) and \
                        isinstance(bodyNode.nodes[nodeInd], FuncNode) and \
                        bodyNode.nodes[nodeInd].title in ['elif', 'else']:
                            nodeInd += 1
                        # add to call stack and return to manager
                        self.callStack[-1][1] = nodeInd
                        self.callStack.append((node.inner, 0))
                        return True
                elif node.title == 'else':
                    self.callStack[-1][1] = nodeInd + 1
                    self.callStack.append((node.inner, 0))
                    return True
                elif node.title == 'choice':
                    if val is not None:
                        gs.gameMode = GameMode.inAreaCommand
                        pick = int(val)
                        self.callStack[-1][1] = nodeInd + 1
                        self.callStack.append((node.inner[pick], 0))
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
                    self.callStack.append((node.inner[pick], 0))
                    return True
                elif node.title == 'set':
                    if len(node.args) < 1 or len(node.args) > 2:
                        raise Exception('unexpected number of args in set')
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
                        gs.variables[node.args[0]] = str(int(gs.variables[node.args[0]]) + int(gs.variables[node.args[1]]))
                elif node.title in ['dec', 'sub']:
                    if len(node.args) < 1 or len(node.args) > 2:
                        raise Exception('unexpected number of args in dec')
                    gs.touchVar(node.args[0])
                    if len(node.args) == 1:
                        gs.variables[node.args[0]] = str(int(gs.variables[node.args[0]]) - 1)
                    elif len(node.args) == 2:
                        gs.variables[node.args[0]] = str(int(gs.variables[node.args[0]]) - int(gs.variables[node.args[1]]))
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

    def resume(self, val):
        """ completes a choice or input function with a value """
        self.drainCallStack(val)

    def executeAction(self, body):
        """ wrapper around stack manipulation to execute a BodyNode """
        self.callStack.append([body, 0])
        self.drainCallStack()

if __name__ == '__main__':
    i = Interpreter()
    print(i.parseFormat("Hello @red{there}, friend. How are @bold{you} doing?"))
    print(i.parseFormat("@blue{This} is blue. But @italic{this} is italicized. And @blue{this one} is also blue."))
