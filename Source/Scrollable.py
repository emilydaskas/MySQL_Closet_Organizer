import tkinter as tk
from tkinter import *


# makes it scrollable
class Scrollable(tk.Frame):
    def __init__(self, frame, width = 40):
        scrollbar = Scrollbar(frame, width=width)
        scrollbar.pack(side=tk.RIGHT, fill= BOTH, expand=False)

        self.canvas = tk.Canvas(frame, yscrollcommand= scrollbar.set)
        self.canvas.pack(side=tk.RIGHT, fill=BOTH, expand=True)

        scrollbar.config(command=self.canvas.yview)

        self.canvas.bind('<Configure>', self.__fill_canvas)

        tk.Frame.__init__(self, frame)

        self.windows_item = self.canvas.create_window(0, 0, window=self, anchor=tk.NW)

    def __fill_canvas(self, event):
        canvas_width = event.widget.winfo_width()
        self.canvas.itemconfig(self.windows_item, width=canvas_width)

    def update(self):
        self.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox(self.windows_item))
