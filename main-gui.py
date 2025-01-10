import tkinter as tk
import pytmdl.utils as utils

from tkinter import ttk
from pytubefix import YouTube
from pytmdl.ytsong import YTSong, SongUnavailable
from pytmdl.ytalbum import YTAlbum, NotAnAlbum

dp = 10

def get_screen_center(window, w, h):
    sw = window.winfo_screenwidth()
    sh = window.winfo_screenheight()

    return ((sw / 2) - (w / 2), (sh /2) - (h / 2))

class AddWindow(tk.Tk):
    def __init__(self, window):
        super().__init__()
        self.window = window

        self.w = 350
        self.h = 200

        self.start_x = int(get_screen_center(self, self.w, self.h)[0])
        self.start_y = int(get_screen_center(self, self.w, self.h)[1])
        
        self.title("Add URL")
        self.geometry(f"{self.w}x{self.h}+{self.start_x}+{self.start_y}")
        self.minsize(self.w, self.h)
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.close)

    def close(self):
        self.window.deiconify()
        self.destroy()

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.w = 500
        self.h = 370

        self.start_x = int(get_screen_center(self, self.w, self.h)[0])
        self.start_y = int(get_screen_center(self, self.w, self.h)[1])

        self.title("PYTMDL")
        self.geometry(f"{self.w}x{self.h}+{self.start_x}+{self.start_y}")
        self.minsize(self.w, self.h)

        self.logo = ttk.Label(self, text="PYTMDL", font=("Arial Black", 20))
        self.download_btn = ttk.Button(self, text="Download")
        self.listbox = tk.Listbox(self)
        self.progress_current_label = ttk.Label(self, text="Current: N/A")
        self.progress_current = ttk.Progressbar(self)
        self.progress_all_label = ttk.Label(self,text="All: N/A")
        self.progress_all = ttk.Progressbar(self)
        self.add_button = ttk.Button(self, text="Add", command=self.show_add_window)
        self.remove_button = ttk.Button(self, text="Remove")
        self.add_from_file_button = ttk.Button(self, text="Add from file")
        self.remove_all_button = ttk.Button(self, text="Remove all")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.logo.grid(row=0, column=0, padx=dp, pady=dp, sticky="we")
        self.download_btn.grid(row=0, column=1, pady=dp/2, padx=dp/2, sticky="we")
        self.add_button.grid(row=2, column=1, pady=dp/2, padx=dp/2, sticky="nwe")
        self.remove_button.grid(row=3, column=1, pady=dp/2, padx=dp/2, sticky="nwe")
        self.add_from_file_button.grid(row=4, column=1, pady=dp/2, padx=dp/2, sticky="nwe")
        self.remove_all_button.grid(row=5, column=1, pady=dp/2, padx=dp/2, sticky="nwe")

        self.listbox.grid(row=1, column=0, padx=dp, pady=dp, rowspan=5, sticky="nswe")
        self.progress_current_label.grid(row=6, column=0, columnspan=2)
        self.progress_current.grid(row=7, column=0, padx=dp, pady=dp, columnspan=2, sticky="nswe")
        self.progress_all_label.grid(row=8, column=0, columnspan=2)
        self.progress_all.grid(row=9, column=0, padx=dp, pady=dp, columnspan=2, sticky="nswe")

    def show_add_window(self):
        self.add_window = AddWindow(self)
        self.add_window.deiconify()
        self.withdraw()

    def download_progress(self, stream, chunk, bytes_remaining):
        """
        Callback function to update the progress bar.

        Args:
            stream: The YouTube stream object.
            chunk: The current chunk being downloaded.
            bytes_remaining: The number of bytes remaining to be downloaded.
        """
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = (bytes_downloaded / total_size) * 100
        print(f"{percentage}%")

mw = MainWindow()
mw.mainloop()