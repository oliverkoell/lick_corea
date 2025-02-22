# Copyright (c) 2025, Michael Žutić, Oliver Köll
# All rights reserved.
#
# This source code is licensed under the
# MIT License found in the LICENSE.txt file 
# in the root directory of this source tree.

import pretty_midi
import random
from itertools import combinations_with_replacement
import lick_reader as lr
import re


scales = {"ionian":         {   1:0,    2:2,    3:4,    4:5,    5:7,    6:9,    7:11    },
          "dorian":         {   1:0,    2:2,    3:3,    4:5,    5:7,    6:9,    7:10    },
          "phrygian":       {   1:0,    2:1,    3:3,    4:5,    5:7,    6:8,    7:10    },
          "lydian":         {   1:0,    2:2,    3:4,    4:6,    5:7,    6:9,    7:11    },
          "mixolydian":     {   1:0,    2:2,    3:4,    4:5,    5:7,    6:9,    7:10    },
          "aeolian":        {   1:0,    2:2,    3:3,    4:5,    5:7,    6:8,    7:10    },
          "locrian":        {   1:0,    2:1,    3:3,    4:5,    5:6,    6:8,    7:10    },

          "major":          {   1:0,    2:2,    3:4,    4:5,    5:7,    6:9,    7:11    },
          "harmonic_minor": {   1:0,    2:2,    3:3,    4:5,    5:7,    6:8,    7:11    },
          "melodic_minor":  {   1:0,    2:2,    3:3,    4:5,    5:7,    6:9,    7:11    },

          "chromatic":       {   1:0,    2:1,    3:2,    4:3,    5:4,    6:5,    7:6,    8:7,    9:8,    10:9,   11:10   },
          "whole_half_diminished":  {   1:0,    2:2,    3:3,    4:5,    5:6,    6:8,    7:9,    8:11    },
          "half_whole_diminished":  {   1:0,    2:1,    3:3,    4:4,    5:6,    6:7,    7:9,    8:10    },
          "whole_tone":     {   1:0,    2:2,    3:4,    4:6,    5:8,    6:10,   7:12    },
          "minor_blues":    {   1:0,    2:3,    3:5,    4:6,    5:7,    6:10,   7:12    },
          "major_blues":    {   1:0,    2:2,    3:3,    4:4,    5:7,    6:9,    7:12    },
          "altered":        {   1:0,    2:1,    3:3,    4:4,    5:6,    6:8,    7:10    },
          }


# Transform-Functions:
#   - Functions for taking defined input for rhythm, degrees, ect. and creating a note dictonary
#   
#   - takes "string-rhythm" and duration and converts it to the dictonary note format used in the whole backend
def rhythm_to_time(rhythm, temp_duration):
    duration = temp_duration*0.5
    notes = []
    rhythm_dict = { "time": [], "note_duration": []}
    counter = 0
    hold_parm = False

    note_amount = rhythm.count(":") + rhythm.count(".") + rhythm.count("_")
    note_lenght = duration/note_amount
    rounded_note_lenght = round(note_lenght, 4)

    for note_value in rhythm:
        if note_value == ":":
            note_time = counter * note_lenght
            rounded_note_time = round(note_time,4)
            rhythm_dict["time"].append(rounded_note_time)
            rhythm_dict["note_duration"].append(rounded_note_lenght)
            hold_parm = True
        elif note_value == "_":
            if hold_parm == True:
                rhythm_dict["note_duration"][-1] += rounded_note_lenght
        elif note_value == ".":
            hold_parm = False
        counter +=1  
    return rhythm_dict


#   - helper for degree_to_note
#   - takes char degree input and converts it to midi note value
#   - also reads the microtonal information and puts it into midi pitch wheel format
def degree_function(degree, scale):
    val = float(degree)
    if (val - int(val)) == 0:
        return (scales[scale][int(val)], 0)
    elif (val - int(val)) == 0.5:
        return (scales[scale][int(val)] + 1, 0)
    else:
        pitch_val = int(8192 * round(val - int(val), 4))
        return (scales[scale][int(val)], pitch_val)


