# Copyright (c) 2025, Michael Žutić, Oliver Köll
# All rights reserved.
#
# This source code is licensed under the
# MIT License found in the LICENSE.txt file 
# in the root directory of this source tree.

import re

# Use regex to locate and transform the degree_list variables
def add_braces_to_degree_list(line):
    # Match degree_list and capture its content
    degree_list_match = re.search(r'notes\s*=\s*\[(.*?)\]', line)

    if degree_list_match:
        # Extract the content inside the degree_list
        degree_list_content = degree_list_match.group(1)

        # Regex to match:
        # 1. Integers (positive and negative), including those with 'va' or 'vb' (e.g., 3va, -2vb)
        # 2. Other values (e.g., variables) should be wrapped in {}.
        
        # First, handle variables and non-number words by wrapping them in {}
        degree_list_content = re.sub(r'\b(?![-+]?\d+(?:va|vb)?\b)(\w+)\b', r'{\1}', degree_list_content)

        # Now the degree_list contains {} wrapped only around non-number values
        # For example: y and test will be wrapped in {}, but 1, 1vb, 4va will remain unchanged.

        # Replace the degree_list part in the original line with the updated content
        line = line.replace(degree_list_match.group(0), f'notes = [{degree_list_content}]')
        line = re.sub(r'(notes\s*=\s*)\[(.*?)\]', r'\1f"[ \2 ]"', line)

    return line



FUNCTION_DETECTED = 1
NO_FUNCTION_DETECTED = 0
PRACTICE_MODE_ON = 1
PRACTICE_MODE_OFF = 0
# checks for specific functions and formats output file accordingly. 
# if no function was detected, line is passed through 
# functions: Modes, PracticeMode, transpoeHarmony, pause
def transform_function_call(line, indentation_level, output_path_midi):
    # Match the function name, arguments, and capture leading whitespace
    match = re.match(
        r'\b(ionian|dorian|phrygian|lydian|mixolydian|aeolian|locrian|'
        r'randomIonian|randomDorian|randomPhrygian|randonLydian|randomMixolydian|randomAeolian|randomLocrian|'
        r'major|harmonicMinor|melodicMinor|'
        r'pause|'
        r'randomMajor|randomHarmonicMinor|randomMelodicMinor|'
        r'cromatic|wholeHalfDiminished|halfWholeDiminished|wholeTone|'
        r'randomCromatic|randomWholeHalfDiminished|randomHalfWholeDiminished|randomWholeTone|'
        r'shredMode|transposeHarmony|enablePracticeMode|'
        r'randomMinorBlues|randomMajorBlues|randomAltered|'
        r'minorBlues|majorBlues|altered)\b\((.*)\)', 
        line
    )
    if match:
        # Extract leading whitespace, function name, and arguments
        func_name = match.group(1)   # Function name (e.g., "dorian")
        func_args = match.group(2)   # Function arguments (e.g., 'rhythm=":.:.", duration=2, notes=[1,7], note_volume=[100,70]')
        

        # Extract the duration value using another regex
        duration_match = re.search(r'\bduration\s*=\s*(\d+)', func_args)
        if duration_match:
            duration_value = duration_match.group(1)  # Extract the duration value as a string
        else:
            duration_value = "1"  # Default duration if not specified

        indentation = '\t' * indentation_level

        # Construct the replacement code block, properly indented 

        if (func_name == "enablePracticeMode"):
            practice_code = (
                f"{indentation}midi_root_notes, chord_list = lw.{func_name}(midi_root_notes, chord_list)\n"
                f"{indentation}max_len = len(midi_root_notes)\n"
                f"{indentation}while (key_count < 12):\n"
            )
            indentation_level += 1
            return practice_code, indentation_level,FUNCTION_DETECTED, PRACTICE_MODE_ON

        if (func_name == "transposeHarmony"):
            transpose_code = (
                f"{indentation}midi_root_notes = lw.{func_name}({func_args}, midi_root_notes)\n"
            )
            return transpose_code, indentation_level,FUNCTION_DETECTED, PRACTICE_MODE_OFF
    
        if (func_name == 'shredMode'):
            #print("shredding!")
            shred_code = (
                f"{indentation}if (beat + {duration_value}) <= max_len:\n"
                f"{indentation}\ttemp_dict = lw.{func_name}({func_args}, chords = chord_list, midi_root_notes = midi_root_notes, time_offset = beat)\n"
                f"{indentation}\tnote_dict = lw.merge_note_dicts(note_dict, temp_dict)\n"
                f"{indentation}\tbeat += {duration_value}\n"
                f"{indentation}else:\n"
                f"{indentation}\tlw.write_midi_from_dict(note_dict, '{output_path_midi}', tempo = readtempo, time_signature = read_time_signature)\n"
                f"{indentation}\tprint('Your created Lick was longer than the harmony file! The lick was successfully created until the end of the given harmony!')\n"
                f"{indentation}\tsys.exit()\n")
            return shred_code, indentation_level, FUNCTION_DETECTED, PRACTICE_MODE_OFF
            
        #func_args = add_quotes_to_degree_list(func_args)
        if (func_name == 'pause'):
            pause_line = ( f"{indentation}beat += lw.{func_name}({func_args})\n" )
            return pause_line, indentation_level, FUNCTION_DETECTED, PRACTICE_MODE_OFF
        
        
        trans_code = (
            f"{indentation}if (beat + {duration_value}) <= max_len:\n"
            f"{indentation}\ttemp_dict = lw.{func_name}({func_args}, midi_root_note = midi_root_notes[beat], time_offset = beat/2)\n"
            f"{indentation}\tnote_dict = lw.merge_note_dicts(note_dict, temp_dict)\n"
            f"{indentation}\tbeat += {duration_value}\n"
            f"{indentation}else:\n"
            f"{indentation}\tlw.write_midi_from_dict(note_dict, '{output_path_midi}', tempo = readtempo, time_signature = read_time_signature)\n"
            f"{indentation}\tprint('Your created Lick was longer than the harmony file! The lick was successfully created until the end of the given harmony!')\n"
            f"{indentation}\tsys.exit()\n")
    
        return trans_code, indentation_level, FUNCTION_DETECTED, PRACTICE_MODE_OFF  # Return the indented block  indented_code.strip(),
    return line, indentation_level, NO_FUNCTION_DETECTED, PRACTICE_MODE_OFF# If no match, return the original line unchanged



