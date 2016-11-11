"""
Definition for game display, which interacts with WindowManager to render
results to screen. The view in our MVC framework.
"""

import tkinter as tk
from global_vars import Globals

class Display:
    def __init__(self, root, windowManager):
        self.windowManager = windowManager
        self.numCols = Globals.NumCols
        self.numRows = Globals.NumRows
        self.root = root

        self.text = tk.Text(self.root, width=Globals.NumCols, height=Globals.NumRows, background='black',
            foreground='white', state=tk.DISABLED, font=(Globals.FontName, Globals.FontSize),
            padx=0, pady=0, borderwidth=0, selectbackground='black')
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

        start_index = 0
        for subformat in self.windowManager.formatting:   # subformat is one tuple: (string tag, (int start_index, int end_index))
            # account for additonal newlines when searching the bufferstr
            adjusted_format_start = subformat[1][0] + (subformat[1][0] // self.numCols)
            adjusted_format_end = subformat[1][1] + (subformat[1][1] // self.numCols)

            plain_text = bufferstr[start_index : adjusted_format_start]     # all the text between the last formatter and the start of this formatter
            formatted_text = bufferstr[adjusted_format_start : adjusted_format_end+1]   # all the text contained within this formatter

            formatter = subformat[0]
            formats = formatter.split('_')
            color = "white"
            font_style = (Globals.FontName, Globals.FontSize)
            for format_tag in formats:
                if format_tag == "bold":
                    font_style = (Globals.FontName, Globals.FontSize, "bold")
                elif format_tag == "italic":
                    font_style = (Globals.FontName, Globals.FontSize, "italic")
                elif format_tag == "underline":
                    font_style = (Globals.FontName, Globals.FontSize, "underline")
                else:
                    color = format_tag
                self.text.tag_config(formatter, foreground=color, font=font_style) # bold=is_bold, italic=is_italicized, underline=is_underlined
            self.text.insert(tk.END, plain_text)
            self.text.insert(tk.END, formatted_text, formatter)
            start_index = adjusted_format_end + 1   # start next search after this formatter

        if start_index < len(bufferstr):
            self.text.insert(tk.END, bufferstr[start_index:])
        self.text.config(state=tk.DISABLED)

    def getWidget(self):
        return self.text
