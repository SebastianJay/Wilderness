"""
Definition for game display, which interacts with WindowManager to render
results to screen. The view in our MVC framework.
"""

class Display:
    def __init__(self):
        pass

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