def removeSemicolon(line):
    if line.endswith(';'):
        line = line[:-1]
    return line
def pause(duration):
    return duration

def checkCurrentChord(line):
    if "currentChord" in line:
        line = re.sub(r'\bcurrentChord\b', 'chord_list[beat]', line)
    return line


def formatAndWriteFile(melody_path, harmony_path, output_path_midi):
    output_path = "output.py"
    add_special_foot = 0
    try:
        with open(melody_path, 'r', encoding='utf-8') as infile, open(output_path, 'w', encoding='utf-8') as outfile:
            indentation_level = 0  # Track the current indentation level
            #go through each line 
            header = {
                f"import lick_reader as lr\n"
                f"import lick_writer as lw\n"
                f"import sys\n"
                f"beat = 0\n"
                f"key_count = 0\n"
                f"midi_root_notes, chord_list, read_time_signature, readtempo = lr.harmony_processor('{harmony_path}')\n"
                f"note_dict = {{'pitch' : [], 'time' : [], 'note_duration' : [], 'volume' : [], 'chord' : [], 'pitchWheelValue' : []}}\n"
                "max_len = len(midi_root_notes)\n"
            }
            outfile.writelines(header)
            for line in infile:

                # Remove leading/trailing whitespace
                line = line.strip()  

                #remove semicolon at the end
                line = removeSemicolon(line) 

                # Adjust indentation level after '}' on the same line
                if line.startswith('}'):
                    indentation_level = max(0, indentation_level - 1)
                    line = line[1:] #remove }
                
                
                # Adjust indentation level for '{' on the same line
                if line.endswith('{'):
                    indentation_level += 1
                    line = line[:-1] #remove {

                line = checkCurrentChord(line) #replaces currentChord with proper string value and returns the whole line 

                line = add_braces_to_degree_list(line)

                # add lw. infront of function
                block_segment, indentation_level ,function_check, practice_mode_check = transform_function_call(line, indentation_level, output_path_midi)
                if (practice_mode_check == 1):
                    add_special_foot = 1
                if (function_check == FUNCTION_DETECTED): #check if the function was transformed to whole block and then write lines
                    outfile.writelines(block_segment)
                    continue #writing into file, line is done go to next line

                        
                # Check for `if`, `while`, `for`, `else`, or `elif` followed by a valid closing parenthesis
                if re.match(r'^\s*(if|while|for|else|elif)\s*(\(.*\))?\s*$', line.strip()):
                    # Add a colon only if one isn't already present
                    line = re.sub(r'(:\s*)?$', r':', line.strip())
                
                # Write the line with the current indentation level
                outfile.write('\t' * indentation_level + line + '\n')
            #check if practice mode is enabled
            if (add_special_foot == 1):
                indentation = '\t' * max(0, indentation_level)
                practice_foot = {
                    f"{indentation}key_count += 1\n"
                    f"lw.write_midi_from_dict(note_dict, '{output_path_midi}', tempo=readtempo, time_signature=read_time_signature)\n"
                    f"print('The lick was successfully created!')\n" 
                    }
                outfile.writelines(practice_foot)
            else:    
                foot = {
                    f"lw.write_midi_from_dict(note_dict, '{output_path_midi}', tempo=readtempo, time_signature=read_time_signature)\n"
                    f"print('The lick was successfully created!')\n"
                    }
                outfile.writelines(foot)


    except FileNotFoundError:
        print(f"Error: File '{melody_path}' not found.")
    except IOError as e:
        print(f"Error reading or writing file: {e}")

