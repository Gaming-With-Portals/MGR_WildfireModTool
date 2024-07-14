import windows
import tkinter
import customtkinter
import platform
import pyglet
import os, sys
import pyglet
from tkinterdnd2 import DND_FILES
from tkinter import ttk
import time
from PIL import ImageTk
from tkinter import filedialog
from plyer import notification
from CTkMenuBar import *
# Import custom libraries
from lib_py import MGR
from lib_py import BinaryLib
from lib_py import Configlib
import prefrences_window

pyglet.options['win32_gdi_font'] = True
DARK_MODE = "dark"
customtkinter.set_appearance_mode(DARK_MODE)
customtkinter.set_default_color_theme("blue")


is_console_mode = False

class spoof_event:
    def __init__(self, data):
        self.data = data


class App(customtkinter.CTk):

    frames = {}
    current = None
    bg = ""
    
    APP_VERSION = "0.1 PREVIEW" # TODO CHANGE THIS EVERY VERSION!!
    
    FRAME_ID_WITH_BORDER = [0, 1, 3]
    VALID_CONTAINER_FILES = []

    def __init__(self):
        if not os.path.exists(os.getenv('LOCALAPPDATA') + "/GWPWildfire/user.cfg"):
            print("Run first time setup")
            windows.MsgBox("Welcome to Wildfire Mod Tool!\nIt appears this is your first time, please preform the setup.", windows.MB_OK | windows.MB_ICONINFORMATION, "Wildfire Mod Tool")
            windows.MsgBox("On the next page, you will be asked to selected your 'METAL GEAR RISING REVENGENCE.EXE'.", windows.MB_OK | windows.MB_ICONINFORMATION, "Wildfire Mod Tool")
            while True:
                rev_exe_path = filedialog.askopenfilename(title = "Select MGR:R EXE", filetypes=[("MGR:R","*.exe")])
                print(os.path.basename(rev_exe_path))
                if os.path.basename(rev_exe_path) == "METAL GEAR RISING REVENGEANCE.exe":
                    print("Valid!")
                    break
                else:
                    windows.MsgBox("Invalid. File name must be METAL GEAR RISING REVENGEANCE.exe", windows.MB_OK | windows.MB_ICONERROR, "Wildfire Mod Tool")
            print("Creating user configuration files")
            try:
                os.mkdir(os.getenv('LOCALAPPDATA') + "/GWPWildfire/")
            except:
                pass
            print(os.getenv('LOCALAPPDATA') + "/GWPWildfire/user.cfg")

            
                
            with open(os.getenv('LOCALAPPDATA') + "/GWPWildfire/user.cfg", "wt") as cfg:
                print("Writing user config...")
                cfg.write("WILDFIREMODTOOL")
                cfg.write("mgr_path="+rev_exe_path)
                cfg.write("lang=en")
                cfg.write("theme=wildfire_dark")
                

                
                
            
            
        print("Loading WILDFIRE")
        print("Loading CFG")
        self.res = "100x100"
        self.cfglibrary = Configlib.ConfigLibrary("bin\\wildfire.cfg")
        self.res = self.cfglibrary.find_value("resolution")
        
        self.VALID_CONTAINER_FILES = self.cfglibrary.find_value("valid_dat_extensions").split(",")
        try:
            pyglet.font.add_file(self.cfglibrary.find_value("title_font_path"))
            pyglet.font.add_file(self.cfglibrary.find_value("light_font_path"))
            self.light_font = self.cfglibrary.find_value("light_font")
            self.title_font = self.cfglibrary.find_value("title_font")
        except:
            windows.MsgBox("Critical font loading error.\nCheck bin/wildfire.cfg and ensure fonts exist.", windows.MB_OK | windows.MB_ICONERROR, "Wildfire Mod Tool")
            quit()
        
        self.extension_cfg_reader = Configlib.ConfigLibrary("bin\\extensions.cfg")
        
        super().__init__()      
        self.bg = self.cget("fg_color")
        self.num_of_frames = 0
        # self.state('withdraw')
        
        
        if not is_console_mode:
            self.title("Wildfire Mod Tool v" + self.APP_VERSION + " | " + platform.system() + " " + platform.release())
        else:
            self.title("Wildfire Mod Tool | Xbox 360/PS3 MODE v" + self.APP_VERSION + " | " + platform.system() + " " + platform.release())
        
        self.iconpath = ImageTk.PhotoImage(file="bin\\ui\\req\\icon.png")
        self.wm_iconbitmap()
        self.iconphoto(False, self.iconpath)
        # screen size
        self.geometry(self.res)
        self.detached_items = []

        # Menu bar
        menu = CTkMenuBar(self, bg_color="#212121")
        button_1 = menu.add_cascade("File")
        button_2 = menu.add_cascade("Edit")
        button_3 = menu.add_cascade("Settings")
        button_4 = menu.add_cascade("Help")

        dropdown1 = CustomDropdownMenu(widget=button_1)
        dropdown1.add_option(option="Open", command=self.open_file_screen_0_explorer)

        dropdown1.add_separator()

        dropdown1.add_option(option="Export", command=self.save)
        dropdown1.add_option(option="Export As", command=self.save_as)

        dropdown2 = CustomDropdownMenu(widget=button_2)
        #dropdown2.add_option(option="Add")
        dropdown2.add_option(option="Delete", command=self.delete_item)
        dropdown2.add_option(option="Replace", command=self.replace_button)
        #dropdown2.add_option(option="Rename")

        dropdown3 = CustomDropdownMenu(widget=button_3)
        dropdown3.add_option(option="Preferences", command=self.open_pref_window)
        #dropdown3.add_option(option="Update", command=self.check_for_update)

        dropdown4 = CustomDropdownMenu(widget=button_4)
        dropdown4.add_option(option="About", command=self.open_about_window)
        
        # root!
        main_container = customtkinter.CTkFrame(self, corner_radius=8, fg_color=self.bg)
        main_container.pack(fill=tkinter.BOTH, expand=True, padx=8, pady=8)

        # right side panel -> to show the frame1 or frame 2, or ... frame + n where n <= 5
        self.right_side_panel = customtkinter.CTkFrame(main_container, corner_radius=8, fg_color="#212121")
        self.right_side_panel.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True, padx=0, pady=0)
        self.right_side_panel.configure(border_width = 1)
        self.right_side_panel.configure(border_color = "#323232")

        # Create frames
        self.create_frame(0)
        
        if self.cfglibrary.find_value("check_for_update_on_startup") == "yes":
            print("Checking for update...")
        
        
        
        # Activate main frame
        self.toggle_frame_by_id(0)
        
    def check_for_update(self):
        self.create_frame(3)
        self.toggle_frame_by_id(3)
        # Update code here

        
    def open_about_window(self):
        windows.MsgBox("Wildfire Mod Tool, Version: " + self.APP_VERSION + "\nSundowner Mod Tool's spritiual successor\nCredit:\nDAT unpacking script based off of KwasTools\nVarious file reading tools based off Nier2Blender by SpaceCore", windows.MB_ICONINFORMATION, "I was too lazy to make a real about window for the preview")
        
        
    def open_pref_window(self):
         prefrences_window.create_window()
        

    def open_file_screen_0_explorer(self):
        filename = filedialog.askopenfilename(title = "Select a File", filetypes = (("MGR:R Container File", "*.dat *.dtt *.evn *.eff"), ("Wildfire Mod Tool Theme", "*.wildfire"))) 
        if filename != "":
            self.drag_drop_screen_0(spoof_event(filename))

                    
    def drag_drop_screen_0(self,event):
        self.file_dir = event.data
        self.file_name = os.path.basename(event.data)
        self.file_extension = os.path.splitext(event.data)[1]
        print("Loading file: " + self.file_name)
        if self.file_extension in self.VALID_CONTAINER_FILES:
            print("Valid file!")
            start = time.time()
            self.create_frame(1)
            self.toggle_frame_by_id(1)
            file = BinaryLib.BinaryFile(False)
            file.open_file_from_path(event.data)
            datreader = MGR.DatReader()
            end = time.time()
            print("Loaded in " + str((end - start) * 1000) + "ms")
            self.loaded_files = datreader.read_file(file.file_bytes, self.file_name)  
            self.title("Wildfire Mod Tool | " + self.file_name)
            if len(self.loaded_files) == 0:
                windows.MsgBox("This " + self.file_extension.strip(".") + " contains 0 sub files, it can still be edited though", windows.MB_OK | windows.MB_ICONINFORMATION, "Wildfire Mod Tool")   
            self.create_frame(2)
            self.toggle_frame_by_id(2)
            
            
        else:
            windows.MsgBox("The file type (" + self.file_extension + ") is not supported at this time.", windows.MB_OK | windows.MB_ICONINFORMATION, "Wildfire Mod Tool")
    def drag_drop_start_0(self,event):
        App.frames[self.current_frame].configure(border_color = "#FFFFFF")
        

    def drag_drop_end_0(self,event):
        print("Drag-drop started")
        App.frames[self.current_frame].configure(border_color = "#323232")

    
    # Drop 1
    def replace_button(self):
        curItem = self.treeview.focus()
        if self.treeview.item(curItem)["text"]:
            filename = filedialog.askopenfilename(title = "Replace File", filetypes = (("Wildfire Suggested Input", "*" + os.path.splitext(self.treeview.item(curItem)["text"])[1]), ("Any file", "*.*"))) 
            if filename != "":     
                self.drag_drop_screen_1(spoof_event(filename))
        else:
            print("Nothing to replace")
    

    def drag_drop_screen_1(self,event):
        input_name = os.path.basename(event.data)
        self.edit_panel.configure(border_color = "#323232")
        curItem = self.treeview.focus()
        if windows.MsgBox("Replace " + self.edit_panel_text.cget("text") + " with " + input_name + "?", windows.MB_YESNO | windows.MB_ICONINFORMATION, "Wildfire Mod Tool") == windows.IDYES:
            print("Replace file")
            for file in self.loaded_files: 
                if file.f_name == self.treeview.item(curItem)["text"]:
                    tmp = BinaryLib.BinaryFile()
                    tmp.open_file_from_path(event.data)
                    file.f_data = tmp.read_all()
                    self.treeview.selection_set(curItem)

    def drag_drop_start_2(self,event):
        self.tv_frame.configure(border_color = "#FFFFFF")
        

    def drag_drop_end_2(self,event):
        self.tv_frame.configure(border_color = "#323232")

    def drag_drop_screen_2(self,event):
        input_name = os.path.basename(event.data)
        self.tv_frame.configure(border_color = "#323232")
        curItem = self.treeview.focus()
        if windows.MsgBox("Add " + input_name + " to the file?", windows.MB_YESNO | windows.MB_ICONINFORMATION, "Wildfire Mod Tool") == windows.IDYES:
            print("add file")
            binary = BinaryLib.BinaryFile()
            binary.open_file_from_path(event.data)
            temp_file = MGR.DatFile.File(input_name, binary.read_all())
            
            self.loaded_files.append(temp_file)
            tmp = self.treeview.insert(self.root, 'end',text=temp_file.f_name,values=(str(self.return_file_type_desc(temp_file.f_name))))
            self.treeview_objects.append(tmp)

    def drag_drop_start_1(self,event):
        self.edit_panel.configure(border_color = "#FFFFFF")
        

    def drag_drop_end_1(self,event):
        self.edit_panel.configure(border_color = "#323232")



    def format_file_sizes(self, byte_count):
        output = byte_count
        suffix = "B"

        if byte_count > 1000:
            suffix = "KB"
            output = byte_count / 1000
        if byte_count > 1e+6:
            suffix = "MB"
            output = byte_count / 1e+6
        if byte_count > 1e+9:
            suffix = "GB"
            output = byte_count / 1e+9
        
        output = round(output * 100)
        output = output / 100
        return str(output) + suffix
        

    def selectItem(self, a):
        try:
            self.selected_file = None
            curItem = self.treeview.focus()
            for file in self.loaded_files: 
                if file.f_name == self.treeview.item(curItem)["text"]:
                    self.selected_file = file
            
            
            self.edit_panel_text.configure(True, text=self.treeview.item(curItem)["text"])
            metadata = ""
            try:
                if os.path.splitext(self.selected_file.f_name)[1] == ".wmb":
                    metadata = "Model Type: " + MGR.get_wmb_type(self.selected_file.f_data)
                elif os.path.splitext(self.selected_file.f_name)[1] == ".scr":
                    metadata = "Model Type: " + MGR.get_scr_type(self.selected_file.f_data)     
                elif os.path.splitext(self.selected_file.f_name)[1] == ".wta":
                    metadata = "Metadata:\n" + MGR.get_wta_metadata(self.selected_file.f_data)        
                elif os.path.splitext(self.selected_file.f_name)[1] == ".mot":
                    metadata = MGR.get_mot_metadata(self.selected_file.f_data)  
                elif os.path.splitext(self.selected_file.f_name)[1] == ".ly2":
                    metadata = MGR.get_ly2_metadata(self.selected_file.f_data)     
            except:
                metadata = "Error loading preview data, file type mismatch?"
            
            self.edit_panel_desc.configure(True, text=self.return_file_type_desc(self.treeview.item(curItem)["text"]) + " | " + str(self.format_file_sizes(len(self.selected_file.f_data))) + "\n" + metadata)
        except:
            pass
    def create_treeview(self, parent, root, files):
        for file in files:
            tmp = parent.insert(root, 'end',text=file.f_name,values=(str(self.return_file_type_desc(file.f_name))))
            self.treeview_objects.append(tmp) 
            if file.is_container:
                print("Creating treeview " + file.f_name)
                self.create_treeview(parent, tmp, file.contained_files.values())
    
    def searchbar(self, p1=None):
        tree = self.treeview
        root_items = tree.get_children('')
        matching_items = []
        for item in root_items:
            matching_items.extend(self.search_treeview(tree, item, self.search_bar.get()))
        
        # self.treeview.selection_set(matching_items)
        if self.search_bar.get() != "":
            for item in matching_items:
                #self.treeview.selection_set(item)  #Select the matching item...
                self.treeview.focus(item)  #Focus on the matching item...
                self.treeview.see(item)  #Scroll to make the matching item visible...


    def delete_item(self):
        curItem = self.treeview.focus()
        if windows.MsgBox("Are you sure you want to delete " + self.treeview.item(curItem)["text"] + "?", windows.MB_YESNO | windows.MB_ICONINFORMATION, "Wildfire Mod Tool") == windows.IDYES:
            print("Delete file")
            for file in self.loaded_files: 
                if file.f_name == self.treeview.item(curItem)["text"]:
                    self.loaded_files.remove(file)
            self.treeview.delete(curItem)


    def search_treeview(self, tree, item, search_text):
        matching_items = []
        # Get item's text
        item_text = tree.item(item, 'text')
        
        # Check if the search_text is in the item text
        if search_text.lower() in item_text.lower():
            matching_items.append(item)

        # Get children items
        children = tree.get_children(item)
        for child in children:
            matching_items.extend(self.search_treeview(tree, child, search_text))
        
        return matching_items
      
    def export_file(self):
        curItem = self.treeview.focus()
        if self.treeview.item(curItem)["text"]:
            suggested_output = os.path.splitext(self.treeview.item(curItem)["text"])[1]
            filename = filedialog.asksaveasfilename(title = "Save File", filetypes = (("Wildfire Suggested Output", "*" + suggested_output), ("Any file", "*.*")), initialfile=self.treeview.item(curItem)["text"]) 
            if filename != "":     
                for x in self.loaded_files:
                    if x.f_name == self.treeview.item(curItem)["text"]:
                        if os.path.splitext(filename)[1] == "":
                            filename = filename + suggested_output
                        f = open(filename, "wb")
                        f.write(x.f_data)
                        break
        else:
            print("Nothing to replace")           
    
    # create the frame
    def create_frame(self, frame_id):
        self.current_frame = frame_id
        App.frames[frame_id] = customtkinter.CTkFrame(self, fg_color=self.cget("fg_color"))
        if frame_id in self.FRAME_ID_WITH_BORDER:
            App.frames[frame_id].configure(corner_radius = 8)
            App.frames[frame_id].configure(border_width = 2)
            App.frames[frame_id].configure(border_color = "#323232")
            App.frames[frame_id].padx = 8
        # Starting Screen
        if frame_id == 0:
            frame_0_text  = customtkinter.CTkLabel(App.frames[frame_id], text="Drag and drop any MGR data file onto this pane", font=(self.light_font, 25))
            frame_0_text.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
            App.frames[frame_id].drop_target_register(DND_FILES)
            App.frames[frame_id].dnd_bind('<<Drop>>', self.drag_drop_screen_0)
            App.frames[frame_id].dnd_bind('<<DropEnter>>', self.drag_drop_start_0)
            App.frames[frame_id].dnd_bind('<<DropLeave>>', self.drag_drop_end_0)
            
        # Loading Bar For Dat
        elif frame_id == 1:
            frame_1_text  = customtkinter.CTkLabel(App.frames[frame_id], text="Loading file data...", font=(self.light_font, 25))
            frame_1_text.place(relx=0.5, rely=0.4, anchor=tkinter.CENTER)
            
            if self.cfglibrary.find_value("display_file_name_while_loading") == "yes":
                frame_1_text_2 = customtkinter.CTkLabel(App.frames[frame_id], text=self.file_name + self.file_extension, font=(self.light_font, 15))
                frame_1_text_2.place(relx=0.5, rely=0.6, anchor=tkinter.CENTER)
            
            
            frame_1_progress_bar = customtkinter.CTkProgressBar(App.frames[frame_id], 1000, 20, 5, mode='indeterminate', indeterminate_speed=2)
            frame_1_progress_bar.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
            frame_1_progress_bar.start()
            


            
        # WMT Dat Menu
        elif frame_id == 2:

            title = customtkinter.CTkLabel(App.frames[frame_id], text="Wildfire Mod Tool", font=(self.title_font, 35), anchor=tkinter.S)
            title.place(relx=0, rely=0, anchor=tkinter.NW)
            
            files_loaded_counter = customtkinter.CTkLabel(App.frames[frame_id], text=str(len(self.loaded_files)) + " files loaded", font=(self.title_font, 25), anchor=tkinter.S)
            files_loaded_counter.place(x=450, rely=0, anchor=tkinter.NW)

            # Input text
            self.search_bar = customtkinter.CTkEntry(App.frames[frame_id], 500, 26, 5, font=(self.light_font, 12))
            self.search_bar.bind("<KeyRelease>", command=self.searchbar)
            self.search_bar.place(x=0, y=35)
            search_button = customtkinter.CTkButton(App.frames[frame_id], 100, 26, 5, font=(self.light_font, 12), text="SEARCH", command=self.searchbar)
            search_button.place(x=510, y=35)
            
            

            # Treeview
            bg_color = self._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkFrame"]["fg_color"])
            text_color = self._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkLabel"]["text_color"])
            selected_color = self._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkButton"]["fg_color"])

            treestyle = ttk.Style()
            treestyle.theme_use('default')
            treestyle.configure("Treeview", background=bg_color, foreground=text_color, fieldbackground=bg_color, borderwidth=0, font=(self.light_font, 12), rowheight=30)
            treestyle.map('Treeview', background=[('selected', bg_color)], foreground=[('selected', selected_color)])
            self.bind("<<TreeviewSelect>>", lambda event: self.focus_set())

            # Treeview widget data
            self.tv_frame = customtkinter.CTkFrame(App.frames[frame_id])
            self.tv_frame.configure(corner_radius = 8)
            self.tv_frame.configure(border_width = 2)
            self.tv_frame.configure(border_color = "#323232")
            self.tv_frame.pack(side=tkinter.LEFT, fill=tkinter.Y, pady=70)
            

            
            self.treeview = ttk.Treeview(self.tv_frame, column=("c1"), show="tree")
            self.treeview.column("# 0",anchor="w", width=400)
            self.treeview.column("# 1",anchor="e", width=200)
            self.treeview.heading("# 1", text="Type")   
            self.treeview.bind('<ButtonRelease-1>', self.selectItem)
            self.root = self.treeview.insert('', 'end',text=self.file_name,values=('Container')) 
            self.treeview_objects = []
            self.create_treeview(self.treeview, self.root, self.loaded_files)
            
            self.treeview.drop_target_register(DND_FILES)
            self.treeview.dnd_bind('<<Drop>>', self.drag_drop_screen_2)
            self.treeview.dnd_bind('<<DropEnter>>', self.drag_drop_start_2)
            self.treeview.dnd_bind('<<DropLeave>>', self.drag_drop_end_2)                    

            
            
            self.treeview.pack(side=tkinter.LEFT, fill=tkinter.Y, expand=tkinter.TRUE)
            self.tv_scroll = customtkinter.CTkScrollbar(self.tv_frame, command=self.treeview.yview)
            self.tv_scroll.pack(side=tkinter.LEFT, fill=tkinter.Y, expand=tkinter.TRUE)
            self.treeview.configure(yscrollcommand=self.tv_scroll.set)
            
            # Edit Pane
            self.edit_panel = customtkinter.CTkFrame(App.frames[frame_id], fg_color=self.cget("fg_color"))
            self.edit_panel.configure(corner_radius = 8)
            self.edit_panel.configure(border_width = 2)
            self.edit_panel.configure(border_color = "#323232")
            self.edit_panel.pack(side=tkinter.RIGHT, fill=tkinter.BOTH, expand=tkinter.TRUE, pady=35, padx=5)           
            
            self.edit_panel.drop_target_register(DND_FILES)
            self.edit_panel.dnd_bind('<<Drop>>', self.drag_drop_screen_1)
            self.edit_panel.dnd_bind('<<DropEnter>>', self.drag_drop_start_1)
            self.edit_panel.dnd_bind('<<DropLeave>>', self.drag_drop_end_1)
            
            self.edit_panel_text = customtkinter.CTkLabel(self.edit_panel, text="N/A", font=(self.light_font, 25))
            self.edit_panel_text.place(x=10, y=5)
 
            self.edit_panel_desc = customtkinter.CTkLabel(self.edit_panel, text="N/A", font=(self.light_font, 15), justify="left", anchor="w")
            self.edit_panel_desc.place(x=10, y=35)       
            
            export_button = customtkinter.CTkButton(self.edit_panel, 140, 28, 5, text="Export", font=(self.light_font, 15), command=self.export_file)   
            export_button.place(relx=0, x=10, rely=1, y=-10, anchor=tkinter.SW)

            replace_button = customtkinter.CTkButton(self.edit_panel, 140, 28, 5, text="Replace", font=(self.light_font, 15), command=self.replace_button)   
            replace_button.place(relx=0, x=160, rely=1, y=-10, anchor=tkinter.SW)

            
        # Loading Bar auto updater
        elif frame_id == 3:
            frame_1_text  = customtkinter.CTkLabel(App.frames[frame_id], text="Updating Wildfire Mod Tool...", font=(self.light_font, 25))
            frame_1_text.place(relx=0.5, rely=0.4, anchor=tkinter.CENTER)
            
            
            frame_1_progress_bar = customtkinter.CTkProgressBar(App.frames[frame_id], 1000, 20, 5, mode='indeterminate', indeterminate_speed=2)
            frame_1_progress_bar.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)
            frame_1_progress_bar.start()
        
        
        
    def return_file_type_desc(self, extension : str):
        extension = os.path.splitext(extension)[1]
        output = self.extension_cfg_reader.find_value(extension)
        return output.replace(" ", "_")
        

    
    
    # method to change frames
    def toggle_frame_by_id(self, frame_id):
        
        if App.frames[frame_id] is not None:
            if App.current is App.frames[frame_id]:
                App.current.pack_forget()
                App.current = None
            elif App.current is not None:
                App.current.pack_forget()
                App.current = App.frames[frame_id]
                App.current.pack(in_=self.right_side_panel, side=tkinter.TOP, fill=tkinter.BOTH, expand=True, padx=0, pady=0)
            else:
                App.current = App.frames[frame_id]
                App.current.pack(in_=self.right_side_panel, side=tkinter.TOP, fill=tkinter.BOTH, expand=True, padx=0, pady=0)

    def save(self):
        dat = MGR.DatReader()
        byte = dat.save_file(self.loaded_files)
        with open(self.file_dir, "wb") as f:
            f.write(byte)
            f.close()
        print("Done!")
        self.notification(self.file_extension + " file packaged!")

    def save_as(self):
        dat = MGR.DatReader()
        byte = dat.save_file(self.loaded_files)
        filename = filedialog.asksaveasfilename(title = "Save File", filetypes = (("Wildfire Suggested Output", "*" + self.file_extension), ("MGR:R Container File", "*.dat *.dtt *.evn *.eff"))) 
        if filename != "":     
            with open(filename, "wb") as f:
                f.write(byte)
                f.close()
            print("Done!")
            self.notification(self.file_extension + " file packaged!")

    def notification(self, text):
        notification.notify(
        title = "Wildfire Mod Tool v" + self.APP_VERSION,
        message = text,
        timeout = 2
        )

if __name__ == "__main__":
    if "-360" in sys.argv:
        print("Launching in console mode...")
        is_console_mode = True
    a = App()
    a.mainloop()