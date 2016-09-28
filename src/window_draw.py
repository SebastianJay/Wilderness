
# def parse_input(self, list_of_string):
def draw(input_list):
    width = 30
    height = 5
    output_dict = {}
    output_list = []
    output_count = 0
    output_line_count = 0

    inputs = []

    #takes in all input and puts them all in a list of words
    for a in input_list:
        for b in a.split(" "):
            inputs.append(b)

    #put the input into the dictionary with line # as key, and length limited
    key = 0
    output_dict[key] = []
    current_count = 0
    for b in inputs:
        if current_count + len(b) > width:
            current_count = 0
            key += 1
            output_dict[key] = []
        current_count += len(b) + 1
        output_dict[key].append(b)

    #Check if it fits the screen height
    start = 0
    if key > height:
        for a in range(height):
            output_list.append(" ".join(output_dict[key-height + a+1]))
    else:
        for a in output_dict.keys():
            output_list.append(" ".join(output_dict[a]))

    for a in output_list:
        print(a)

draw(["Hello, nice to meet you. I'm just trying to test out thise code", "So, this is supposed to cut the input and organize them so it can fit into the given screen", "Do you think this is gonna work? 'Cause,,, I 'm not really sure myself.", "So.. I wonder how long this is now.."])
