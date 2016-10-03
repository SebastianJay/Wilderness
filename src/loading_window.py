import window
import time


class loading_window(window):

    def __init__(self, w, h, updateDelay, border):

        self.width = w
        self.height = h
        self.windowChars = []
        self.continueAnimating = True
        self.delay = updateDelay
        self.border = border

        self.animStateOne = [["L", [self.width // 2 - 5, self.height // 2]], ["o", [self.width // 2 - 4, self.height // 2]],
                             ["a", [self.width // 2 - 3, self.height // 2]], ["d", [self.width // 2 - 2, self.height // 2]],
                             ["i", [self.width // 2 - 1, self.height // 2]], ["n", [self.width // 2, self.height // 2]],
                             ["g", [self.width // 2 + 1, self.height // 2]], [".", [self.width // 2 + 2, self.height // 2]],
                             [" ", [self.width // 2 + 3, self.height // 2]], [" ", [self.width // 2 + 4, self.height // 2]], ]
        self.animStateTwo = [["L", [self.width // 2 - 5, self.height // 2]], ["o", [self.width // 2 - 4, self.height // 2]],
                             ["a", [self.width // 2 - 3, self.height // 2]], ["d", [self.width // 2 - 2, self.height // 2]],
                             ["i", [self.width // 2 - 1, self.height // 2]], ["n", [self.width // 2, self.height // 2]],
                             ["g", [self.width // 2 + 1, self.height // 2]], [".", [self.width // 2 + 2, self.height // 2]],
                             [".", [self.width // 2 + 3, self.height // 2]], [" ", [self.width // 2 + 4, self.height // 2]], ]
        self.animStateThree = [["L", [self.width // 2 - 5, self.height // 2]], ["o", [self.width // 2 - 4, self.height // 2]],
                               ["a", [self.width // 2 - 3, self.height // 2]], ["d", [self.width // 2 - 2, self.height // 2]],
                               ["i", [self.width // 2 - 1, self.height // 2]], ["n", [self.width // 2, self.height // 2]],
                               ["g", [self.width // 2 + 1, self.height // 2]], [".", [self.width // 2 + 2, self.height // 2]],
                               [".", [self.width // 2 + 3, self.height // 2]], [".", [self.width // 2 + 4, self.height // 2]], ]

        for i in range(0, self.height):
            self.windowChars.append([])

            for j in range(0, self.width):
                self.windowChars[i].append(" ")

        if self.border:
            for i in range(0, self.width):
                self.windowChars[0][i], self.windowChars[self.height - 1][i] = "*", "*"

            for i in range(1, self.height - 1):
                self.windowChars[i][0], self.windowChars[i][self.width - 1] = "*", "*"



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


    def update(self, listOfUpdates):
        """
        listOfUpdates to be in form [ [charcter, [self.widthOfChar, self.heightOfChar]], ...]
        delay to be in milliseconds
        """
        time.sleep(self.delay / 1000)
        for i in listOfUpdates:
            self.windowChars[int(i[1][1])][int(i[1][0])] = i[0]
        self.draw()

    def animate(self):

        while self.continueAnimating:
            self.update(self.animStateOne)
            self.update(self.animStateTwo)
            self.update(self.animStateThree)

    def stopAnimating(self):

        self.continueAnimating = False


	
