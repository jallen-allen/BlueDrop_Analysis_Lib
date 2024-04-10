import numpy as np
import pandas as pd
import os
import shutil
import time 

from lib.data_classes.folder import Folder
from lib.data_classes.pffpFile import pffpFile
from lib.general_functions.general_function import create_folder_if_not_exists, progress_bar
class pffpDataFolder(Folder):
    # Pupose: Hold data about a folder that contains a PFFP data

    # Init the input params and store them in DataFolder Instance
    def __init__(self, folder_dir, pffp_id, calibration_factor_dir):
        # init the parent class
        Folder.__init__(self, folder_dir)

        self.folder_dir = folder_dir # Store the folder directory
        self.pffp_id = pffp_id       # Store the PFFP id
        self.calibration_factor_dir = calibration_factor_dir # Directory containing the calibration factors for the PFFP

        # Init variables that aren't defined
        self.num_pffp_files = "Not set"
        self.datetime_range = "Not set"
        self.calibration_excel_sheet = None
        self.calibration_params = None
        self.num_drop_files = "Not Set"

    def __str__(self):
        return f"Folder: {self.folder_dir} \nDate range: {self.datetime_range} \nPFFP id: {self.pffp_id} \
                \nCalibration Param dir: {self.calibration_factor_dir} \nNum .bin files: {self.num_pffp_files} \
                \nNum files with drops: {self.num_drop_files}"
    
    def read_calibration_excel_sheet(self):
        # Purpose: Read the calibartion data for specified pffp id
        sheet_name = "bluedrop_" + str(self.pffp_id)

        self.calibration_excel_sheet = pd.read_excel(self.calibration_factor_dir, sheet_name)

    def get_sensor_calibration_params(self, date_string):
        # Purpose: Retrieve the possible calibration dates for the selected sheet

        # temp storage of the data
        data = self.calibration_excel_sheet

        if type(data) is not pd.DataFrame:
            raise IndexError("Calibration data must be read first")
        
        # Construct the column headers
        offset_string = date_string + "_offset"
        scale_string  = date_string + "_scale"
        
        # Select those columns of the df
        self.calibration_params = data[["Sensor", offset_string, scale_string]]

    def store_pffp_files(self, recursive = False, subfolder = ""):
        # Purpose: Store the binary files in the 
        binary_file_dirs = self.get_directories_by_extension("bin", recursive, subfolder)

        # init list to hold pffp files
        self.pffp_files = []

        # Check that the calibration params have been read
        if  type(self.calibration_params) is not pd.DataFrame:
            raise IndexError("Calibration data must be read first")
        
        # Loop over binary file directories and create instance of the pffpFile class
        for file_dir in binary_file_dirs: 
            # add the pffpFile to the list
            self.pffp_files.append(pffpFile(file_dir, self.calibration_params))

        self.num_pffp_files = len(self.pffp_files)

    def analyze_all_files(self, subfolder_dir = "no_drop_folder", use_pore_pressure = True, store_df = True ):
        # Purpose: Get the files that have drops in them

        # store_drop_df: Store the df if it's a drop

        # Init list to store the pffp files that contain drops and variable to store the number of files that contain drops
        self.pffp_drop_files = []
        self.pffp_no_drop_files = []
        self.pffp_funky_files = []

        self.num_drop_files = 0
        self.num_funky_files = 0

        full_subfolder_dir = os.path.join(self.folder_dir, subfolder_dir)
        funky_dir = os.path.join(self.folder_dir, "funky")

        # Try to create the subfolder
        create_folder_if_not_exists(full_subfolder_dir)

        create_folder_if_not_exists(funky_dir)

        # Print progress bar label
        print("\nProgress analysing drops...")

        for i, file in enumerate(self.pffp_files):
            
            # Get an estimate for how much longer is left
            start_time= time.time()

            # Get the number of drops in the pffp file
            file.analyze_file_for_drop_info(use_pore_pressure, store_df = store_df)

            # Check if there's a drop in the file and append to the mask arr
            drop_in_file = file.check_drop_in_file()

            if not drop_in_file:
                updated_file_dir = os.path.join(full_subfolder_dir, file.file_name)

                # Check if the file already in the directory
                if not os.path.exists(updated_file_dir):
                    # If it doesn't move and update the file
                    # Move the file into a subdirectory
                    shutil.move(file.file_dir, full_subfolder_dir)

                    # Update the folder dir
                    file.file_dir = updated_file_dir

                # Add the file to the no drop directory
                self.pffp_no_drop_files.append(file)
            else:
                

                # Check if the file is funky
                if file.funky:
                    funky_file_dir = os.path.join(funky_dir, file.file_name)
                    
                    shutil.move(file.file_dir, funky_dir)

                    file.file_dir = funky_file_dir

                    self.pffp_funky_files.append(file)
                    self.num_funky_files +=1
                else:
                    # Store the drop files
                    self.pffp_drop_files.append(file)

                    # Increment the number of files with drops
                    self.num_drop_files +=1
            
            end_time= time.time()

            time_left = (end_time - start_time) * (self.num_pffp_files - (i+1))
            
            # Print a progress bar
            progress_bar(i+1, self.num_pffp_files, time_left)

        print("\nInitial analysis complete!")      

    def get_file_index_from_name(self):
        # TODO: Purpose: Given a file name get the index of that file in
            #  pffp_files list
            # pffp_no_drop list or pffp_drop list depending on where it is
        pass

