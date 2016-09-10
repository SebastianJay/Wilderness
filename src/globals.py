"""
Contains variables that should be accessible from any scope
"""

#TODO make class method into properties so they can be accessed like Globals.isWindows
class Globals:
    def isWindows():
        pass

    def isMac():
        pass

    def isDev():
        return True

    def width():
        return 300

    def height():
        return 200
