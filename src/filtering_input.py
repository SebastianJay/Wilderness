# Siddharth Ghatti(#sg4ff)

def filtering():
    test_list=["python","Gabe","Newell","Bruce","Wayne","pluto","Geb","panther","Jupiter"]
    display_list=[]
    user_input=input("Command:")
    j=range(0,len(test_list))
    for j in range(0,len(test_list)):
        if user_input[0]==test_list[j][0] and user_input[1]==test_list[j][1]:
            display_list.append(test_list[j])
    print(display_list)
filtering()