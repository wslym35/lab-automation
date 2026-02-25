# -*- coding: utf-8 -*-
"""
Created on Tue Feb 17 10:31:33 2026

@author: Wesley Mills 
"""
###############################################################################
# The following imports allow you to use the lab controls in any Python script 
import sys 

sys.path.append(r"C:\Users\schul\OneDrive\Desktop\code")

from LightFieldControls import LightField 
from KinesisControls import (K10CR2, PRMTZ8) 
from PowerMeterControls import PM100D 
###############################################################################

def setup(lf_params):
    # Launch an instance of lightfield 
    lf = LightField(lf_params) 
    
    # Connect to the half-wave plate (number is serial number) 
    hwp = K10CR2('55535784') 
    hwp.connect() 
    
    # Connect to the analyzing polarizer (number is serial number) 
    analyzer = K10CR2('55536784')
    analyzer.connect() 
    
    # Connect to the mirror rotation stage (number is KCube serial number) 
    mirror = PRMTZ8('27270898') 
    mirror.connect()
    
    # Connect to the power meter 
    PM = PM100D('USB0::4883::32888::P0007396::0::INSTR') 
    
    # Home the rotation mounts 
    hwp.home() 
    analyzer.home() 
    mirror.home() 
    
    return lf, analyzer, hwp, mirror, PM 

def experiment():
    hwp.move_to(6)
    analyzer.move_to(112) 
    mirror.move_to(0) 
    lf.set_exposure_time(100) 
    lf.acquire_as_csv('test-file-name', r"C:\Users\schul\OneDrive\Desktop\data\misc") 
    

def finish(): 
    # Call this function this when the experiment is done 
    hwp.disconnect()
    analyzer.disconnect() 
    PM.disconnect() 
    lf.close()


lf_params = {'experiment_name' : 'LEDs', # This is the only required parameter to initial a LightField experiment 
             # These are all optional 
             #'exposure_time' : 50.0, # Note that you need to use floating points, not integers, for all numeric values
             #'center_wavelength': 540.0, 
             #'grating': '[500nm,300][0][0]'
             }  


lf, analyzer, hwp, mirror, PM = setup(lf_params) 
input("Now you can do your experiment")
experiment() 
finish() 


