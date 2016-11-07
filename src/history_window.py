"""
Window containing the history/feedback of a player's actions. The content of
the game is exposed through this window.
"""
from window import Window
from game_state import GameState

class HistoryWindow(Window):

    def __init__(self, width, height):
        super().__init__(width, height)
        self.threshold = 0.033  # Delay in seconds before each character appears on-screen
        self.periodThreshold = self.threshold * 5 # Delay for periods
        self.timestep = 0.0     # Tracks the time since the last character was displayed
        self.currentChar = None # The current character
        self.charLimit = 1      # The current number of characters that can be displayed
        self.allWritten = True  # True if everything has been displayed, false otherwise
        self.outputLength = 0
        self.startingLine = 0
        self.historyBufferWatch = 0 # keeps track of length of GameState history buffer
        self.charMax = 0        # total number of characters rendered to screen discounting animation, height limit

    def update(self, timestep, keypresses):
        # unrendered text exists if history buffer is larger than charLimit
        if len(GameState().historyBuffer) > self.historyBufferWatch:
            self.historyBufferWatch = len(GameState().historyBuffer)
            self.allWritten = False
        # Only increment charLimit when there's unrendered text still to be displayed
        # Otherwise, there will be no delay when the next batch of text is sent
        # since charLimit has been incrementing the whole time
        if self.allWritten == False:
            self.timestep += timestep
            if len(keypresses):
                for key in keypresses:
                    # Pressing space will speed up the animation
                    if key is ' ' and self.timestep > self.threshold / 3:
                        self.timestep -= self.threshold / 3
                        self.charLimit += 3
                        return

            if self.currentChar == '.':
                if self.timestep > self.periodThreshold:
                    self.timestep -= self.periodThreshold
                    self.charLimit += 1
            elif self.timestep > self.threshold:
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
        #print(self.allWritten, self.startingLine, self.charLimit, self.charMax)

    def draw(self):
        # TODO move line wrapping logic into update()
        #   this will keep the draw method short
        input_lines = GameState().historyBuffer
        input_list = input_lines.split("\n")
        input_formatting = GameState().historyFormatting

        if len(input_list) == 0:
            return self.pixels

        output_list = []    # list of row text - each row contains a string
        row_indices = []    # list of (start, end) indices of historyBuffer corresponding to row
        total_count = 0     # number of characters from historyBuffer (include whitespace) written
        start_row_count = 0 # number of characters written by start of current line

        # go through word list and perform wrapping as necessary
        # TODO refactor
        i = 0
        line_remaining = input_list[i]
        while i < len(input_list):
            if len(line_remaining) <= self.width:
                output_list.append(line_remaining)
                total_count += len(line_remaining) + 1
                i += 1
                if i >= len(input_list):
                    break
                line_remaining = input_list[i]
                row_indices.append((start_row_count, total_count-1))
                start_row_count = total_count
            else:
                space_ind = line_remaining.rfind(' ', 0, self.width)
                output_list.append(line_remaining[:space_ind])
                total_count += len(line_remaining[:space_ind]) + 1
                line_remaining = line_remaining[space_ind+1:]
                row_indices.append((start_row_count, total_count-1))
                start_row_count = total_count
        row_indices.append((start_row_count, total_count-1))

        # take most recent lines that fit into window
        self.outputLength = len(output_list)
        # reset charMax to be sum of all line lengths
        self.charMax = 0
        for line in output_list:
            self.charMax += len(line)
        # charsWritten is current count of characters rendered to screen
        charsWritten = 0
        if self.outputLength > self.height:
            # if in animating mode, choose the starting line based on which line is animating
            if not self.allWritten:
                current_line = 0
                char_counter = 0
                while current_line < len(output_list) and char_counter < self.charLimit:
                    char_counter += len(output_list[current_line])
                    current_line += 1
                self.startingLine = current_line - self.height if current_line - self.height >= 0 else 0
            # include lines above window in charsWritten count
            charsWritten = 0
            for prevRow in output_list[:self.startingLine]:
                charsWritten += len(prevRow)
            # find the right window
            output_list = output_list[self.startingLine:self.startingLine + self.height]
            row_indices = row_indices[self.startingLine:self.startingLine + self.height]

        # map output_list to self.pixels
        r = 0
        stopWriting = False     # flag that indicates if we hit charLimit
        for line in output_list:
            c = 0
            # fill in pixels with word content
            for ch in line:
                self.pixels[r][c] = ch
                c += 1
                charsWritten += 1

                if charsWritten >= self.charLimit:
                    self.currentChar = ch
                    stopWriting = True
                    break

            # fill in what remains with spaces
            for cc in range(c, self.width):
                self.pixels[r][cc] = " "
            r += 1
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
    test_input = "Kipp stepped back to take a good look at the room. He eyed a fancy bookself with some books that may be worth inspecting. In the far left corner of the room, Kipp also saw a sleeping bag. It may not be the right time to take a nap, but maybe he could use it to de-stress for a while. He looked back at Arthur. It looked like he hasn't gotten any better since we last talked. Maybe Kipp should go talk to Arthur again. \n  \n Kipp: Hmm...what should I do?"
    GameState().subStates[0].historyBuffer = test_input
    formatting = {'yellow': [(67, 74), (174, 185)],
        'green': [(302, 307), (404, 409)],
        'red': [(110, 119), (251, 253), (396, 402)],
    }
    GameState().subStates[0].historyFormatting = formatting
    h.debugDraw()
