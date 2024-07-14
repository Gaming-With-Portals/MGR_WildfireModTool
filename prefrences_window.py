import windows
import tkinter
import customtkinter
import platform
import pyglet
import os
import pyglet
from tkinterdnd2 import DND_FILES
from tkinter import ttk
import time
from PIL import ImageTk
from tkinter import filedialog
from CTkMenuBar import *
# Import custom libraries
from lib_py import MGR
from lib_py import BinaryLib
from lib_py import Configlib


pyglet.options['win32_gdi_font'] = True
DARK_MODE = "dark"
customtkinter.set_appearance_mode(DARK_MODE)
customtkinter.set_default_color_theme("blue")




class App(customtkinter.CTk):

    frames = {}
    current = None
    bg = ""
    

    def __init__(self):
        
        self.res = "400x600"
        self.cfglibrary = Configlib.ConfigLibrary("bin\\wildfire.cfg")
        try:
            pyglet.font.add_file(self.cfglibrary.find_value("title_font_path"))
            pyglet.font.add_file(self.cfglibrary.find_value("light_font_path"))
            self.light_font = self.cfglibrary.find_value("light_font")
            self.title_font = self.cfglibrary.find_value("title_font")
        except:
            windows.MsgBox("Critical font loading error.\nCheck bin/wildfire.cfg and ensure fonts exist.", windows.MB_OK | windows.MB_ICONERROR, "Wildfire Mod Tool")
            quit()
        
        
        super().__init__()      
        self.bg = self.cget("fg_color")
        # self.state('withdraw')
        self.title("Wildfire Mod Tool | Preferences")
        
        
        # screen size
        self.geometry(self.res)

        self.languages = []
        for file in os.listdir("bin\\lang\\"):
            lang_cfg = Configlib.ConfigLibrary("bin\\lang\\" + file)
            self.languages.append(lang_cfg.find_value("name"))    
        
        self.themes = []
        for file in os.listdir("bin\\theme\\"):
            lang_cfg = Configlib.ConfigLibrary("bin\\theme\\" + file + "\\theme.ini")
            self.themes.append(lang_cfg.find_value("name")) 

        # root!
        main_container = customtkinter.CTkFrame(self, corner_radius=8, fg_color=self.bg)
        main_container.pack(fill=tkinter.BOTH, expand=True, padx=8, pady=8)

        # right side panel -> to show the frame1 or frame 2, or ... frame + n where n <= 5
        self.right_side_panel = customtkinter.CTkFrame(main_container, corner_radius=8, fg_color="#212121")
        self.right_side_panel.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True, padx=0, pady=0)
        self.right_side_panel.configure(border_width = 1)
        self.right_side_panel.configure(border_color = "#323232")

        self.title = customtkinter.CTkLabel(self.right_side_panel, text="Preferences", font=(self.title_font, 35))
        self.title.pack(side=tkinter.TOP, fill=tkinter.X, expand=False, padx=5, pady=5)

        # LANGUAGE
        self.lang_text = customtkinter.CTkLabel(self.right_side_panel, text="Language", font=(self.light_font, 20))
        self.lang_text.pack(side=tkinter.TOP, fill=tkinter.X, expand=False, padx=5, pady=5)
        self.lang_picker = customtkinter.CTkComboBox(self.right_side_panel, corner_radius=5, values=self.languages, font=(self.light_font, 15))
        self.lang_picker.pack(side=tkinter.TOP, fill=tkinter.X, expand=False, padx=5, pady=5)
        
        # THEME
        self.theme_text = customtkinter.CTkLabel(self.right_side_panel, text="Theme", font=(self.light_font, 20))
        self.theme_text.pack(side=tkinter.TOP, fill=tkinter.X, expand=False, padx=5, pady=5)
        self.theme_picker = customtkinter.CTkComboBox(self.right_side_panel, corner_radius=5, values=self.themes, font=(self.light_font, 15))
        self.theme_picker.pack(side=tkinter.TOP, fill=tkinter.X, expand=False, padx=5, pady=5)     
        



def create_window():
    pre = App()
    pre.mainloop()

        

