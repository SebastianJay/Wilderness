"""
Definition for input handler, which captures keystrokes.
"""

from tkinter import *
from queue import Queue

class InputHandler:
    def __init__(self):
        root = Tk()

        queue = Queue()

        def onKeyPressed(event):
            # Ignore non-printable characters
            # This does not capture Tab, BackSpace, Return, Escape
            if event.char == "":
                return

            if event.keysym == "Escape" or event.keysym == "Return":
                while not queue.empty():
                    print(queue.get())
                return

            if event.keysym == "BackSpace":
                # TODO: Implement proper backspace support
                return

            # keysym gives the actual key for special characters
            # eg Ctrl_L for Control
            # We're ignoring them right now (see above), but it could be useful
            # in the future.
            # Otherwise it should be identical to char.
            queue.put(event.keysym)

        frame = Frame(root, width=100, height=100)
        frame.bind("<Key>", onKeyPressed)
        frame.pack()
        frame.focus_set()

        print("Listening for keys...press Esc or Enter to list detected keys")

        root.mainloop()

test = InputHandler()
