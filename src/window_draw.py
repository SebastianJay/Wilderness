
# def parse_input(self, list_of_string):
def draw(list_of_string): 
    number_of_lines = 0
    temp = {}
    for item in list_of_string:
        count = 0
        space_index = 0
        char_since_space = 0
        temp[number_of_lines] = []
        for character in item:
#            if(count > self._width):
            if(count > 30):
                number_of_lines += 1
                temp[number_of_lines] = []
                count = 0
                check = temp[number_of_lines-1].pop()
                if(check != ' ' and character != ' '):
                    for i in range(1, char_since_space):
                        move = temp[number_of_lines-1][30-char_since_space + i]
                        if(move != ' '):
                            temp[number_of_lines].append(move)
                            count += 1
                    if(check != ' ' ):
                        temp[number_of_lines].append(check)
                        count +=1
                    for i in range(1, char_since_space):
                        temp[number_of_lines-1].pop()
                    for i in range(1, char_since_space):
                        temp[number_of_lines-1].append("_")
            if(character == ' '):
                space_index = count
                char_since_space = 0
            temp[number_of_lines].append(character)
            count += 1
            char_since_space += 1
        number_of_lines += 1
    return temp
    

temp = parse_input(["Hey, This is a Line! Surprise!!!!!! Is this more than 30 letters yet?","This is another line. hopefully less than 30 letters"])
for a in temp.keys():
        for b in temp[a]:
            print(b, end='')
        print()