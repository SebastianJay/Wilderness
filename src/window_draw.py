
# def parse_input(self, list_of_string):
def draw(input_list):
    width = 30
    height = 5
    output_list = [[]]
    output_count = 0
    output_line_count = 0

    inputs = []

    #takes in all input and puts them all in a list of words
    for a in input_list:
        for b in a.split(" "):
            inputs.append(b)

    line_count = 0
    current_count = 0
    for b in inputs:
        if b.strip() != "":
            if current_count + len(b) > width:
                current_count = 0
                line_count += 1
                output_list.append([])
            current_count += len(b) + 1
            output_list[line_count].append(b)

    for a in output_list:
        a = list(" ".join(a))
        print(a)

draw(["Hello, nice to meet you. I'm just trying to test out thise code", "So, this is supposed to cut the input and organize             them so it can fit into the given screen", "Do you think this is gonna work? 'Cause,,, I 'm not really sure myself.", "So.. I wonder how long this is now.."])
