"""
Definition for window manager, which takes care of multiple Windows.
"""

class WindowManager:
    def __init__(screenWidth, screenHeight):
        self._screenWidth =  screenWidth #the width of the entire screen
        self._screenHeight = screenHeight #the height of the entire screen
        self._numOfWindows = 0 #number of windows in the windowList

        #this is a list of all the windows that the window manager is going to draw
        self._windowList = [Window(width, height) for x in range(0,numOfWindows)]

        #this is the full 2D-array of chars that contains all the content from all the windows.
        #this is what will display on the screen
        self._screen = [[' ' for x in range of(0, self._screenWidth)] for y in range of(0, self._screenHeight)]

    #This functions stitches together multiple windows into the screen
    def stitch():
        #traverse the window list and determine the order that the windows will be added to the screen
        #must figure out how we will find locations of individual windows
        #for x in range of (0, numOfWindows):

    def returnScreen():
        return self._screen


    def addWindow(window):
        #possible sorting of windows when adding them
        self._windowList.append(window)
        self._numOfWindows += 1

    """
	def border(self):
		"""
		Creates a border of asterisks around the window
		"""
		for i in range(0, self.width):
			self.pixels[0][i] = "*",
			self.pixels[self.height - 1][i] = "*"

		for i in range(1, self.height - 1):
			self.pixels[i][0] = "*"
			self.pixels[i][self.width - 1] = "*"
    """
