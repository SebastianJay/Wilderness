"""
Definition of game state, which is the model in our MVC framework.
"""
import json

class GameState:

    def __init__(self):
        GameState = []
        GameState['user'] = {
            'name': 'user',
            'address': 'home',
            'gender': 'male'
        }

        s = json.dumps(GameState)
        with open("C://User//GameState.txt", "w") as f:
            f.write(s)


            pass
