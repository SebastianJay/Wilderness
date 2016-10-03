"""
Definition for game display, which interacts with WindowManager to render
results to screen. The view in our MVC framework.
"""

import tkinter as tk
from global_vars import Globals

class Display:
    def __init__(self, root, windowManager):
        self.windowManager = windowManager
        self.xRes = Globals.XRes
        self.yRes = Globals.YRes
        self.numCols = Globals.NumCols
        self.numRows = Globals.NumRows
        self.root = root

        self.canvas = tk.Canvas(self.root, width=self.xRes, height=self.yRes, background='black')
        self.textIds = []
        for i in range(self.numRows):
            self.textIds.append([])
            for j in range(self.numCols):
                #TODO parameterize size of each char
                #TODO load custom font? seems difficult
                textId = self.canvas.create_text((j+1)*(Globals.FontSize-2) + Globals.XOffset,\
                    (i+1)*(Globals.FontSize-2) + Globals.YOffset,\
                    fill='white', font=('Courier New', Globals.FontSize))
                self.textIds[-1].append(textId)
        self.canvas.pack()

    def draw(self):
        pixels = self.windowManager.draw()
        for i in range(self.numRows):
            for j in range(self.numCols):
                self.canvas.itemconfig(self.textIds[i][j], text=pixels[i][j])

### Informal test for if print string / clear screen loop is fast enough on my shell
### Empirically it's too slow, so we will need to use something like tkinter instead
import subprocess as sp
def test():
    while True:
        pixels = [[' ' for x in range(150)] for y in range(50)]
        for y in range(len(pixels)):
            for x in range(len(pixels[0])):
                if x < y:
                    pixels[y][x] = '*'
                elif x > y:
                    pixels[y][x] = '^'
                else:
                    pixels[y][x] = '@'
        strcat = '\n'.join([''.join(row) for row in pixels])
        print(strcat)
        sp.call('cls', shell=True)
