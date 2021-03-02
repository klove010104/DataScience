# -*- coding: utf-8 -*-
"""Call Vocab Checker to check a list of terms against a standard vocabulary.

This module allows the user to specify via GUI the input file, threshold, and 
max matches for comparing to the standard vocabulary. Note the standard 
vocabulary is obfuscated in the controller class VocabChecker.

  input file 
      Excel file with columns 'Entity Name' and 'Attribute Name'
      and 'Attribute/Column Definition' (TODO not used)
      rows with blank Attribute Names will be dropped
  output file
      Excel file in the same directory as the input file

Created on Sun Feb 14 13:15:59 2021

@author: klove
"""

import os
import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter.constants import LEFT, RIGHT
import VocabChecker

WORKING_DIRECTORY = "./"
RESULT_FILE_NAME = 'Matched_Vocab.xlsx'
 
def get_file_name():
    """Returns the fully qualified file name that the user selects.
    
    """
    file_name = askopenfilename(initialdir=WORKING_DIRECTORY,
                           filetypes =(("Excel File", "*.xlsx"),("All Files","*.*")),
                           title = "Choose a file."
                           )
    return file_name

def close_app():
    window.destroy()


def run_app():
    """Gathers the user inputs and calls VocabChecker

    """
    myLabel.config(text = "getting user inputs")
    # validate inputs
    try:
        user_threshold = int(match_threshold_entry.get())
        if (user_threshold < 0)|(user_threshold > 100):
            raise ValueError()
    except ValueError:
        myLabel.config(text = "Threshold must be an integer between 0 and 100")
        return 
    
    try:
        user_max_matches = int(max_matches_entry.get())
        if (user_max_matches <= 0):
            raise ValueError()
    except ValueError:
        myLabel.config(text = "Max Matches must be an integer greater than 0")
        return 
    
    user_file_name = get_file_name()
    if (len(user_file_name)==0):
        myLabel.config(text = "No file name chosen.")
        return
    
    myLabel.config(text = "file: " + user_file_name)
    results = VocabChecker.run_vocab_match(user_file_name, user_threshold, user_max_matches)
    #print(results.head())
    directory = os.path.split(user_file_name)[0]
    #print(directory)
    result_file = directory + "/" + RESULT_FILE_NAME
    myLabel.config(text = "Writing results to " + result_file)
    results.to_excel(result_file)

# main program
window = tk.Tk() 
window.title("Vocabulary Checker") 
window.geometry("600x300") # size of the window when it opens

# three frames on top of each other
frame_header = tk.Frame(window, borderwidth=2, pady=2)
center_frame = tk.Frame(window, borderwidth=2, pady=5)
bottom_frame = tk.Frame(window, borderwidth=2, pady=5)
frame_header.grid(row=0, column=0)
center_frame.grid(row=1, column=0)
bottom_frame.grid(row=2, column=0)

# label header to be placed in the frame_header
header = tk.Label(frame_header, text = "Vocab Checker Tool", bg='blue', fg='white', height='3', width='50', font=("Helvetica 16 bold"))
# inside the grid of frame_header, place it in the position 0,0
header.grid(row=0, column=0)
header2 = tk.Label(frame_header, text = "Check your list against standard vocabulary", height='1', width='50', font=("Helvetica 12 bold"))
header2.grid(row=1, column=0)

# an additional frame inside the center_frame
frame_main_1 = tk.Frame(center_frame, borderwidth=2, relief='sunken')
frame_main_2 = tk.Frame(center_frame, borderwidth=2, relief='sunken')

# populate the frames with the labels referring to the inputs we want from the user
match_threshold = tk.Label(frame_main_1, text = "Match Threshold: ")
max_matches = tk.Label(frame_main_1, text = "Max Number of Matches:")
myLabel = tk.Label(frame_main_2, text = "Choose threshold, max, then click Run to choose input file", width='50', font=("Helvetica 10"))
# Put it simply: StringVar() allows you to easily track tkinter variables and see if they were read, changed, etc
# check resources here for more details: http://effbot.org/tkinterbook/variable.htm
match_threshold1 = tk.StringVar()
max_matches1 = tk.StringVar()

# creating the entries for the user input
match_threshold_entry = tk.Entry(frame_main_1, textvariable = match_threshold1, width=4)
max_matches_entry = tk.Entry(frame_main_1, textvariable = max_matches1, width=4)

# and we pack the frame in the center_frame and then the elements inside them
frame_main_1.pack(fill='x', pady=2)
frame_main_2.pack(fill='x', pady=2)

# the order which we pack the items is important
match_threshold.pack(side=LEFT)
match_threshold_entry.pack(side=LEFT, padx=2)

max_matches_entry.pack(side=RIGHT, padx=2)
max_matches.pack(side=RIGHT)

myLabel.pack(pady=10)

# a proper app needs some buttons too!
button_run = tk.Button(bottom_frame, text="Run", command=run_app, bg='dark green', fg='white', relief='raised', width=10, font=('Helvetica 9 bold'))
button_run.grid(column=0, row=0, sticky='w', padx=100, pady=2)

button_close = tk.Button(bottom_frame, text="Exit", command=close_app, bg='dark red', fg='white', relief='raised', width=10, font=('Helvetica 9'))
button_close.grid(column=1, row=0, sticky='e', padx=100, pady=2)

window.mainloop()