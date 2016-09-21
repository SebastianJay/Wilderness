"""
Definition for input handler, which captures keystrokes.
"""

from tkinter import *


class InputHandler:
    def __init__(self):
        root = Tk()

        def onKeyPressed(event):
            if event.keysym.startswith("Shift"):  # Shift_L, Shift_R
                print("hoho!")
                return

            print("{} was pressed".format(event.keysym))

        frame = Frame(root, width=100, height=100)
        frame.bind("<Key>", onKeyPressed)
        frame.pack()
        frame.focus_set()

        root.mainloop()

test = InputHandler()
