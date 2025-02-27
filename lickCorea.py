# Copyright (c) 2025, Michael Žutić, Oliver Köll
# All rights reserved.
#
# This source code is licensed under the
# MIT License found in the LICENSE.txt file 
# in the root directory of this source tree.

import sys
import os
import lick_reader as lr
import lick_writer as lw
import lick_parser as lp

cmd_line_arg_01 = sys.argv[1]

if cmd_line_arg_01 == "readLick":
    midiHarmonyFileName = input("\nEnter Harmony-File name: ")
    midiFileName = input("Enter MIDI-File name: ")
    midiFileTag = input("Enter MIDI-File tag: ")

    new_licks = lr.read_split_midi_files(midiFileName, midiHarmonyFileName)
    lr.update_database(new_licks, midiFileTag)

    print("\nYour lick has been successfully added to the database!\n")

elif cmd_line_arg_01 == "readMutipleLicks":

    filePath = input("\nEnter File-Path: ") 
    fileName = input("Enter File name: ")
    lickNumber = input("How many licks do you want to read: ")
    midiFileTag = input("Enter MIDI-File tag: ")

    for i in range(1,int(lickNumber)+1):
        
        midiFileName = filePath + "/" + fileName + f"{i}" + ".mid"
        midiHarmonyFileName = filePath + "/" + fileName + f"{i}" + ".rb"
        
        new_licks = lr.read_split_midi_files(midiFileName, midiHarmonyFileName)
        lr.update_database(new_licks, midiFileTag)

    print("\nYour licks have been successfully added to the database!\n")

elif cmd_line_arg_01 == "database":
    while 1:
        databaseOperation = input("\nDatabase Operation > ")
        if databaseOperation == "clear":
            lr.clear_database()
            print("\nYour lick database has been successfully cleaned!")
        elif databaseOperation == "show":
            print("\nYour lick database has the following tags: ")
            lr.show_database()
        elif databaseOperation == "exit":
            print("\n")
            break
        else:
            print("Database Command is not known!")

elif cmd_line_arg_01 == "writeLick":
    
    harmonyFileName = input("\nEnter Harmony-File name: ")
    melodyFileName = input("Enter Melody-File name: ")
    midiFileName = input("Enter MIDI-File name: ")

    lp.formatAndWriteFile(melodyFileName, harmonyFileName, midiFileName)

    with open("output.py","r") as file:
        code = file.read()
        exec(code)

    os.remove("output.py")

else:
    print(f"ERROR! CMD Line Arg: {cmd_line_arg_01} is unknown!")
