
class BodyNode:
    """ Node containing a mixture of natural language and functions as child nodes """

    def __init__(self, nodes=[]):
        """ contains a sequence of LangNodes and FuncNodes """
        self.nodes = nodes

    def __str__(self):
        print("BodyNode[")
        #for a in self.nodes:
        #    a.printString()
        for a in self.nodes:
            print(a)
        print("]")

class LangNode:
    """ Node that contains natural language to be displayed in game """

    def __init__(self, text='', formatting={}):
        """ text to be displayed in game """
        self.text = text
        """ formatting for text to modify color or style """
        self.formatting = formatting

    def __str__(self):
        print("LangNode(text: " + self.text.replace("\n"," \\n ") + ", formatting: {", end="")
        for c in self.formatting.keys():
            print(c + ": " + self.formatting[c], end = "")
        print("})")

class FuncNode:
    """ Node that contains a function to be evaluated during runtime """

    def __init__(self, title='', args=[], inner=None):
        """ a string of the function name """
        self.title = title
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
        print("FuncNode(title: " + self.title + ", \nargs: " + (str)(self.args) + ",")
        print("inner: [")
        if self.inner is not None:
            for a in self.inner:
                print("(", end = "")
                print(a[0])
                print(a[1])
        print("])")

class Interpreter:
    """ Contains parsing and execution routines for the game's custom scripting language. """

    def __init__(self):
        pass

    def matchingBraceIndex(string, startInd=0):
        """ identify index of matching close brace """
        nextInd = startInd
        openCount = 1
        while True:
            openInd = strIndex(string, '{', nextInd)
            closeInd = strIndex(string, '}', nextInd)
            if closeInd == -1:
                # error, no matching brace
                # throw exception
                pass
            elif openInd == -1:
                return closeInd
            elif openInd < closeInd:
                openCount += 1
                nextInd = openInd + 1
            else:
                openCount -= 1
                if openCount == 0:
                    return closeInd
                nextInd = closeInd + 1

    def strIndex(string, target, startInd=0):
        """ utility method for finding index substrings """
        return string.index(target, startInd) if target in string else -1

    def parseBody(self, bodyStr):
        """ Converts a string into a BodyNode """

        def parseBodyRec(scriptStr):
            """ Recursive helper for parseBody """
            remainingInd = 0
            nodes = []
            while remainingInd < len(scriptStr):
                # locate a function by searching for $
                funcInd = strIndex(scriptStr, '$', remainingInd)
                # function not found -> all content can be captured in LangNode
                functionExists = funcInd != -1
                # if content exists between current index and function, store in LangNode
                if not functionExists:
                    langStr = scriptStr[remainingInd:].strip()
                else:
                    langStr = scriptStr[remainingInd:funcInd].strip()
                if langStr != "":
                    langNode = LangNode(langStr)
                    nodes.append(langNode)
                # only proceed with function parsing if function exists
                if not functionExists:
                    break
                # determine if function has inner (part surrounded by {})
                braceOpenInd = strIndex(scriptStr, '{', funcInd)
                innerExists = (braceOpenInd != -1 and len(scriptStr[funcInd:braceOpenInd].split()) == 1)
                # index where function name ends
                funcNameEndInd = 0
                # string containing function inner, if it exists
                funcInnerStr = None
                # function has inner -> parse that portion
                if innerExists:
                    braceCloseInd = matchingBraceIndex(scriptStr, braceOpenInd + 1)
                    funcInnerStr = scriptStr[braceOpenInd+1:braceCloseInd]
                    funcNameEndInd = braceOpenInd
                    remainingInd = braceCloseInd + 1
                # function has no inner
                else:
                    # function description ends on newline
                    newlineInd = strIndex(scriptStr, '\n', funcInd)
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
                    funcInner = parseBodyRec(funcInnerStr.strip())
                elif funcTitle == 'choice':
                    choices = funcInnerStr.split("|")
                    funcInner = []
                    option = None
                    result = None
                    for i in range(len(choices)):
                        if i % 2 = 0:
                            option = LangNode(choices[i].strip())
                        else:
                            result = parseBodyRec(choices[i].strip())
                            funcInner.append((option, result))
                elif funcTitle == 'random':
                    funcInner = []
                    choices = funcInnerStr.split("|")
                    for a in choices:
                        funcInner.append(parseBodyRec(a.strip()))
                else:
                    funcInner = None
                funcNode = FuncNode(funcTitle, funcArgs, funcInner)
                nodes.append(funcNode)
            return BodyNode(nodes)
        # recursively parse body
        return parseBodyRec(scriptStr)

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
        # remove beginning forward slash (syntax for preserving leading spaces)
        #lines = [(line[1:] if len(line) > 0 and line[0] == '\\' else line) for line in lines]
        # join back into one string
        scriptStr = '\n'.join(lines)
        remainingInd = 0
        tuples = []
        while remainingInd < len(scriptStr):
            braceloc = strIndex(scriptStr, "{", remainingInd)
            if braceloc == -1:
                break
            verb = scriptStr[remainingInd:braceloc].strip()
            closeInd = matchingBraceIndex(scriptStr, braceloc + 1)
            reaction = parseBody(scriptStr[braceloc+1:closeInd].strip())
            tuples.append((verb, reaction))
            remainingInd = closeInd + 1
        pass

    def executeBody(self, bodyNode):
        """ Evaluates a BodyNode """
        pass
