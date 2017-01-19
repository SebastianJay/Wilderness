"""
Contains routines for parsing the game's custom language. Contains the node definitions.
"""

from global_vars import Globals

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

    def __init__(self, text='', formatting=[], variables=[]):
        """ string text to be displayed in game """
        self.text = text
        """
        formatting for text to modify color or style;
        list of dicts that map tag to inclusive start and end indices where tag applies;
        each dict represents a portion of text without any interpolated variables, so its
         length is in [len(self.variables), len(self.variables)+1]
        [{formatter1: (index1, index2),},]
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
        for dct in self.formatting:
            for c in dct:
                ret += c + ": " + str(dct[c]) + ", "
            if len(dct) > 0:
                ret += "\n"
        ret += '}, variables: {'
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
    def __init__(self):
        pass

    def strFind(self, string, target, startInd=0):
        """ (internal) extension of str.find() that ignores escaped characters """
        ind = string.find(target, startInd)
        while ind != -1:
            # check if character is "escaped" by being in art line
            prev_nlind = string.rfind('\n', 0, ind)
            if string[prev_nlind+1] == '\\':
                next_nlind = string.find('\n', ind)
                if next_nlind != -1:
                    ind = string.find(target, next_nlind+1)
                else:
                    ind = -1
                    break
            else:
                break
        return ind

    def matchingBraceIndex(self, string, startInd=0):
        """ (internal) identify index of matching close brace """
        nextInd = startInd
        openCount = 1
        while True:
            openInd = self.strFind(string, '{', nextInd)
            closeInd = self.strFind(string, '}', nextInd)
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
        """ (internal) performs a split by vertical pipe, accounting for functions """
        # remainingInd represents where unprocessed string starts
        remainingInd = startInd
        # seekInd indicates where to start looking for a pipe
        seekInd = startInd
        # results contains the split substrings
        results = []
        while remainingInd < len(string):
            # find the pipe
            pipeInd = self.strFind(string, '|', seekInd)
            # no more pipes -> done
            if pipeInd == -1:
                break
            # find the opening of a function
            openInd = self.strFind(string, '{', seekInd)
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
        # remove any empty elements in results
        results = [result for result in results if len(result) > 0]
        return results

    def parseFormat(self, text):
        """ (internal) Reads color/style formatted text and returns (text, {formatter1 : [(index1,index2),],})"""
        # empty text case
        if len(text) == 0:
            return text, {}

        #index_of_at will track the last instance of the "@" character in the text
        index_of_at = 0
        index_close_bracket = -1
        previous_close_bracket = -1
        index_open_bracket = -1
        formatting = {} # dictionary of formation {string : tuple} of formatters and where they apply
        text_without_formatters = ""
        escape_char_count = 0 if text[0] != '\\' else 1

        #While there are remaining "@"s in the string, format into a LangNode
        while self.strFind(text, "@", index_of_at) != -1:
            # count escape chars ("\" at beginning of line) between last formatter and this one
            next_index_of_at = self.strFind(text, "@", index_of_at)
            escape_char_count += text.count('\n\\', index_of_at, next_index_of_at)

            # find indices
            index_of_at = next_index_of_at
            index_open_bracket = text.find("{", index_of_at)
            index_close_bracket = text.find("}", index_open_bracket)

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

            # Remember where in the text_without_formatters string each formatter applies
            # Decrement the indices by escape_char_count since those will be removed afterward
            if formatter not in formatting:
                formatting[formatter] = []
            formatting[formatter].append((len(text_without_formatters)-len(formatted_text)-escape_char_count,
                len(text_without_formatters)-1-escape_char_count))

            previous_close_bracket = index_close_bracket # remember where the previous } was
            index_of_at = index_close_bracket + 1   # start searching for the next @
        # capture remaining unformatted text
        text_without_formatters += text[previous_close_bracket+1:]

        # Remove escape chars
        lines = text_without_formatters.split('\n')
        lines = [(line[1:] if len(line) > 0 and line[0] == '\\' else line) for line in lines]
        final_text = '\n'.join(lines)

        return final_text, formatting

    def parseFormatAndVars(self, text):
        """ (internal) parses text into a LangNode with formatter and variable locations """
        parsed_text = ''        # text without variables and formatters
        formatting_list = []    # formatter indices between variables
        variables_list = []     # list of (var_name, index into parsed_text)
        index_seek = 0
        # find location of start of variable
        while self.strFind(text, "[", index_seek) != -1:
            # isolate name of variable
            index_start_bracket = self.strFind(text, "[", index_seek)
            index_end_bracket = self.strFind(text, "]", index_start_bracket)
            var_name = text[index_start_bracket+1 : index_end_bracket]
            # parse formatters of all text preceding variable
            text_stub, formatting = self.parseFormat(text[index_seek:index_start_bracket])
            parsed_text += text_stub
            formatting_list.append(formatting)
            variables_list.append((var_name, len(parsed_text)))
            index_seek = index_end_bracket + 1
        # parse formatters for text following last variable
        text_stub, formatting = self.parseFormat(text[index_seek:])
        if len(text_stub) > 0:
            parsed_text += text_stub
            formatting_list.append(formatting)
        return LangNode(parsed_text, formatting_list, variables_list)

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
        remainingInd = 0
        nodes = []
        while remainingInd < len(scriptStr):
            # locate a function by searching for $
            funcInd = self.strFind(scriptStr, '$', remainingInd)
            # function not found -> all content can be captured in LangNode
            functionExists = funcInd != -1
            # if content exists between current index and function, store in LangNode
            if not functionExists:
                langStr = scriptStr[remainingInd:].strip()
            else:
                langStr = scriptStr[remainingInd:funcInd].strip()
            if langStr != "":
                langNode = self.parseFormatAndVars(langStr)
                nodes.append(langNode)
            # only proceed with function parsing if function exists
            if not functionExists:
                break
            # determine if function has inner (part surrounded by {})
            braceOpenInd = self.strFind(scriptStr, '{', funcInd)
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
                    newlineInd = len(scriptStr)
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
        """ Converts file contents string into a list of (string verb, BodyNode reaction) tuples """
        scriptStr = self.preformatScriptString(scriptStr)
        remainingInd = 0
        tuples = []
        while remainingInd < len(scriptStr):
            braceLoc = scriptStr.find("{", remainingInd)
            if braceLoc == -1:
                break
            verbCondLst = scriptStr[remainingInd:braceLoc].split('|')
            verb = verbCondLst[0].strip().lower()
            if len(verbCondLst) > 1:
                condition = verbCondLst[1].strip()
            else:
                condition = None
            closeInd = self.matchingBraceIndex(scriptStr, braceLoc + 1)
            reaction = self.parseBody(scriptStr[braceLoc+1:closeInd].strip())
            tuples.append((verb, reaction, condition))
            remainingInd = closeInd + 1
        return tuples

if __name__ == '__main__':
    p = Parser()
