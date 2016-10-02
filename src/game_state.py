#Definition of game state, which is the model in our MVC framework.

import json

class GameState:

    name = ""
    gender = ""
    location = ""
    id_number = 0;

    inventory = [] #should be a dictionary object
    status = []
    playtime = 0 #minutes

    def __init__(self): #more instance variables can be added and subtracted
        GameState = {
            {
                'name': "John",
                'gender': "Male",
                'location': "Home",
                'id_number': 0,

                'playtime': 50,
                'inventory': ["spoon", "trowel", "flashlight"],
                'status': "asleep",
            }
        }

        s = json.dumps(GameState)
        with open("C://User//GameState.txt", "w") as f: #write a different filepath
            f.write(s)
        pass

    def add(state): #may not be the correct syntax; depending on how the file is read, each individual "state"
                    #on someone's computer should have their own 'GameState object' that can be added to
        GameState.update(state)

        loads()
        pass

    def loads(): #when any instance is added to GameState, this method is called to create another saveFile
        with open ("C://User//GameState.txt") as json_data: #write  a different filepath
            save_data = json.loads(json_data)

        for individual_state in save_data['GameState']
            fo = open(individual_state['id'] + "_" + ['name'] + ".txt", "wb")

            for item in individual_state:
                fo.write(item + "           ")

            fo.close()

        pass
