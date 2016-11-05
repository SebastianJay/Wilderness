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

        # formatting = self.windowManager._formatting
        # _formatting: [(string tag, (int start_index, int end_index)), (... )]
        # bold, italics, underline, and text color

        for sublst in pixels:
            substr = ''.join(sublst)
            bufferlst.append(substr)
        bufferstr = '\n'.join(bufferlst)

        self.text.config(state=tk.NORMAL)
        self.text.delete(1.0, tk.END)

        start_index = 0
        for subformat in self.windowManager._formatting:   # subformat is one tuple: (string tag, (int start_index, int end_index))
            plain_text = bufferstr[start_index:subformat[1][0]]     # all the text between the last formatter and the start of this formatter
            formatted_text = bufferstr[subformat[1][0]:(subformat[1][1]+1)]   # all the text contained within this formatter

            formatter = subformat[0]
            is_bold = 0
            is_italicized = 0
            is_underlined = 0
            formats = formatter.split('_')
            color = "white"
            font_style = (Globals.FontName, Globals.FontSize)
            for format in formats:

                if format == "bold":
                    font_style = (Globals.FontName, Globals.FontSize, "bold")
                elif format == "italic":
                    font_style = (Globals.FontName, Globals.FontSize, "italic")
                elif format == "underline":
                    font_style = (Globals.FontName, Globals.FontSize, "underline")
                else:
                    color = format
                self.text.tag_config(formatter, foreground=color, font=font_style) # bold=is_bold, italic=is_italicized, underline=is_underlined
            self.text.insert(tk.END, plain_text)
            self.text.insert(tk.END, formatted_text, formatter)
            start_index = subformat[1][1] + 1   # start next search after this formatter

        if start_index < len(bufferstr):
            self.text.insert(tk.END, bufferstr[start_index:])
        self.text.config(state=tk.DISABLED)

    def getWidget(self):
        return self.text
