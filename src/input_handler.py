"""
Definition for input handler, which captures keystrokes.
"""

from queue import Queue
from global_vars import Globals

class InputHandler:
    def __init__(self, canvas):
        self.canvas = canvas
        self.queue = Queue()

        def onKeyPressed(event):
            # Debugging info about key event
            if Globals.IsDev:
                print("Key event: " + event.char + ", " + event.keysym)

            # Whitelist of metakeys (control keys) that are used in game
            metakeys = ['Up', 'Down', 'Left', 'Right',\
                'BackSpace', 'Escape', 'Prior', 'Next', 'Return']

            # Use char (raw printable character) by default, but prefer metakey name
            putchar = event.char
            if event.keysym in metakeys:
                putchar = event.keysym

            # Ignore any non-printable characters that are not whitelisted
            if putchar == "":
                return

            # Otherwise enqueue the char
            self.queue.put(putchar)

        self.canvas.bind("<Key>", onKeyPressed)
        self.canvas.focus_set()

    def getKeyPresses(self):
        keys = list()
        while not self.queue.empty():
            keys.append(self.queue.get())
        return keys

if __name__ == '__main__':
    import tkinter as tk
    from time import sleep
    import sys
    root = tk.Tk()
    canvas = tk.Canvas(root, width=100, height=100)
    canvas.pack()
    test = InputHandler(canvas)
    while True:
        try:
            root.update()
            print(test.getKeyPresses())
            sleep(0.5)
        except:
            sys.exit()
