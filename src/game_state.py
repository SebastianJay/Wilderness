"""
Definition of game state, which is the model in our MVC framework.
"""

from global_vars import Globals
import json
import os

class GameState:
    # Python singleton implementation adapted from
    # http://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html
    class __GameState:
        def __init__(self):
            self.name = ""
            self.gender = ""
            self.location = ""
            self.id_number = 0
            self.inventory = {}
            self.status = []
            self.playtime = 0 #minutes

        def dumps(self):
            """ Json stringifies the GameState """
            return json.dumps(self.__dict__)

        def loads(self, jsonstr):
            """ Initialize the GameState from a Json string """
            # "join" dct manually so omitted members of dct do not carry over
            dct = json.loads(jsonstr)
            for key in dct:
                # NOTE no copies made - dct should persist in memory
                setattr(self, key, dct[key])

        def writeFile(self, fpath):
            """ Write GameState to file """
            # create the directory to the save files if it does not exist
            fdir = os.path.dirname(fpath)
            if not os.path.exists(fdir):
                os.makedirs(fdir)
            with open(fpath, 'w') as f:
                f.write(self.dumps())

        def readFile(self, fpath):
            """ Load GameState from file """
            with open(fpath, 'r') as f:
                self.loads(f.read())

        def __str__(self):
            return self.dumps()

    instance = None
    def __new__(cls):
        if not GameState.instance:
            GameState.instance = GameState.__GameState()
        return GameState.instance
    def __getattr__(self, name):
        return getattr(self.instance, name)
    def __setattr__(self, name):
        return setattr(self.instance, name)

    """
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

    def add(state): #may not be the correct syntax; depending on how the file is read, each individual "state"
                    #on someone's computer should have their own 'GameState object' that can be added to
        GameState.update(state) # TODO resolve update()

        loads()

    def loads(): #when any instance is added to GameState, this method is called to create another saveFile
        with open ("C://User//GameState.txt") as json_data: #write  a different filepath
            save_data = json.loads(json_data)

        for individual_state in save_data['GameState']:
            fo = open(individual_state['id'] + "_" + ['name'] + ".txt", "wb")

            for item in individual_state:
                fo.write(item + "           ")

            fo.close()
    """

if __name__ == '__main__':
    g = GameState()
    g.name = 'testing'
    print(g)
    jsonstr = '{"gender": "??", "inventory": {"fork": 0}, "id_number": 5, \
        "name": "unknown", "status": [], "location": ""}'
    g.loads(jsonstr)
    print(g)

    g.writeFile(Globals.SavePaths[0])
    g.name = 'changed!'
    g.readFile(Globals.SavePaths[0])
    print(g)
