# -*- coding: utf-8 -*-
"""
Created on Thu Feb 19 10:04:23 2026

@author: Wesley Mills 
"""

# List of wavelength ranges at various spectrometer center wavelelngths 
# This file is imported into LightFieldControls and used to generate wavelength labels for the output csv files 
# To add a new center wavelength, 
    # (1) get the first and last wavelengths from the GUI 
    # (2) use those as the np.linspace arguments 
# Please use the same formatting, i.e., 
    # "XXX" : np.linspace(first, last, 1024), # Last updated
    # XXXX is the spectrometer center wavelength in nm 
    # Last updated is the data you last updated the array 
# If you re-do the spectrometer callibration, you'll need to update the arrays in this file 

import numpy as np 

wavelength_ranges = {'0' : np.linspace(-66.303, +65.851, 1024), # 2026-02-19
                     "1080" : np.linspace(1016.182, 1143.160, 1024), # 2026-02-19
                     "540" : np.linspace(474.714, 604.729, 1024) # 2026-02-19
                     }