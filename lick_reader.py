# Copyright (c) 2025, Michael Žutić, Oliver Köll
# All rights reserved.
#
# This source code is licensed under the
# MIT License found in the LICENSE.txt file 
# in the root directory of this source tree.

import pretty_midi
import json

DATABASE = "database/lick_database.json"
BACKUP_DATABASE = "database/lick_database_backup.json"

# Harmony File Functions:
#   - functions for reading and processing the Harmony File
#
#   - helper
#   - turns chord into one out of three possible chord forms
def chord_to_vibe(chord):
    match chord:
        case "":
            return "maj"
        case "maj7":
            return "maj"
        case "m":
            return "min"
        case "m7":
            return "min"
        case "7":
            return "dom"

#   - splits a chord (char) into the midi note of the root of the chord and the cord function
def char_chord_processor(chord):
    midi_note = 0
    sign_parameter = 0
    root = chord[0]
    if len(chord) != 1: 
        if chord[1] == "b":
            sign_parameter = -1
            function = chord_to_vibe(chord[2:])
        elif chord[1] == "#":
            sign_parameter = 1
            function = chord_to_vibe(chord[2:])
        else:
            sign_parameter = 0
            function = chord_to_vibe(chord[1:])
    else:
        sign_parameter = 0
        function = "maj"

    match root:
        case "C":
            midi_note = 60 + sign_parameter
        case "D":
            midi_note = 62 + sign_parameter
        case "E":
            midi_note = 64 + sign_parameter
        case "F":
            midi_note = 65 + sign_parameter
        case "G":
            midi_note = 55 + sign_parameter
        case "A":
            midi_note = 57 + sign_parameter
        case "B":
            midi_note = 59 + sign_parameter

    return midi_note, function

#   - takes file name and creates a list of characters out of it
def read_harmony_file(file_name):
    harmony_array = []
    time_signature_flag = 1

    with open(file_name, 'r') as file:
        for line in file:
            if time_signature_flag == 1:
                numerator = int(line.strip()[:line.find("/")])
                denominator = int(line.strip()[line.find("/")+1:line.find(":")])
                tempo = int(line.strip()[line.find(":")+1:line.find("BPM")])
                harmony_array.append([numerator,denominator,tempo]) 
                time_signature_flag = 0
            elif line.find("|") == -1:
                pass
            else:
                for chord in line.split("|"):
                    if chord.strip() == "":
                        pass
                    elif chord.strip() == "%":
                        harmony_array.append(harmony_array[-1])   
                    else:
                        harmony_array.append(chord.strip())   
    return harmony_array

#   - takes harmony file and extracts the root notes, the chord functions and the root diffrences
def harmony_processor(file_name):
    read_harmony_file_out = read_harmony_file(file_name)
    signature_file = read_harmony_file_out[0]
    harmony_array = read_harmony_file_out[1:]

    time_signature = (signature_file[0], signature_file[1])
    tempo = signature_file[2]

    midiRootArray = []
    function_list = []

    for chord in harmony_array:
        midi_note, function = char_chord_processor(chord)
        midiRootArray.append(midi_note)
        function_list.append(function)
        
    return midiRootArray, function_list, time_signature, tempo  


###Lick Reader Functions###
#   - read and split midi files into chord based licks
def read_split_midi_files(midiFileName, harmonyFileName):
    lick_list = []
    new_lick_dict = {"pitch" : [], "time" : [], "note_duration" : [], "volume" : [], "chord" : [], "pitchWheelValue" : []}
    midi_data = pretty_midi.PrettyMIDI(midiFileName)

    midiRootArray, function_list, read_time_signature, readtempo = harmony_processor(harmonyFileName)

    for note in midi_data.instruments[0].notes:
        new_lick_dict["pitch"].append(note.pitch)
        new_lick_dict["time"].append(note.start)
        new_lick_dict["note_duration"].append(note.get_duration())
        new_lick_dict["volume"].append(note.velocity)
        new_lick_dict["pitchWheelValue"].append(0)

    new_lick_dict["chord"] = function_list

    #splitter part
    split_mark_list = []
    split_time_list = [0]
    root_list = [midiRootArray[0]]
    chord_cut = []
    beat = 0
    time_list = new_lick_dict["time"]
    old_chord = new_lick_dict["chord"][0]
    for chord in new_lick_dict["chord"]:
        if chord != old_chord:
            for time in time_list:
                if time*2 < beat:
                    pass
                else:
                    split_mark_list.append(time_list.index(time))
                    split_time_list.append(beat/2)
                    root_list.append(midiRootArray[beat])
                    chord_cut.append(beat)
                    break
            old_chord = chord
        beat += 1
    split_mark_list.append(len(time_list))
    chord_cut.append(beat)

    old_split_mark = 0
    old_chort_cut = 0
    for i in range(0,len(split_mark_list)):
        splitLick = {}
        splitLick["pitch"] = [x - root_list[i] for x in new_lick_dict["pitch"][old_split_mark:split_mark_list[i]]]
        splitLick["time"] = [x - split_time_list[i] for x in new_lick_dict["time"][old_split_mark:split_mark_list[i]]]
        splitLick["note_duration"] = new_lick_dict["note_duration"][old_split_mark:split_mark_list[i]]
        splitLick["volume"] = new_lick_dict["volume"][old_split_mark:split_mark_list[i]]
        splitLick["chord"] = new_lick_dict["chord"][old_chort_cut:chord_cut[i]]
        splitLick["pitchWheelValue"] = new_lick_dict["pitchWheelValue"][old_split_mark:split_mark_list[i]]
        splitLick["length"] = len(splitLick["chord"])
        lick_list.append(splitLick)
        old_split_mark = split_mark_list[i]
        old_chort_cut = chord_cut[i]

    return lick_list


# Database Operations:
# - functions for handeling the database
#
#   - sets database to backup state
def clear_database():
    with open(BACKUP_DATABASE, "r") as bfile:
        backup_database = json.load(bfile)
    lick_database = backup_database
    with open(DATABASE, "w") as file:
        json.dump(lick_database, file, indent=4)  # 'indent=4' für lesbares Format

#   - reads outdatabase and returns it in a dictonary
def load_database():
    with open(DATABASE, "r") as file:
        lick_database = json.load(file)
    return lick_database

#   - displays statistic of database
def show_database():
    lick_database = load_database()
    for key in lick_database.keys():
        print(f"Tag: {key}:")
        for chord_type in lick_database[key].keys():
            print(f"\t{chord_type}:\t{len(lick_database[key][chord_type])}")  

#   - updates several new licks to the database
def update_database(new_licks, tag):
    lick_database = load_database()

    if tag not in lick_database:
        lick_database[tag] = {   "min" : [{"pitch": [0], "time": [0],"note_duration": [0.01],"volume": [0],"chord": ["min"],"pitchWheelValue": [0],"length": 1}],
                                "maj" : [{"pitch": [0], "time": [0],"note_duration": [0.01],"volume": [0],"chord": ["maj"],"pitchWheelValue": [0],"length": 1}],
                                "dom" : [{"pitch": [0], "time": [0],"note_duration": [0.01],"volume": [0],"chord": ["dom"],"pitchWheelValue": [0],"length": 1}]}
    for lick in new_licks:
        lick_database[tag][lick["chord"][0]].append(lick)
    
    with open(DATABASE, "w") as file:
        json.dump(lick_database, file, indent=4)
