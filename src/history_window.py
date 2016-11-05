"""
Window containing the history/feedback of a player's actions. The content of
the game is exposed through this window.
"""
from window import Window
from game_state import GameState

class HistoryWindow(Window):

    def __init__(self, width, height):
        super().__init__(width, height)
        self.threshold = 0.05   # Delay in seconds before each character appears on-screen
        self.periodThreshold = self.threshold * 3 # Delay for periods
        self.timestep = 0.0     # Tracks the time since the last character was displayed
        self.currentChar = None # The current character
        self.charLimit = 1      # The current number of characters that can be displayed
        self.allWritten = True  # True if everything has been displayed, false otherwise
        self.outputLength = 0
        self.startingLine = 0

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
        else: # Only allow scrolling if we're not writing text to the screen
            for key in keypresses:
                if key == "Prior":
                    if self.startingLine > 0:
                        self.startingLine -= 1
                elif key == "Next":
                    if self.startingLine + self.height < self.outputLength:
                        self.startingLine += 1
        for key in keypresses:
            if key == " ":
                self.charLimit = len(GameState().historyBuffer)
                self.allWritten = True
                self.timestep = 0.0

    def draw(self):
        #input_list = GameState().historyLines
        input_lines = GameState().historyBuffer
        input_list = input_lines.split("\n")
        input_formatting = GameState().historyFormatting

        inputs = []
        #takes in list of strings and puts them into list of tokens
        if input_list:
            for a in input_list:
                for b in a.split():
                    #if b != "":
                    inputs.append(b)
                    #else:
                    #    inputs.append("\n")
                inputs.append("\n")
            inputs.pop()    # correct for extra "\n" at end

        output_list = [[]]  # list of rows, where each row is a list of tokens
        row_indices = []    # list of (start, end) indices of historyBuffer corresponding to row
        current_count = 0   # number of characters on line so far
        total_count = 0     # number of characters from historyBuffer (include whitespace) written
        start_row_count = 0 # number of characters written by start of current line

        def incLine():
            nonlocal output_list, current_count, start_row_count, row_indices
            current_count = 0
            output_list.append([])
            row_indices.append((start_row_count, total_count-1))
            start_row_count = total_count

        # go through word list and perform wrapping as necessary
        for b in inputs:
            if b == "\n":
                incLine()
            else:
                if current_count + len(b) > self.width:
                    incLine()
                current_count += len(b) + 1
                total_count += len(b) + 1
                output_list[-1].append(b)
        row_indices.append((start_row_count, total_count))

        # take most recent lines that fit into window
        self.outputLength = len(output_list)
        if self.outputLength > self.height:
            if not self.allWritten:
                if self.startingLine != self.outputLength - self.height:
                    self.charLimit -= self.width
                self.startingLine = self.outputLength - self.height
            output_list = output_list[self.startingLine:self.startingLine + self.height]
            row_indices = row_indices[self.startingLine:self.startingLine + self.height]

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

        # map LangNode formatting to Window formatting
        # TODO super inefficient - refactor later
        output_formatting = []
        for style in input_formatting:
            for indices in input_formatting[style]:
                start_index = indices[0]
                end_index = indices[1]
                # see if (start_index, end_index) is contained within current view of history
                # clip indices if needed
                if start_index >= row_indices[0][0] and start_index <= row_indices[-1][1]:
                    if end_index > row_indices[-1][1]:
                        end_index = row_indices[-1][1]
                elif end_index >= row_indices[0][0] and end_index <= row_indices[-1][1]:
                    start_index = row_indices[0][0]
                else:
                    continue
                # scan through row_indices to find the rows where the style applies
                for ri1, row1 in enumerate(row_indices):
                    if start_index >= row1[0] and start_index <= row1[1]:
                        ci1 = start_index - row1[0]
                        for ri2, row2 in enumerate(row_indices[ri1:]):
                            if end_index >= row2[0] and end_index <= row2[1]:
                                ci2 = end_index - row2[0]
                                # the row and column values translate to window indices
                                fi1 = ri1 * self.width + ci1
                                fi2 = (ri1 + ri2) * self.width + ci2
                                output_formatting.append((style, (fi1, fi2)))
                                break
                        break

        self.formatting = output_formatting
        self.allWritten = not stopWriting
        return self.pixels

if __name__ == '__main__':
    h = HistoryWindow(30, 10)
    # NOTE do not set GameState values directly in non-test code
    #test_input = ["Hello, nice to meet you. I'm just trying to test out thise code",
    #"So, this is supposed to cut the input and organize             them so it can fit into the given screen",
    #"Do you think this is gonna work? 'Cause,,, I 'm not really sure myself.",
    #"So.. I wonder how long this is now.."]
    #GameState().subStates[0].historyLines = test_input

    test_input = "Kipp stepped back to take a good look at the room. He eyed a fancy bookself with some books that may be worth inspecting. In the far left corner of the room, Kipp also saw a sleeping bag. It may not be the right time to take a nap, but maybe he could use it to de-stress for a while. He looked back at Arthur. It looked like he hasn't gotten any better since we last talked. Maybe Kipp should go talk to Arthur again. \n  \n Kipp: Hmm...what should I do?"
    GameState().subStates[0].historyBuffer = test_input
    formatting = {'yellow': [(67, 74), (174, 185)],
        'green': [(302, 307), (404, 409)],
        'red': [(110, 119), (251, 253), (396, 402)],
    }
    GameState().subStates[0].historyFormatting = formatting
    h.debugDraw()
