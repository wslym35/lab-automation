# -*- coding: utf-8 -*-
"""
Created on Tue Feb 17 10:31:33 2026

@author: Wesley Mills 
"""
from LightFieldControls import LightField 
# If this fails to import, make sure your current working directory (top right corner in Spyder) is Desktop/code
#import os # to save files using os.getcwd() 

lf_params = {'experiment_name' : 'LEDs', # This is the only required parameter to initial a LightField experiment 
             'exposure_time' : 50.0, # Note that you need to use floating points, not integers, for all numeric values
             'center_wavelength': 540.0, 
             'grating': '[500nm,300][0][0]'}  

lf = LightField(lf_params) 

dir(lf) 