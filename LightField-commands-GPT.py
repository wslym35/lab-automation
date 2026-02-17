import sys
import os
import clr
import time

# ----------------------------------------------------------------------
# 1. Add LightField paths (edit if needed)
# ----------------------------------------------------------------------
LIGHTFIELD_ROOT = r"C:\Program Files\Princeton Instruments\LightField"

sys.path.append(LIGHTFIELD_ROOT)
sys.path.append(os.path.join(LIGHTFIELD_ROOT, "AddInViews"))

# ----------------------------------------------------------------------
# 2. Load .NET assemblies
# ----------------------------------------------------------------------
clr.AddReference("PrincetonInstruments.LightField.AutomationV4")
clr.AddReference("PrincetonInstruments.LightFieldViewV4")

from PrincetonInstruments.LightField.Automation import Automation
from PrincetonInstruments.LightField.AddIns import ExperimentSettings
from System.Collections.Generic import List 
from System import String 

# ----------------------------------------------------------------------
# 3. Launch LightField
# ----------------------------------------------------------------------
print("Starting LightField...") 
args = List[String]()   # Required .NET string list
auto = Automation(True, args)  # True = show GUI

experiment = auto.LightFieldApplication.Experiment

# ----------------------------------------------------------------------
# 4. Load an existing experiment
# ----------------------------------------------------------------------
experiment.Load("MyExperiment")   # <-- change to your experiment name

# ----------------------------------------------------------------------
# 5. Set file saving options
# ----------------------------------------------------------------------
save_directory = r"C:\Data"
base_filename = "test_capture"

experiment.SetValue(
    ExperimentSettings.FileNameGenerationDirectory,
    save_directory
)

experiment.SetValue(
    ExperimentSettings.FileNameGenerationBaseFileName,
    base_filename
)

# Optional: ensure unique filenames
experiment.SetValue(
    ExperimentSettings.FileNameGenerationAttachDate,
    True
)

# ----------------------------------------------------------------------
# 6. Acquire one frame
# ----------------------------------------------------------------------
print("Acquiring frame...")
experiment.Acquire()

# Wait for acquisition to finish
while experiment.IsRunning:
    time.sleep(0.1)

print("Acquisition complete.")

# ----------------------------------------------------------------------
# 7. Shutdown (optional)
# ----------------------------------------------------------------------
# auto.Dispose()   # Uncomment if you want LightField to close

print("Done.")
