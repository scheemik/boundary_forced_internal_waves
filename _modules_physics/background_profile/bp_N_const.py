# Parameters and settings for the background density profile
#   Constant background profile
"""
Description:

This a file of background profile settings for the Dedalus experiment. This file will create a constant stratification of a specified value. That is, N will be constant in z
"""

import numpy as np
# To import vertical profile helper functions
import sys
sys.path.append("../") # Adds higher directory to python modules path
p_module_dir = './_modules_physics/'
# To get the characteristic stratification from the boundary forcing file
sys.path.insert(0, p_module_dir)
import boundary_forcing as bf

###############################################################################
# Background profile parameters

# The value of the constant stratification
N_0     = bf.N_0        # [rad s^-1]

###############################################################################
# Background profile function

def build_bp_array(z):
    BP_array = z*0.0 + N_0
    return BP_array
