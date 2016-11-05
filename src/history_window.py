"""
Window containing the history/feedback of a player's actions. The content of
the game is exposed through this window.
"""
from window import Window
from game_state import GameState

class HistoryWindow(Window):

    def __init__(self, width, height):
        super().__init__(width, height)
        self.threshold = 0.05 # Delay in seconds before each character appears on-screen
        self.periodThreshold = self.threshold * 3 # Delay for periods
        self.timestep = 0.0 # Tracks the time since the last character was displayed
        self.currentChar = None # The current character
        self.charLimit = 1 # The current number of characters that can be displayed
        self.allWritten = True # True if everything has been displayed, false otherwise

    def update(self, timestep, keypresses):
        # Only increment charLimit when there's unrendered text still to be displayed
        # Otherwise, there will be no delay when the next batch of text is sent
        # since charLimit has been incrementing the whole time
        if self.allWritten == False:
            self.timestep += timestep
            if self.currentChar == '.':
                if self.timestep > self.periodThreshold:
                    self.timestep -= self.periodThreshold
                    self.charLimit += 1
            else:
                if self.timestep > self.threshold:
                    self.timestep -= self.threshold
                    self.charLimit += 1

    def draw(self):
        input_list = GameState().historyLines

        inputs = []
        #takes in all input and puts them all in a list of words
        if input_list:
            for a in input_list:
                for b in a.split():
                    inputs.append(b)
                inputs.append("\n")
            inputs.pop()    # correct for extra "\n" at end

        output_list = [[]]
        discarded = []
        line_count = 0
        current_count = 0
        # helper function for dropping to next line
        def incLine():
            nonlocal current_count
            nonlocal line_count
            nonlocal output_list
            current_count = 0
            line_count += 1
            output_list.append([])

        # go through word list and perform wrapping as necessary
        for b in inputs:
            if b == "\n":
                incLine()
            else:
                if current_count + len(b) > self.width:
                    incLine()
                current_count += len(b) + 1
                output_list[line_count].append(b)

        # take most recent lines that fit into window
        while len(output_list) > self.height:
            discarded.append(output_list.pop(0))

        # map output_list to self.pixels
        r = 0
        charsWritten = 0
        stopWriting = False     # flag that indicates if we hit charLimit
        for line_list in output_list:
            c = 0
            # fill in pixels with word content
            line = " ".join(line_list)
            for ch in line:
                self.pixels[r][c] = ch
                c += 1

                if charsWritten + c >= self.charLimit:
                    self.currentChar = ch
                    stopWriting = True
                    break

            # fill in what remains with spaces
            for cc in range(c, self.width):
                self.pixels[r][cc] = " "
            r += 1
            charsWritten += c
            if stopWriting:
                break

        # fill in blank lines
        for rr in range(r, self.height):
            for c in range(self.width):
                self.pixels[rr][c] = " "

        self.allWritten = not stopWriting
        return self.pixels

if __name__ == '__main__':
    h = HistoryWindow(30, 10)
    test_input = ["Hello, nice to meet you. I'm just trying to test out thise code",
    "So, this is supposed to cut the input and organize             them so it can fit into the given screen",
    "Do you think this is gonna work? 'Cause,,, I 'm not really sure myself.",
    "So.. I wonder how long this is now.."]
    # NOTE do not set historyLines directly in non-test code
    GameState().subStates[0].historyLines = test_input
    h.debugDraw()
