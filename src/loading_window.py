from window import Window
from time import *


class LoadingWindow(window):

    def __init__(self, w, h, border):

        self.width = w
        self.height = h
        self.windowChars = []
        self.border = border
		self.animState = 1

        self.animStateOne = [("L", (self.width // 2 - 5, self.height // 2)),
                             ("o", (self.width // 2 - 4, self.height // 2)),
                             ("a", (self.width // 2 - 3, self.height // 2)),
                             ("d", (self.width // 2 - 2, self.height // 2)),
                             ("i", (self.width // 2 - 1, self.height // 2)), 
							 ("n", (self.width // 2, self.height // 2)),
                             ("g", (self.width // 2 + 1, self.height // 2)),
                             (".", (self.width // 2 + 2, self.height // 2)),
                             (" ", (self.width // 2 + 3, self.height // 2)),
                             (" ", (self.width // 2 + 4, self.height // 2))]
        self.animStateTwo = [("L", (self.width // 2 - 5, self.height // 2)),
                             ("o", (self.width // 2 - 4, self.height // 2)),
                             ("a", (self.width // 2 - 3, self.height // 2)),
                             ("d", (self.width // 2 - 2, self.height // 2)),
                             ("i", (self.width // 2 - 1, self.height // 2)), 
							 ("n", (self.width // 2, self.height // 2)),
                             ("g", (self.width // 2 + 1, self.height // 2)),
                             (".", (self.width // 2 + 2, self.height // 2)),
                             (".", (self.width // 2 + 3, self.height // 2)),
                             (" ", (self.width // 2 + 4, self.height // 2))]
        self.animStateThree = [("L", (self.width // 2 - 5, self.height // 2)),
                               ("o", (self.width // 2 - 4, self.height // 2)),
                               ("a", (self.width // 2 - 3, self.height // 2)),
                               ("d", (self.width // 2 - 2, self.height // 2)),
                               ("i", (self.width // 2 - 1, self.height // 2)),
                               ("n", (self.width // 2, self.height // 2)),
                               ("g", (self.width // 2 + 1, self.height // 2)),
                               (".", (self.width // 2 + 2, self.height // 2)),
                               (".", (self.width // 2 + 3, self.height // 2)),
                               (".", (self.width // 2 + 4, self.height // 2))]

        for i in range(self.height):
            self.windowChars.append([])

            for j in range(self.width):
                self.windowChars[i].append(" ")

        if self.border:
            for i in range(self.width):
                self.windowChars[0][i], self.windowChars[self.height - 1][i] = "*", "*"

            for i in range(1, self.height - 1):
                self.windowChars[i][0], self.windowChars[i][self.width - 1] = "*", "*"



    def border(self):
        """
        Creates a border of asterisks around the window
        """
        for i in range(0, self.width):
            self.windowChars[0][i] = "*",
			self.windowChars[self.height - 1][i] = "*"

        for i in range(1, self.height - 1):
            self.windowChars[i][0] = "*"
			self.windowChars[i][self.width - 1] = "*"


    def draw(self):
        """
        Displays the windowChars matrix using print()
        """
        for i in range(0, self.height):
            if not i == 0: print()
            for j in range(0, self.width):
                print(self.windowChars[i][j], end="")
        print()


    def update(self):
        """
		Updates loading window
		"""
		if self.animState == 1:
        	for i in animStateOne:
            	self.windowChars[int(i[1][1])][int(i[1][0])] = i[0]
			animState = 2
		elif self.animState == 2:
			for i in animStateTwo:
            	self.windowChars[int(i[1][1])][int(i[1][0])] = i[0]
			animState = 3	
		else:
			for i in animStateThree:
            	self.windowChars[int(i[1][1])][int(i[1][0])] = i[0]
			animState = 1


	
