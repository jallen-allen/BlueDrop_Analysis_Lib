import os
import numpy as np
import pandas as pd
import shutil
import sys
from lib.general_functions.global_constants import GRAVITY_CONST

# File Purpose: Store general purpose functions - I will organize this better later
def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder '{folder_path}' created successfully.")
    else:
        print(f"Folder '{folder_path}' already exists.")

def apply_mask_to_list(values, mask):
    return [value for value, m in zip(values, mask) if m]

def progress_bar(iterations, total, time_left):
    progress = iterations / total
    bar_length = 50
    completed_length = int(bar_length * progress)
    remaining_length = bar_length - completed_length

    bar = "[" + "=" * completed_length + "-" * remaining_length + "]"
    percentage = "{:.2%}".format(progress)
    time_est = "{:.2}".format(time_left/60)
    sys.stdout.write("\r" + bar + " " + percentage + " ETA (min): " + time_est)
    sys.stdout.flush()

def convert_time_units(val, input_unit, output_unit):
    #Purpose: Convert one time unit to another
    # Fist convert everything to seconds
    input_to_standard = {
        "min" : 60.0,
        "hour": 3600.0,
        "s"   : 1.0
    }
    
    standard_to_output = {
        "min" : 1/input_to_standard["min"],
        "hour": 1/input_to_standard["hour"],
        "s"   : input_to_standard["s"]
    }
    
    # Convert the val to seconds (s)
    standard = val * input_to_standard[input_unit]
    # Convert the standard value to the desired value
    output_val = standard * standard_to_output[output_unit]
    
    return output_val

def convert_accel_units(val, input_unit, output_unit):
    # Purpose: Convert one acceleration unit to another
    # First convert everything to m/s^2
    input_to_standard ={
        "g": GRAVITY_CONST,
        "m/s^2":1
    }
    standard_to_output = {
        "g": 1/GRAVITY_CONST,
        "m/s^2":1
    }
    
    # Convert the val to m/s^2 (standard value)
    standard = val * input_to_standard[input_unit]
    # Convert the standard value to the desired value
    output_val = standard * standard_to_output[output_unit]
    # Return the value
    return output_val

def convert_length_units(val, input_unit, output_unit):
    # Purpose: Convert one length unit to another

    input_to_standard = {
        "cm":1e-2,
        "mm":1e-3,
        "m" : 1.0
    }
    standard_to_output = {
        "cm":1/input_to_standard["cm"],
        "mm":1/input_to_standard["mm"],
        "m" :1/input_to_standard["m"]
    }

    # Convert the val to standard value
    standard = val * input_to_standard[input_unit]

    # Conver the standard valuye to the desired output
    output_val = standard * standard_to_output[output_unit]

    return output_val