#   - takes list of notes and creats tuple of a midi note list and pitch value list
def degree_to_note(degree_list, scale):
    notes = []
    pitch_values = []
    for degree in degree_list:
        if degree.find("va") != -1:
            note_value, pitch_value = degree_function(degree[:degree.find("va")], scale)
            notes.append(note_value + 12)       
            pitch_values.append(pitch_value)
        elif degree.find("vb") != -1:
            note_value, pitch_value = degree_function(abs(float(degree[:degree.find("vb")])), scale)
            notes.append(note_value  - 24)       
            pitch_values.append(pitch_value)
        elif float(degree) > 0:
            note_value, pitch_value = degree_function(degree, scale)
            notes.append(note_value)       
            pitch_values.append(pitch_value)
        elif float(degree) < 0:
            note_value, pitch_value =  degree_function(abs(float(degree)), scale)
            notes.append(note_value - 12)       
            pitch_values.append(pitch_value)
        else:
            print(f"Note Parameter Error! Check your entert note - {degree}")
    return notes,pitch_values


#   - helper
#   - takes a notes string inptut and puts it into a list of string notes
def string_to_list(note_str):
    note_str = note_str.strip("[]")
    return re.split(r',\s*(?=[^,])', note_str)

#   - helper for create_lick function
#   - checks if entered lists have the same length
def list_length_check(*lists):
    return len(set(len(list) for list in lists)) == 1

#   - takes funtion input parameters and creates solo part in used dictonary format
def create_lick(rhythm, duration, degree_str, scale, volume_list, midi_root_note, time_offset):
    note_dict = {"pitch" : [], "time" : [], "note_duration" : [], "volume" : [], "chord" : [], "pitchWheelValue" : []}

    degree_list = string_to_list(degree_str)

    notes, pitch_values = degree_to_note(degree_list, scale)
    rhythm_dict = rhythm_to_time(rhythm, duration)

    if list_length_check(notes, pitch_values, rhythm_dict["time"], rhythm_dict["note_duration"], volume_list) == False:
        print("Something went wrong! Check your entered values in creatLick function.")
        return -1

    for note in notes:
        note_dict["pitch"].append(note + midi_root_note)
    for time in rhythm_dict["time"]:
        note_dict["time"].append(time + time_offset)

    note_dict["note_duration"] = rhythm_dict["note_duration"]
    note_dict["volume"] = volume_list
    note_dict["pitchWheelValue"] = pitch_values

    for i in range(0,len(note_dict["pitch"])):
        note_dict["chord"].append("")

    return note_dict

#   - helper for create_rand_degrees
#   - handels upper and lower boundary problems of a random lick
def randomnote_to_degree(note, scale, updown_flag):
    range_boundary = 7
    match scale:
        case "chromatic":
            range_boundary = 11
        case "whole_half_diminished":
            range_boundary = 8        
        case "half_whole_diminished":
            range_boundary = 8
    if note <= 0:
        if note > -(range_boundary):
            return f"-{abs(abs(note)-range_boundary)}", updown_flag
        elif note > -(range_boundary * 2):
            return f"-{abs(abs(note+range_boundary)-range_boundary)}vb", updown_flag
        else:
            return "-1vb", 1   
    else:
        if note <= range_boundary:
            return f"{note}", updown_flag
        elif note <= (range_boundary * 2):
            return f"{note - range_boundary}va", updown_flag
        else:
            return f"{range_boundary}va", -1
   
