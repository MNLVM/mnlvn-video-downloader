from tkinter.filedialog import askopenfilenames
import tkinter as tk
from customtkinter import CTkEntry


def open_many_file():
    filetypes = (("csv files", "*.csv"), ("All files", "*.csv"))
    file_path = askopenfilenames(title="ouvrir un fichier", filetypes=filetypes)
    return " ; ".join(file_path), list(file_path)


def set_path_file(input: CTkEntry):
    path, _ = open_many_file()
    if input:
        if input.get() != "":
            input.delete(0, tk.END)
        input.insert(0, str(path))
