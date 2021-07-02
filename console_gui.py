# Import modules
import tkinter as tk
from datetime import datetime as dt
from tkinter import messagebox, END

# Initialise
root = tk.Tk()

# Variables
title    = 'Messenger.exe'
iconpath = 'C:/Python/Learning/learning_gui_console_icon.ico'

screen_width  = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

app_width  = 950
app_height = 450

window_position_x = int((screen_width / 2) - (app_width / 2))
window_position_y = int((screen_height / 2) - (app_height / 2))

# Setup
root.title(title)
root.iconbitmap(iconpath)
root.geometry(f'{app_width}x{app_height}+{window_position_x}+{window_position_y}')
root.resizable(False, False)

# Functions
def quit():
    if messagebox.askyesno(title, 'Are you sure you want to quit?'):
        root.quit()

def getTime():
    raw_time    = dt.now().strftime('%x %X')
    time_string = str(raw_time)
    return time_string

def submit(event):
    if not (entry_1.get() == ''):
        time = getTime()
        entry = entry_1.get()
        message = time + ' User: ' + entry
        label = tk.Label(frame, text=message)
        label.pack()
        entry_1.delete(0, END)

# Menu bar
menubar = tk.Menu(root)
root.config(menu=menubar)
file_menu = tk.Menu(menubar)
menubar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label='Exit',command=quit)

# Create frames
frame = tk.LabelFrame(root, text='Welcome User!', padx=5, pady=5)

# Create entries
entry_1 = tk.Entry(root, text='Enter your name', width=50, borderwidth=5)

# Create button
button_submit = tk.Button(root, text='Submit', command = lambda: submit(''), padx=10)
root.bind("<Return>", submit)

# Place widgets
frame.grid(row=0, column=0, columnspan=2, padx=20, pady=5)
placeholder = tk.Label(frame, text='').pack()
entry_1.grid(row=1, column=0, padx=(20, 10), pady=10)
button_submit.grid(row=1, column=1, padx=(10, 20), pady=5)

root.mainloop()
