
class BodyNode:
    """ Node containing a mixture of natural language and functions as child nodes """

    def __init__(self, nodes=[]):
        """ contains a sequence of LangNodes and FuncNodes """
        self.nodes = nodes

class LangNode:
    """ Node that contains natural language to be displayed in game """

    def __init__(self, text='', formatting={}):
        """ text to be displayed in game """
        self.text = text
        """ formatting for text to modify color or style """
        self.formatting = formatting

class FuncNode:
    """ Node that contains a function to be evaluated during runtime """

    def __init__(self, title='', args=[], inner=None):
        """ a string of the function name """
        self.title = title
        """ a list of strings of function parameters (other tokens separated by underscores) """
        self.args = args
        """
        type of self.inner depends on self.title:
            if, elif, else -> BodyNode that gets executed if condition in args is true
            choice -> (LangNode, BodyNode)[] the BodyNode result for the chosen LangNode option is executed
            random -> BodyNode[] of which one gets randomly executed
        for other functions without {}, self.inner is None
        """
        self.inner = inner

class Interpreter:
    """ Contains parsing and execution routines for the game's custom scripting language. """

    def __init__(self):
        pass

    def parseBody(self, bodyStr):
        """ Converts a string into a BodyNode (can be called recursively) """
        pass

    def parseScript(self, scriptStr):
        """ Converts file contents string into a list of (string verb, BodyNode reaction) tuples """
        pass

    def executeBody(self, bodyNode):
        """ Evaluates a BodyNode """
        pass
