"""
Definition for game display, which interacts with WindowManager to render
results to screen. The view in our MVC framework.
"""

import tkinter as tk
from global_vars import Globals

class Display:
    def __init__(self, root, windowManager):
        self.windowManager = windowManager
        self.xRes = Globals.NumCols
        self.yRes = Globals.NumRows
        self.numCols = Globals.NumCols
        self.numRows = Globals.NumRows
        self.root = root

        self.text = tk.Text(self.root, width=self.xRes, height=self.yRes, background='black',
            foreground='white', state=tk.DISABLED, font=(Globals.FontName, Globals.FontSize),
            padx=0, pady=0, bd=0, selectbackground='black')
        self.text.pack()

    def draw(self):
        pixels = self.windowManager.draw()
        bufferlst = []
        for sublst in pixels:
            substr = ''.join(sublst)
            bufferlst.append(substr)
        bufferstr = '\n'.join(bufferlst)
        self.text.config(state=tk.NORMAL)
        self.text.delete(1.0, tk.END)
        self.text.insert(tk.END, bufferstr)
        self.text.config(state=tk.DISABLED)

    def getWidget(self):
        return self.text
