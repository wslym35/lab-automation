# -*- coding: utf-8 -*-
"""
Created on Fri Feb 13 10:14:19 2026

@author: schul

Works as of 2026-02-17
- Wes 
"""

import clr 
import sys 
import os
from System.IO import * 
from System import String
from System.Collections.Generic import List 

#LIGHTFIELD_ROOT = r"C:\Program Files\Princeton Instruments\LightField"

sys.path.append(os.environ['LIGHTFIELD_ROOT'])
sys.path.append(os.environ['LIGHTFIELD_ROOT']+'\\AddInViews')
clr.AddReference("PrincetonInstruments.LightFieldViewV4")
clr.AddReference("PrincetonInstruments.LightField.AutomationV4")
clr.AddReference("PrincetonInstruments.LightFieldAddInSupportServices")

from PrincetonInstruments.LightField.Automation import Automation
from PrincetonInstruments.LightField.AddIns import CameraSettings
from PrincetonInstruments.LightField.AddIns import DeviceType 

def set_value(setting, value):
    # Check for existence before setting
    if experiment.Exists(setting):
        experiment.SetValue(setting, value)

def camera_found():
    # Check if a camera is connected 
    for device in experiment.ExperimentDevices: 
        if (device.Type == DeviceType.Camera):
            return True 
    # If connected device is not a camera, inform the user 
    print("Camera not found. Please add a camera and try again.") 
    return False 

auto = Automation(True, List[String]()) 
# First parameter is whether or not to display LightField GUI
# Second parameter forces LF to load with no experiment 

experiment = auto.LightFieldApplication.Experiment 
experiment.Load("LEDs")   # Or desired experiment name 

if (camera_found()==True):
    # Set exposure time 
    set_value(CameraSettings.ShutterTimingExposureTime, 20.0) 
    
    experiment.Acquire() 

# Probably what I want to do is define some functions to be imported & used in another module
# def load_LightField(lf_params <dict>): a function that loads the right experiment with the right settings and returns something you can interface with later 
# def save_image(): 
    
    