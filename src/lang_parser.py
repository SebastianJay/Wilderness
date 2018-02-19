"""
Contains routines for parsing the game's custom language. Contains the node definitions.
"""

from global_vars import Globals

class ContainerNodeBase:
    """ Base class for parent/internal nodes """

    def __init__(self, nodes=[]):
        """ Contains a sequence of subnodes """
        self.nodes = nodes

    def __str__(self):
        ret = "ContainerNode[\n"
        for node in self.nodes:
            ret += str(node)
        ret += "]\n"
        return ret

    # TODO iterable

class ScriptNode(ContainerNodeBase):
    """
    Node representing a sequence of behaviors which can be taken on a certain object
    nodes member should be a sequence of BehaviorNodes
    """
    pass

class BodyNode(ContainerNodeBase):
    """
    Node containing a mixture of natural language and functions as child nodes
    nodes member should be a sequence of LangNodes and FuncNodes
    """
    pass

class BehaviorNode:
    """ Node representing a verb[], condition, reaction tuple of a certain action """

    def __init__(self, actions, condition, reaction):
        self.actions = actions
        self.condition = condition
        self.reaction = reaction

    def __str__(self):
        return ','.join(self.actions) + "; " + str(self.condition) + "; " + str(self.reaction)

class LangNode:
    """ Node that contains natural language to be displayed in game """

    def __init__(self, text='', formatting=[], variables=[]):
        """ string text to be displayed in game """
        self.text = text
        """
        formatting for text to modify color or style;
        list of tuples with tag name and inclusive start and end indices where tag applies;
        [(formatter, (index1, index2)),]
        """
        self.formatting = formatting
        """
        interpolated variable locations;
        list of tuples of variable name and index into self.text where variable starts
        [(varname, varindex),]
        """
        self.variables = variables

    def __str__(self):
        ret = "LangNode(text: " + self.text.replace("\n"," \\n ") + ", formatting: {"
        for tup in self.formatting:
            ret += str(tup) + ", "
        ret += '\n}, variables: {'
        for var, index in self.variables:
            ret += var + ": " + str(index) + ", "
        ret += "})\n"
        return ret

class FuncNode:
    """ Node that contains a function to be evaluated during runtime """

    def __init__(self, title='', args=[], inner=None):
        """ a string of the function name """
        self.title = title.lower()
        """ a list of strings of function parameters (other tokens separated by underscores) """
        self.args = args
        # typecheck the number of arguments
        if (self.title in ['set', 'inc', 'add', 'dec', 'sub'] and (len(self.args) < 1 or len(self.args) > 3)) \
            or (self.title in ['actionset', 'timeset'] and len(self.args) != 3) \
            or (self.title in ['if', 'elif'] and len(self.args) < 1) \
            or (self.title in ['init', 'unset'] and (len(self.args) < 1 or len(self.args) > 2)) \
            or (self.title in ['input', 'goto'] and len(self.args) != 1) \
            or (self.title in ['gameover', 'switchcharacter', 'random', 'choice', 'else'] and len(self.args) > 0):
            raise Exception('type check fail (number args) for $'+self.title)
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

