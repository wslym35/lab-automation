# -*- coding: utf-8 -*-
"""
Created on Fri Feb 13 10:14:19 2026

@author: Wes 
"""

import clr 
import sys 
import os
#from System.IO import *
from System import String
from System.Collections.Generic import List

sys.path.append(os.environ['LIGHTFIELD_ROOT'])
sys.path.append(os.environ['LIGHTFIELD_ROOT']+'\\AddInViews')
clr.AddReference("PrincetonInstruments.LightFieldViewV4")
clr.AddReference("PrincetonInstruments.LightField.AutomationV4")
clr.AddReference("PrincetonInstruments.LightFieldAddInSupportServices")

from PrincetonInstruments.LightField.Automation import Automation
from PrincetonInstruments.LightField.AddIns import CameraSettings
#from PrincetonInstruments.LightField.AddIns import ExperimentSettings
from PrincetonInstruments.LightField.AddIns import SpectrometerSettings
from PrincetonInstruments.LightField.AddIns import DeviceType 

# =============================================================================
# auto = Automation(True, List[String]()) 
# # First parameter is whether or not to display LightField GUI
# # Second parameter forces LF to load with no experiment 
# 
# experiment = auto.LightFieldApplication.Experiment 
# experiment.Load("LEDs")   # Or desired experiment name 
# 
# if (camera_found()==True):
#     # Set exposure time 
#     set_value(CameraSettings.ShutterTimingExposureTime, 20.0) 
#     
#     experiment.Acquire() 
# ============================================================================= 
    
class LightField:
    # Params is a dict of values used to set up LightField 
    def __init__(self, params):
        # Launch LightField and set initial parameters 
        lf = Automation(True, List[String]())
        # First parameter is whether or not to display LightField GUI
        # Second parameter forces LF to load with no experiment 
        self.experiment = lf.LightFieldApplication.Experiment
        self.experiment.Load(params['experiment_name'])
        
        self.set_exposure_time(params['exposure_time'])
        self.set_center_wavelength(params['center_wavelength'])
        self.set_grating(params['grating']) 
        
        # Check that temp is locked and everything else is correct 
        input('Please check that: \n' +
              '(1) The camera and the spectrometer are connected in the Devices tab \n' + 
              '(2) The aquisition time units are ms \n' + 
              '(3) The temperature is locked at -70 C \n' + 
              '\n Press [Enter] when ready to proceed')
    
    def set_value(self, setting, value):
        # Check for existence before setting
        if self.experiment.Exists(setting):
            self.experiment.SetValue(setting, value)
        else:
            print("That setting doesn\'t exist")
    
    def set_exposure_time(self, time):
        if self.camera_found():  
            self.set_value(CameraSettings.ShutterTimingExposureTime, time) 
    
    def set_center_wavelength(self, wavelength):
        if self.spectrometer_found(): 
            self.set_value(SpectrometerSettings.GratingCenterWavelength, wavelength)
    
    def set_grating(self, grating):
        print("Need to write set_grating method") 

    def camera_found(self):
        # Check if a camera is connected 
        for device in self.experiment.ExperimentDevices: 
            if (device.Type == DeviceType.Camera):
                return True 
        # If connected device is not a camera, inform the user 
        print("Camera not found. Please add a camera and try again.") 
        return False 
    
    def spectrometer_found(self):
        # Check is a spectrometer is connected 
        for device in  self.experiment.ExperimentDevices: 
            if (device.Type == DeviceType.Spectrometer):
                return True 
        print('Spectrometer not found. Please add a spectrometer and try again.') 
        return False 
    
    # Acquire background 
    
    # Acquire and save image as csv (maybe make this two seperate methods?) 
    
    # Exit/close LightField 
    