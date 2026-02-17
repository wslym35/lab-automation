# -*- coding: utf-8 -*-
"""
Created on Tue Feb 17 10:31:33 2026

@author: Wes 
"""
from LightFieldControls import LightField 
# If this fails to import, make sure your current working directory (top right corner in Spyder) is Desktop/code

lf_params = {'experiment_name' : 'LEDs', 
             'exposure_time' : 50.0, 
             'center_wavelength': 0.0, 
             'grating': 0.0} # Note that you need to use floating points, not integers, for all numeric values 

lf = LightField(lf_params) 