#   - creates pseudo random degree list
def create_rand_degrees(length, jump_prop, up_down_prop, scale):
    updown_flag = 1
    notes = [1]
    notes_char = ["1"]
    for i in range(1,length):
        if random.random() < (1-jump_prop):
            if updown_flag == 1:
                if random.random() < up_down_prop:
                    updown_flag = 1
                    new_note = notes[-1] + 1
                    new_degree, updown_flag = randomnote_to_degree(new_note, scale, updown_flag)
                    notes_char.append(new_degree)
                    notes.append(new_note)
                else:
                    updown_flag = -1
                    new_note = notes[-1] - 1
                    new_degree, updown_flag = randomnote_to_degree(new_note, scale, updown_flag)
                    notes_char.append(new_degree)
                    notes.append(new_note)
            elif updown_flag == -1:
                if random.random() < 1-up_down_prop:
                    updown_flag = 1
                    new_note = notes[-1] + 1
                    new_degree, updown_flag = randomnote_to_degree(new_note, scale, updown_flag)
                    notes_char.append(new_degree)
                    notes.append(new_note)
                else:
                    updown_flag = -1
                    new_note = notes[-1] - 1
                    new_degree, updown_flag = randomnote_to_degree(new_note, scale, updown_flag)
                    notes_char.append(new_degree)
                    notes.append(new_note)
        else:
            if random.random() < 0.33:
                new_note = notes[-1] + random.choice([-3,3])
                new_degree, updown_flag = randomnote_to_degree(new_note, scale, updown_flag)
                notes_char.append(new_degree)
                notes.append(new_note)
            elif  random.random() > 0.66:
                new_note = notes[-1] + random.choice([-4,4])
                new_degree, updown_flag = randomnote_to_degree(new_note, scale, updown_flag)
                notes_char.append(new_degree)
                notes.append(new_note)
            else:
                new_note = notes[-1] + random.choice([-5,5])
                new_degree, updown_flag = randomnote_to_degree(new_note, scale, updown_flag)
                notes_char.append(new_degree)
                notes.append(new_note)
        i += 1

    return notes_char


#   - creates a random solo 
def create_rand_lick(rhythm, duration, scale, volume_list, jump_prop, up_down_prop, midi_root_note, time_offset):
    note_dict = {"pitch" : [], "time" : [], "note_duration" : [], "volume" : [], "pitchWheelValue" : []}

    rhythm_dict = rhythm_to_time(rhythm, duration)
    degree_list = create_rand_degrees(len(rhythm_dict["time"]), jump_prop, up_down_prop, scale)
    notes, pitch_values = degree_to_note(degree_list, scale)

    if list_length_check(notes, pitch_values, rhythm_dict["time"], rhythm_dict["note_duration"], volume_list) == False:
        print("Something went wrong! Check your entered values in creatLick function.")
        return -1

    for note in notes:
        note_dict["pitch"].append(note + midi_root_note)
    for time in rhythm_dict["time"]:
        note_dict["time"].append(time + time_offset)

    note_dict["note_duration"] = rhythm_dict["note_duration"]
    note_dict["volume"] = volume_list
    note_dict["pitchWheelValue"] = pitch_values

    return note_dict


