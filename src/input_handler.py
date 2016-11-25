"""
Definition for input handler, which captures keystrokes.
"""

from queue import Queue
from global_vars import Globals
from string import printable

class InputHandler:
    def __init__(self, widget):
        self.widget = widget
        self.queue = Queue()

        def onKeyPressed(event):
            # Debugging info about key event
            if Globals.IsDev:
                print("Key event:", event.char, event.keysym)

            # Whitelist of metakeys (control keys) that are used in game
            metakeys = ['Up', 'Down', 'Left', 'Right', 'Tab', 'F11', \
                'BackSpace', 'Escape', 'Prior', 'Next', 'Return']

            # Use char (raw printable character) by default, but prefer metakey name
            putchar = event.char
            if event.keysym in metakeys:
                putchar = event.keysym

            # Ignore any non-printable characters that are not whitelisted
            if len(putchar) == 0 or (len(putchar) == 1 and putchar not in printable):
                return

            # Otherwise enqueue the char
            self.queue.put(putchar)

        self.widget.bind("<Key>", onKeyPressed)
        self.widget.focus_set()

    def getKeyPresses(self):
        keys = []
        while not self.queue.empty():
            key = self.queue.get()
            keys.append(key)
            # throttle input by stalling keystrokes after Return until next update
            if key == 'Return':
                break
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
