"""
Definition for input handler, which captures keystrokes.
"""

from tkinter import *

class InputHandler:
    def __init__(self):
        root = Tk()

        keys = list()

        def onKeyPressed(event):
            # Ignore non-printable characters
            # This does not capture Tab, BackSpace, Return, Escape
            if(event.char == ""):
                return

            if(event.keysym == "Escape"):
                for key in keys:
                    print(key)
                keys.clear()
                return

            if(event.keysym == "BackSpace"):
                keys.pop()
                return

            # keysym gives the actual key for special characters
            # eg Ctrl_L for Control
            # We're ignoring them right now (see above), but it could be useful
            # in the future.
            # Otherwise it should be identical to char.
            keys.append(event.keysym)

        frame = Frame(root, width=100, height=100)
        frame.bind("<Key>", onKeyPressed)
        frame.pack()
        frame.focus_set()

        print("Listening for keys...press Esc to list detected keys")

        root.mainloop()

test = InputHandler()