#   - splits a number into a list of elements out of an provided values list
def split_number_into_list(target, values):
    values = sorted(values, reverse=True)
    
    for r in range(1, target // min(values) + 1):
        for combination in combinations_with_replacement(values, r):
            if sum(combination) == target:
                return list(combination)
    return [] 


#   - function for finding the right random lick in database                                                                                            schöner!!!
def create_shred(style_tag, chord_list, midi_root_list, time_offset):
    lick_database = lr.load_database()
    new_lick = {"pitch" : [], "time" : [], "note_duration" : [], "volume" : [],"chord" :  [], "pitchWheelValue" : []}

    if style_tag not in lick_database:
        print(f"The given style {style_tag} was not found in our database!")

    database_lick_lengths = {"min" : {}, "maj" : {}, "dom" : {}}

    for chord_type in lick_database[style_tag]:
        for lick in lick_database[style_tag][chord_type]:
        
            if lick["length"] in database_lick_lengths[chord_type]:
                database_lick_lengths[chord_type][lick["length"]] += 1
            else:
                database_lick_lengths[chord_type][lick["length"]] = 1

    old_chord = chord_list[0]
    length = 0
    chord_lentghs = []
    chords = [chord_list[0]]
    
    for chord in chord_list:
        if chord != old_chord:
            chord_lentghs.append(length)
            chords.append(chord)
            length = 1
        else:
            length += 1
        old_chord = chord

    chord_lentghs.append(length)

    lick_lengths = []

    for i in range(0,len(chord_lentghs)):
        lick_lengths.extend(split_number_into_list(chord_lentghs[i], list(database_lick_lengths[chords[i]].keys())))

    new_chord_list = []
    counter = 0
    for length in lick_lengths:
        new_chord_list.append(chord_list[counter])
        counter += length

    final_lick_list = []
    for i in range(0,len(lick_lengths)):
        possible_licks = []
        for lick in lick_database[style_tag][new_chord_list[i]]:
            if lick["length"] == lick_lengths[i]:
                possible_licks.append(lick)
        final_lick_list.append(possible_licks)
            
    itt = 0
    beat = 0
    start_note = midi_root_list[0]

    for length in lick_lengths:
        upper_boundary = 1
        lower_boundary = -1
        while(True):
            rand_index = random.randint(0,(len(final_lick_list[itt])-1))
            if len(final_lick_list[itt][rand_index]["pitch"]) != 0:
                if (final_lick_list[itt][rand_index]["pitch"][0] + midi_root_list[beat] - start_note) < upper_boundary and (final_lick_list[itt][rand_index]["pitch"][0] + midi_root_list[beat] - start_note) > lower_boundary:
                    break
                else:
                    upper_boundary +=1
                    lower_boundary -=1
            else:
                pass

        new_lick["pitch"].extend(final_lick_list[itt][rand_index]["pitch"])
        new_lick["time"].extend(final_lick_list[itt][rand_index]["time"])
        new_lick["note_duration"].extend(final_lick_list[itt][rand_index]["note_duration"])
        new_lick["volume"].extend(final_lick_list[itt][rand_index]["volume"])

        for i in range(len(new_lick["pitch"])-len(final_lick_list[itt][rand_index]["pitch"]),len(new_lick["pitch"])):
            new_lick["pitch"][i] += midi_root_list[beat]
            new_lick["time"][i] += beat/2 + time_offset
            new_lick["pitchWheelValue"].append(0)

        start_note = final_lick_list[itt][rand_index]["pitch"][-1] + midi_root_list[beat]
        beat += length
        itt += 1

    return new_lick

#   - name_changes for transparser
#   - deterministic functions:
def ionian(rhythm, duration, notes, volume, midi_root_note, time_offset):
    return create_lick(rhythm=rhythm, duration=duration, degree_str=notes, scale="ionian", volume_list=volume, midi_root_note=midi_root_note, time_offset=time_offset)

def dorian(rhythm, duration, notes, volume, midi_root_note, time_offset):
    return create_lick(rhythm=rhythm, duration=duration, degree_str=notes, scale="dorian", volume_list=volume,  midi_root_note=midi_root_note, time_offset=time_offset)

def phrygian(rhythm, duration, notes, volume, midi_root_note, time_offset):
    return create_lick(rhythm=rhythm, duration=duration, degree_str=notes, scale="phrygian", volume_list=volume,  midi_root_note=midi_root_note, time_offset=time_offset)

def lydian(rhythm, duration, notes, volume, midi_root_note, time_offset):
    return create_lick(rhythm=rhythm, duration=duration, degree_str=notes, scale="lydian", volume_list=volume,  midi_root_note=midi_root_note, time_offset=time_offset)

def mixolydian(rhythm, duration, notes, volume, midi_root_note, time_offset):
    return create_lick(rhythm=rhythm, duration=duration, degree_str=notes, scale="mixolydian", volume_list=volume,  midi_root_note=midi_root_note, time_offset=time_offset)

def aeolian(rhythm, duration, notes, volume, midi_root_note, time_offset):
    return create_lick(rhythm=rhythm, duration=duration, degree_str=notes, scale="aeolian", volume_list=volume,  midi_root_note=midi_root_note, time_offset=time_offset)

def locrian(rhythm, duration, notes, volume, midi_root_note, time_offset):
    return create_lick(rhythm=rhythm, duration=duration, degree_str=notes, scale="locrian", volume_list=volume,  midi_root_note=midi_root_note, time_offset=time_offset)

def major(rhythm, duration, notes, volume, midi_root_note, time_offset):
    return create_lick(rhythm=rhythm, duration=duration, degree_str=notes, scale="major", volume_list=volume,  midi_root_note=midi_root_note, time_offset=time_offset)

def harmonicMinor(rhythm, duration, notes, volume, midi_root_note, time_offset):
    return create_lick(rhythm=rhythm, duration=duration, degree_str=notes, scale="harmonic_minor", volume_list=volume, midi_root_note=midi_root_note, time_offset=time_offset)

def melodicMinor(rhythm, duration, notes, volume, midi_root_note, time_offset):
    return create_lick(rhythm=rhythm, duration=duration, degree_str=notes, scale="melodic_minor", volume_list=volume, midi_root_note=midi_root_note, time_offset=time_offset)

def cromatic(rhythm, duration, notes, volume, midi_root_note, time_offset):
    return create_lick(rhythm=rhythm, duration=duration, degree_str=notes, scale="cromatic", volume_list=volume, midi_root_note=midi_root_note, time_offset=time_offset)

def wholeHalfDiminished(rhythm, duration, notes, volume, midi_root_note, time_offset):
    return create_lick(rhythm=rhythm, duration=duration, degree_str=notes, scale="whole_half_diminished", volume_list=volume, midi_root_note=midi_root_note, time_offset=time_offset)

def halfWholeDiminished(rhythm, duration, notes, volume, midi_root_note, time_offset):
    return create_lick(rhythm=rhythm, duration=duration, degree_str=notes, scale="half_whole_diminished", volume_list=volume, midi_root_note=midi_root_note, time_offset=time_offset)

def wholeTone(rhythm, duration, notes, volume, midi_root_note, time_offset):
    return create_lick(rhythm=rhythm, duration=duration, degree_str=notes, scale="whole_tone", volume_list=volume, midi_root_note=midi_root_note, time_offset=time_offset)

def minorBlues(rhythm, duration, notes, volume, midi_root_note, time_offset):
    return create_lick(rhythm=rhythm, duration=duration, degree_str=notes, scale="minor_blues", volume_list=volume, midi_root_note=midi_root_note, time_offset=time_offset)

def majorBlues(rhythm, duration, notes, volume, midi_root_note, time_offset):
    return create_lick(rhythm=rhythm, duration=duration, degree_str=notes, scale="major_blues", volume_list=volume, midi_root_note=midi_root_note, time_offset=time_offset)

def altered(rhythm, duration, notes, volume, midi_root_note, time_offset):
    return create_lick(rhythm=rhythm, duration=duration, degree_str=notes, scale="altered", volume_list=volume, midi_root_note=midi_root_note, time_offset=time_offset)

#   - random functions:
def randomIonian(rhythm, duration, volume, jump_prop, up_down_prop, midi_root_note, time_offset):
    return create_rand_lick(rhythm=rhythm, duration=duration, scale="ionian", volume_list=volume, jump_prop=jump_prop, 
                            up_down_prop=up_down_prop, midi_root_note=midi_root_note, time_offset=time_offset)

def randomDorian(rhythm, duration, volume, jump_prop, up_down_prop, midi_root_note, time_offset):
    return create_rand_lick(rhythm=rhythm, duration=duration, scale="dorian", volume_list=volume, jump_prop=jump_prop, 
                            up_down_prop=up_down_prop, midi_root_note=midi_root_note, time_offset=time_offset)

def randomPhrygian(rhythm, duration, volume, jump_prop, up_down_prop, midi_root_note, time_offset):
    return create_rand_lick(rhythm=rhythm, duration=duration, scale="phrygian", volume_list=volume, jump_prop=jump_prop, 
                            up_down_prop=up_down_prop, midi_root_note=midi_root_note, time_offset=time_offset)

def randomLydian(rhythm, duration, volume, jump_prop, up_down_prop, midi_root_note, time_offset):
    return create_rand_lick(rhythm=rhythm, duration=duration, scale="lydian", volume_list=volume, jump_prop=jump_prop, 
                            up_down_prop=up_down_prop, midi_root_note=midi_root_note, time_offset=time_offset)

def randomMixolydian(rhythm, duration, volume, jump_prop, up_down_prop, midi_root_note, time_offset):
    return create_rand_lick(rhythm=rhythm, duration=duration, scale="mixolydian", volume_list=volume, jump_prop=jump_prop, 
                            up_down_prop=up_down_prop, midi_root_note=midi_root_note, time_offset=time_offset)

def randomAeolian(rhythm, duration, volume, jump_prop, up_down_prop, midi_root_note, time_offset):
    return create_rand_lick(rhythm=rhythm, duration=duration, scale="aeolian", volume_list=volume, jump_prop=jump_prop, 
                            up_down_prop=up_down_prop, midi_root_note=midi_root_note, time_offset=time_offset)

def randomLocrian(rhythm, duration, volume, jump_prop, up_down_prop, midi_root_note, time_offset):
    return create_rand_lick(rhythm=rhythm, duration=duration, scale="locrian", volume_list=volume, jump_prop=jump_prop, 
                            up_down_prop=up_down_prop, midi_root_note=midi_root_note, time_offset=time_offset)

def randomMajor(rhythm, duration, volume, jump_prop, up_down_prop, midi_root_note, time_offset):
    return create_rand_lick(rhythm=rhythm, duration=duration, scale="major", volume_list=volume, jump_prop=jump_prop, 
                            up_down_prop=up_down_prop, midi_root_note=midi_root_note, time_offset=time_offset)

def randomHarmonicMinor(rhythm, duration, volume, jump_prop, up_down_prop, midi_root_note, time_offset):
    return create_rand_lick(rhythm=rhythm, duration=duration, scale="harmonic_minor", volume_list=volume, jump_prop=jump_prop, 
                            up_down_prop=up_down_prop, midi_root_note=midi_root_note, time_offset=time_offset)

def randomMelodicMinor(rhythm, duration, volume, jump_prop, up_down_prop, midi_root_note, time_offset):
    return create_rand_lick(rhythm=rhythm, duration=duration, scale="melodic_minor", volume_list=volume, jump_prop=jump_prop, 
                            up_down_prop=up_down_prop, midi_root_note=midi_root_note, time_offset=time_offset)

def randomCromatic(rhythm, duration, volume, jump_prop, up_down_prop, midi_root_note, time_offset):
    return create_rand_lick(rhythm=rhythm, duration=duration, scale="cromatic", volume_list=volume, jump_prop=jump_prop, 
                            up_down_prop=up_down_prop, midi_root_note=midi_root_note, time_offset=time_offset)

def randomWholeHalfDiminished(rhythm, duration, volume, jump_prop, up_down_prop, midi_root_note, time_offset):
    return create_rand_lick(rhythm=rhythm, duration=duration, scale="whole_half_diminished", volume_list=volume, jump_prop=jump_prop, 
                            up_down_prop=up_down_prop, midi_root_note=midi_root_note, time_offset=time_offset)

def randomHalfWholeDiminished(rhythm, duration, volume, jump_prop, up_down_prop, midi_root_note, time_offset):
    return create_rand_lick(rhythm=rhythm, duration=duration, scale="half_whole_diminished", volume_list=volume, jump_prop=jump_prop, 
                            up_down_prop=up_down_prop, midi_root_note=midi_root_note, time_offset=time_offset)

def randomWholeTone(rhythm, duration, volume, jump_prop, up_down_prop, midi_root_note, time_offset):
    return create_rand_lick(rhythm=rhythm, duration=duration, scale="whole_tone", volume_list=volume, jump_prop=jump_prop, 
                            up_down_prop=up_down_prop, midi_root_note=midi_root_note, time_offset=time_offset)

def randomMinorBlues(rhythm, duration, volume, jump_prop, up_down_prop, midi_root_note, time_offset):
    return create_rand_lick(rhythm=rhythm, duration=duration, scale="minor_blues", volume_list=volume, jump_prop=jump_prop, 
                            up_down_prop=up_down_prop, midi_root_note=midi_root_note, time_offset=time_offset)

def randomMajorBlues(rhythm, duration, volume, jump_prop, up_down_prop, midi_root_note, time_offset):
    return create_rand_lick(rhythm=rhythm, duration=duration, scale="major_blues", volume_list=volume, jump_prop=jump_prop, 
                            up_down_prop=up_down_prop, midi_root_note=midi_root_note, time_offset=time_offset)

def randomAltered(rhythm, duration, volume, jump_prop, up_down_prop, midi_root_note, time_offset):
    return create_rand_lick(rhythm=rhythm, duration=duration, scale="altered", volume_list=volume, jump_prop=jump_prop, 
                            up_down_prop=up_down_prop, midi_root_note=midi_root_note, time_offset=time_offset)


#   - shred mode:
def shredMode(style, duration, chords, midi_root_notes, time_offset):
    return create_shred(style_tag=style, chord_list=chords[time_offset:time_offset+duration], midi_root_list=midi_root_notes[time_offset:time_offset+duration], time_offset=time_offset/2)

#   - pause function:
def pause(duration):
    return duration

#           - specials:
def transposeHarmony(transpose_by,midi_root_notes):
    transposed_midi_root_notes = []
    for note in midi_root_notes:
        transposed_midi_root_notes.append(note + transpose_by)
    return transposed_midi_root_notes

def enablePracticeMode(midi_root_notes, chord_list):
    practice_midi_root_notes = []
    practice_chord_list = []
    for i in range(0,12):
        practice_chord_list.extend(chord_list)
        for note in midi_root_notes:
            practice_midi_root_notes.append(note + i)
    return practice_midi_root_notes, practice_chord_list


# Midi-Creator Functions:
#
#   - merges a reference new dictionary to a reference dictonary 
def merge_note_dicts(ref_dict, new_dict):
    for key in new_dict.keys():
        ref_dict[key].extend(new_dict[key])
    return ref_dict

#   - writes note dictonary to a midi file
def write_midi_from_dict(note_dict, output_filename, tempo=120, time_signature=(4, 4)):
    
    midi = pretty_midi.PrettyMIDI()

    midi._initial_tempo = tempo
    numerator, denominator = time_signature
    midi.time_signature_changes.append(pretty_midi.TimeSignature(numerator, denominator, time=0.0))

    instrument = pretty_midi.Instrument(program=0)

    for beat_nr in range(0,len(note_dict["pitch"])):
        note = pretty_midi.Note(velocity=note_dict["volume"][beat_nr], pitch=note_dict["pitch"][beat_nr], start=note_dict["time"][beat_nr], 
                                end=note_dict["time"][beat_nr] + note_dict["note_duration"][beat_nr])
        instrument.notes.append(note)

        pitch_bend_event = pretty_midi.PitchBend(note_dict["pitchWheelValue"][beat_nr], note_dict["time"][beat_nr])
        instrument.pitch_bends.append(pitch_bend_event)

    midi.instruments.append(instrument)

    midi.write(output_filename)

