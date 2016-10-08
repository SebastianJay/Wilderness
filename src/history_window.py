"""
Window containing the history/feedback of a player's actions. The content of
the game is exposed through this window.
"""
from window import Window
from game_state import GameState

class HistoryWindow(Window):

    def __init__(self, width, height):
        super().__init__(width, height)

    def update(self, timestep, keypresses):
        pass

    def draw(self):
        input_list = GameState().historyLines

        inputs = []
        #takes in all input and puts them all in a list of words
        if input_list:
            for a in input_list:
                for b in a.split(" "):
                    inputs.append(b)
                inputs.append("\n")
            inputs.pop()    # correct for extra "\n" at end

        output_list = [[]]
        discarded = []
        output_count = 0
        output_line_count = 0
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
            elif b.strip() != "":
                if current_count + len(b) > self.width:
                    incLine()
                current_count += len(b) + 1
                output_list[line_count].append(b)

        # take most recent lines that fit into window
        while len(output_list) > self.height:
            discarded.append(output_list.pop(0))

        # map output_list to self.pixels
        r = 0
        for line_list in output_list:
            c = 0
            # fill in pixels with word content
            for wi, word in enumerate(line_list):
                for ch in word:
                    self.pixels[r][c] = ch
                    c += 1
                if wi < len(line_list) - 1:
                    self.pixels[r][c] = " "
                    c += 1
            # fill in what remains with spaces
            for cc in range(c, self.width):
                self.pixels[r][cc] = " "
            r += 1
        # fill in blank lines
        for rr in range(r, self.height):
            for c in range(self.width):
                self.pixels[rr][c] = " "
        return self.pixels

if __name__ == '__main__':
    h = HistoryWindow(30, 10)
    test_input = ["Hello, nice to meet you. I'm just trying to test out thise code", "So, this is supposed to cut the input and organize             them so it can fit into the given screen", "Do you think this is gonna work? 'Cause,,, I 'm not really sure myself.", "So.. I wonder how long this is now.."]
    # NOTE do not set historyLines directly in non-test code
    GameState().historyLines = test_input
    h.debugDraw()