class Parser:

    def strFind(self, string, target, startIndex=0):
        """ (internal) extension of str.find() that ignores escaped characters """
        index = string.find(target, startIndex)
        while index != -1:
            # check if character is "escaped" by being in art line
            previousNewlineIndex = string.rfind('\n', 0, index)
            if string[previousNewlineIndex+1] == '\\':
                nextNewlineIndex = string.find('\n', index)
                if nextNewlineIndex != -1:
                    index = string.find(target, nextNewlineIndex+1)
                else:
                    index = -1
                    break
            else:
                break
        return index

    def matchingBraceIndex(self, string, startIndex=0):
        """ (internal) identify index of matching close brace """
        seekIndex = startIndex
        openCount = 1
        while True:
            openIndex = self.strFind(string, '{', seekIndex)
            closeIndex = self.strFind(string, '}', seekIndex)
            if closeIndex == -1:
                raise Exception('No matching brace in string:\n' + string)
            elif openIndex != -1 and openIndex < closeIndex:
                openCount += 1
                seekIndex = openIndex + 1
            else:
                openCount -= 1
                if openCount == 0:
                    return closeIndex
                seekIndex = closeIndex + 1

    def splitByPipe(self, string, startIndex=0):
        """ (internal) performs a split by vertical pipe, accounting for functions """
        # where unprocessed string starts
        seekIndex = startIndex
        # where to start looking for a pipe
        pipeSeekIndex = startIndex
        # results contains the split substrings
        results = []
        while seekIndex < len(string):
            # find the pipe
            pipeIndex = self.strFind(string, '|', pipeSeekIndex)
            # no more pipes -> done
            if pipeIndex == -1:
                break
            # find the opening of a function
            openIndex = self.strFind(string, '{', pipeSeekIndex)
            # if function opens before pipe, the pipe might be part of subfunction inner
            if openIndex != -1 and openIndex < pipeIndex:
                # skip past the function and retry
                closeIndex = self.matchingBraceIndex(string, openIndex+1)
                pipeSeekIndex = closeIndex + 1
            # otherwise the pipe is part of this function inner
            else:
                # capture the substring and continue
                results.append(string[seekIndex:pipeIndex])
                seekIndex = pipeSeekIndex = pipeIndex + 1
        # append element between last pipe and end of string
        if seekIndex < len(string):
            results.append(string[seekIndex:])
        # remove any empty elements in results
        results = [result for result in results if len(result) > 0]
        return results

    def parseFormat(self, text):
        """ (internal) Reads color/style formatted text and returns (text, [(formatter, (index1,index2)),])"""
        # empty text case
        if len(text) == 0:
            return text, []

        seekIndex = 0
        formatting = []
        textWithoutFormatters = ""
        escapeCharCount = 0 if text[0] != '\\' else 1

        #While there are remaining "@"s in the string, format into a LangNode
        while self.strFind(text, "@", seekIndex) != -1:
            # count escape chars ("\" at beginning of line) between last formatter and this one
            indexOfAt = self.strFind(text, "@", seekIndex)
            escapeCharCount += text.count('\n\\', seekIndex, indexOfAt)

            # find indices
            indexOpenBracket = text.find("{", indexOfAt)
            indexCloseBracket = text.find("}", indexOpenBracket)

            #if no close or open bracket exists, exit the method and return error message
            if indexOpenBracket == -1:
                raise Exception("The formatter is missing an opening bracket: \n" + text)
            if indexCloseBracket == -1:
                raise Exception("The formatter is missing an closing bracket: \n" + text)

            # the formatted text looks like @formatter{formattedText}
            formatter = text[indexOfAt + 1 : indexOpenBracket].strip()
            formattedText = text[indexOpenBracket + 1 : indexCloseBracket]

            # textWithoutFormatters will hold the text with the @formatter{formattted_text} replaced with just formattedText
            textWithoutFormatters += text[seekIndex : indexOfAt]
            textWithoutFormatters += formattedText

            # Remember where in the textWithoutFormatters string each formatter applies
            # Decrement the indices by escapeCharCount since those will be removed afterward
            formatting.append((formatter,
                (len(textWithoutFormatters)-len(formattedText)-escapeCharCount,
                len(textWithoutFormatters)-1-escapeCharCount)))

            seekIndex = indexCloseBracket + 1   # start searching for the next @
        # capture remaining unformatted text
        textWithoutFormatters += text[seekIndex:]

        # Remove escape chars
        lines = textWithoutFormatters.split('\n')
        lines = [(line[1:] if len(line) > 0 and line[0] == '\\' else line) for line in lines]
        finalText = '\n'.join(lines)

        return finalText, formatting

    def parseFormatAndVars(self, text):
        """ (internal) parses text into a LangNode with formatter and variable locations """
        parsedText = ''         # text without variables and formatters
        allFormatting = []      # list of all formatters
        variablesList = []      # list of (varName, index into parsedText)
        seekIndex = 0

        def parseFormatSection(startIndex, endIndex):
            nonlocal parsedText
            nonlocal allFormatting
            # parse formatters of all text preceding variable
            textStub, formatting = self.parseFormat(text[startIndex:endIndex])
            formatting = [(tag, (ind1 + len(parsedText), ind2 + len(parsedText)))
                for (tag, (ind1, ind2)) in formatting]

            # add parsed values to return vars
            parsedText += textStub
            allFormatting.extend(formatting)

        # find location of start of variable
        while self.strFind(text, "[", seekIndex) != -1:
            # isolate name of variable
            indexStartBracket = self.strFind(text, "[", seekIndex)
            indexEndBracket = self.strFind(text, "]", indexStartBracket)
            varName = text[indexStartBracket+1 : indexEndBracket]

            # add parsed text and formatters
            parseFormatSection(seekIndex, indexStartBracket)
            # add variable
            variablesList.append((varName, len(parsedText)))

            # advance search index
            seekIndex = indexEndBracket + 1
        # parse formatters for text following last variable
        parseFormatSection(seekIndex, len(text))

        return LangNode(parsedText, allFormatting, variablesList)

    def preformatScriptString(self, scriptStr):
        """ (internal) prepares text before it is parsed as a BodyNode or full script file """
        # split bodyStr into lines
        lines = scriptStr.split('\n')
        # remove indenting by stripping leading/trailing spaces from lines
        lines = [line.strip() for line in lines]
        # replace tabs with one space for readability in window
        lines = [line.replace('\t', ' ') for line in lines]
        # remove single line comments
        lines = [line for line in lines if len(line) == 0 or line[0] != '#']
        # remove end of line comments
        lines = [(line[:line.index('#')] if '#' in line else line) for line in lines]
        # join back into one string
        scriptStr = '\n'.join(lines)
        return scriptStr

    def parseBody(self, scriptStr):
        """ (internal) Converts a string into a BodyNode """
        seekIndex = 0
        nodes = []
        while seekIndex < len(scriptStr):
            # locate a function by searching for $
            funcIndex = self.strFind(scriptStr, '$', seekIndex)
            # function not found -> all content can be captured in LangNode
            functionExists = funcIndex != -1
            # if content exists between current index and function, store in LangNode
            if not functionExists:
                langStr = scriptStr[seekIndex:].strip()
            else:
                langStr = scriptStr[seekIndex:funcIndex].strip()
            if langStr != "":
                langNode = self.parseFormatAndVars(langStr)
                nodes.append(langNode)
            # only proceed with function parsing if function exists
            if not functionExists:
                break
            # determine if function has inner (part surrounded by {})
            braceOpenIndex = self.strFind(scriptStr, '{', funcIndex)
            innerExists = (braceOpenIndex != -1 and len(scriptStr[funcIndex:braceOpenIndex].split()) == 1)
            # index where function name ends
            funcNameEndIndex = 0
            # string containing function inner, if it exists
            funcInnerStr = None
            # function has inner -> parse that portion
            if innerExists:
                braceCloseIndex = self.matchingBraceIndex(scriptStr, braceOpenIndex + 1)
                funcInnerStr = scriptStr[braceOpenIndex+1:braceCloseIndex]
                funcNameEndIndex = braceOpenIndex
                seekIndex = braceCloseIndex + 1
            # function has no inner
            else:
                # function description ends on newline
                newlineIndex = scriptStr.find('\n', funcIndex)
                if newlineIndex == -1:
                    newlineIndex = len(scriptStr)
                funcNameEndIndex = newlineIndex
                seekIndex = newlineIndex + 1
            # parse function title and args
            funcAllArgs = scriptStr[funcIndex+1:funcNameEndIndex].strip().split('_')
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
                        option = self.parseFormatAndVars(choices[i].strip())
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

    def parseScriptFragment(self, scriptStr):
        """ Converts fragment file contents into a BodyNode """
        scriptStr = self.preformatScriptString(scriptStr)
        return self.parseBody(scriptStr)

    def parseScript(self, scriptStr):
        """ Converts file contents string into a BehaviorNode """
        scriptStr = self.preformatScriptString(scriptStr)
        seekIndex = 0
        nodes = []
        while seekIndex < len(scriptStr):
            openIndex = scriptStr.find("{", seekIndex)
            if openIndex == -1:
                break
            verbCondLst = scriptStr[seekIndex:openIndex].split('|')
            verbLst = [verb.strip().lower() for verb in verbCondLst[0].split(',')]
            if len(verbCondLst) > 1:
                condition = verbCondLst[1].strip()
            else:
                condition = None
            closeIndex = self.matchingBraceIndex(scriptStr, openIndex + 1)
            reaction = self.parseBody(scriptStr[openIndex+1:closeIndex].strip())
            nodes.append(BehaviorNode(verbLst, condition, reaction))
            seekIndex = closeIndex + 1
        return ScriptNode(nodes)
