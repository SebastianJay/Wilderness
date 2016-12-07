"""
Definition for game display, which interacts with WindowManager to render
results to screen. The view in our MVC framework.
"""

import tkinter as tk
import os
from global_vars import Globals

class Display:

    colorStringToHex = {
        'white':    '#ffffff',
        'black':    '#000000',
        'blue':     '#3030ff',
        'red':      '#ff3030',
        'green':    '#00ff00',
        'cyan':     '#00ffff',
        'yellow':   '#ffff00',
        'orange':   '#ffaa00',
        'pink':     '#ff7feb',
        'purple':   '#ff00ff',
        'brown':    '#8B4513',
    }

    def __init__(self, root, windowManager):
        self.windowManager = windowManager
        self.numCols = Globals.NumCols
        self.numRows = Globals.NumRows
        self.root = root

        # set title
        self.root.wm_title('Wilderness')
        # prevent resizing
        self.root.resizable(width=False, height=False)
        # set window icon
        if 'nt' in os.name:
            self.root.iconbitmap(Globals.IconFilePathWin)
        else:
            self.root.iconbitmap(Globals.IconFilePathUnix)
        # set window attributes
        self.root.configure(background='black', cursor='none')
        # create Text widget
        self.text = tk.Text(self.root, width=self.numCols, height=self.numRows, background='black',
            foreground='white', state=tk.DISABLED, font=(Globals.FontName, Globals.FontSize),
            padx=0, pady=0, borderwidth=0, selectbackground='black', cursor='none')
        self.text.pack(expand=True)

    def draw(self):
        # check for fullscreen change
        if self.windowManager.fullScreen != self.root.wm_attributes('-fullscreen'):
            self.root.wm_attributes('-fullscreen', self.windowManager.fullScreen)

        # aggregate text from pixels
        pixels = self.windowManager.draw()
        bufferlst = []
        for sublst in pixels:
            substr = ''.join(sublst)
            bufferlst.append(substr)
        bufferstr = '\n'.join(bufferlst)

        # set the plain text color to white with the right transparency
        alpha_level = self.windowManager.alphaLevel
        plain_color = '#{0:02X}{0:02X}{0:02X}'.format(max(255 - alpha_level * (256 // Globals.AlphaMax), 0))
        plain = 'plain'     # tags are identified by strings
        self.text.tag_config(plain, foreground=plain_color)

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
            # map readable string to hex color code
            hex_color = Display.colorStringToHex.get(color)
            if hex_color is None:
                hex_color = Display.colorStringToHex['white']
            # create transparency by pulling color to black
            color_ints = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
            color_ints = [max(ci - alpha_level * 256 // Globals.AlphaMax, 0) for ci in color_ints]
            hex_color = '#{:02X}{:02X}{:02X}'.format(*color_ints)
            self.text.tag_config(formatter, foreground=hex_color, font=font_style) # bold=is_bold, italic=is_italicized, underline=is_underlined
            self.text.insert(tk.END, plain_text, plain)
            self.text.insert(tk.END, formatted_text, formatter)
            start_index = adjusted_format_end + 1   # start next search after this formatter

        if start_index < len(bufferstr):
            self.text.insert(tk.END, bufferstr[start_index:], plain)
        self.text.config(state=tk.DISABLED)

    @property
    def widget(self):
        return self.text
