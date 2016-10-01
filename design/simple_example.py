# -*- coding: utf-8 -*-
"""
Created on Wed Sep 28 15:57:48 2016

@author: Kwon
"""
import tkinter as tk

root = tk.Tk()                    # Create a background window object
                                # A simple way to create 2 lists
li     = [[0,1,0,1,0,1,0,1],[1,0,1,0,1,0,1,0],[0,1,0,1,0,1,0,1],[1,0,1,0,1,0,1,0],[0,1,0,1,0,1,0,1],[1,0,1,0,1,0,1,0],[0,1,0,1,0,1,0,1],[1,0,1,0,1,0,1,0]]
listb  = tk.Listbox(root)          # Create 2 listbox widgets

for item in li:              # Insert each item inside li into the listb
    listb.insert(END,item)

listb.pack()                    # Pack listbox into the main window
root.mainloop() 