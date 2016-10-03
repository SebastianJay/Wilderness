import window
import time

class loading_window(window):
    def __init__(self, w, h):

        self.width = w
        self.height = h
        self.windowChars = []

        for i in range(0, self.height):
            self.windowChars.append([])

            for j in range(0, self.width):
                self.windowChars[i].append(" ")

    def border(self):
        """
        Creates a border of asterisks around the window
        """
        for i in range(0, self.width):
            self.windowChars[0][i], self.windowChars[self.height - 1][i] = "*", "*"

        for i in range(1, self.height - 1):
            self.windowChars[i][0], self.windowChars[i][self.width - 1] = "*", "*"

    def draw(self):
        """
        Displays the windowChars matrix using print()
        """
        for i in range(0, self.height):
            if not i == 0: print()
            for j in range(0, self.width):
                print(self.windowChars[i][j], end="")
        print()

    def update(self, listOfUpdates, delay):
        """
        listOfUpdates to be in form [ [charcter, [widthOfChar, heightOfChar]], ...]
        delay to be in milliseconds
        """
        time.sleep(delay/1000)
        for i in listOfUpdates:
            self.windowChars[int(i[1][1])][int(i[1][0])] = i[0]
        self.draw()

"""
The below code is suggestion/example to demonstrate how to use the methods to
create a good looking loading box, and shows what it would look like
"""

width = 51
height = 11

loadingWindow = loading_window(width,height)
loadingWindow.border()

animStateOne = [["L", [width//2-5,height//2]], ["o", [width//2-4,height//2]], ["a", [width//2-3,height//2]], ["d", [width//2-2,height//2]], ["i", [width//2-1,height//2]], ["n", [width//2,height//2]], ["g", [width//2+1,height//2]], [".", [width//2+2,height//2]], [" ", [width//2+3,height//2]], [" ", [width//2+4,height//2]], ]
animStateTwo =[["L", [width//2-5,height//2]], ["o", [width//2-4,height//2]], ["a", [width//2-3,height//2]], ["d", [width//2-2,height//2]], ["i", [width//2-1,height//2]], ["n", [width//2,height//2]], ["g", [width//2+1,height//2]], [".", [width//2+2,height//2]], [".", [width//2+3,height//2]], [" ", [width//2+4,height//2]], ]
animStateThree = [["L", [width//2-5,height//2]], ["o", [width//2-4,height//2]], ["a", [width//2-3,height//2]], ["d", [width//2-2,height//2]], ["i", [width//2-1,height//2]], ["n", [width//2,height//2]], ["g", [width//2+1,height//2]], [".", [width//2+2,height//2]], [".", [width//2+3,height//2]], [".", [width//2+4,height//2]], ]

for i in range(1, 30):
    loadingWindow.update(animStateOne, 500)
    loadingWindow.update(animStateTwo, 500)
    loadingWindow.update(animStateThree, 500)
