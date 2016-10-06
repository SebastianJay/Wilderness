"""
Definition for input handler, which captures keystrokes.
"""

from tkinter import *
from queue import Queue
import sys

class InputHandler:
    def __init__(self):
        root = Tk()

        self.queue = Queue()

        def onKeyPressed(event):
            # Ignore non-printable characters
            # This does not capture Tab, BackSpace, Return, Escape
            if event.char == "":
                return

            if event.keysym == "Escape":
                sys.exit()

            # TODO: Remove this once a proper consumer is implemented
            if event.keysym == "Return":
                for key in self.getKeyPresses():
                    print(key)
                return

            if event.keysym == "BackSpace":
                # TODO: Implement proper backspace support
                return

            # keysym gives the actual key for special characters
            # eg Ctrl_L for Control
            # We're ignoring them right now (see above), but it could be useful
            # in the future.
            # Otherwise it should be identical to char.
            self.queue.put(event.keysym)

        frame = Frame(root, width=100, height=100)
        frame.bind("<Key>", onKeyPressed)
        frame.pack()
        frame.focus_set()

        print("Listening for keys...Enter to list detected keys or Esc to exit")

        root.mainloop()

    def getKeyPresses(self):
        keys = list()

        while not self.queue.empty():
            keys.append(self.queue.get())
        return keys

test = InputHandler()
