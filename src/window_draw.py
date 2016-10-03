class windows:
    width = 30
    height = 10

    # if Output_by_Char is True, the list is split into chars.
    def draw(self, input_list, output_by_char):
        output_list = [[]]
        output_count = 0
        output_line_count = 0
        inputs = []
        discarded = []
        #takes in all input and puts them all in a list of words
        for a in input_list:
            for b in a.split(" "):
                inputs.append(b)

        line_count = 0
        current_count = 0
        for b in inputs:
            if b.strip() != "":
                if current_count + len(b) > self.width:
                    current_count = 0
                    line_count += 1
                    output_list.append([])
                current_count += len(b) + 1
                output_list[line_count].append(b)

        if len(output_list) > self.height:
            while len(output_list) > self.height:
                discarded.append(output_list.pop(0))
        for a in output_list:
            if(output_by_char):
                a = list(" ".join(a))
            print(a)

def main():
    tester = windows()
    test = True
    test_input = ["Hello, nice to meet you. I'm just trying to test out thise code", "So, this is supposed to cut the input and organize             them so it can fit into the given screen", "Do you think this is gonna work? 'Cause,,, I 'm not really sure myself.", "So.. I wonder how long this is now.."]
    tester.draw(test_input, not test)
if __name__ == "__main__":
    main()
