# Parameters and settings for the sponge layer profile
#   Default sponge layer profile
"""
Description:

This is the default file for sponge layer settings for the Dedalus experiment. This file will be used when there has been no other sponge layer file specified.
"""

import numpy as np
# To import vertical profile helper functions
import sys
sys.path.append("../") # Adds higher directory to python modules path
import vert_profile_functs as vpf
import switchboard as sbp

###############################################################################
# Sponge layer parameters

# Bottom boundary of sponge layer
z_sl_bot        = sbp.z_sim_f               # [m]
# Thickness of sponge layer
sl_thickness    = 0.2                       # [m]
# Top boundary of sponge layer
z_sl_top        = z_sl_bot + sl_thickness   # [m]
# Slope of sponge layer ramp
slope           = 40.0                      # []
# Maximum coefficient ramped to at end of sponge layer
max_coeff       = 20                        # []

###############################################################################
# Sponge layer function

def bottom_sponge(z, z_sl_bot, z_sl_top, slope, max_coeff):
    # initialize array of values to be returned
    values = 0*z
    # Find height of sponge layer
    H = abs(z_sl_top - z_sl_bot)
    # Find 2/3 down the sponge layer
    sp_c = z_sl_top - 2.0*H/3.0
    # Add upper stratification
    values += 1 + vpf.tanh_(z, max_coeff-1, -slope, sp_c)
    return values

def build_sl_array2(z):
    SL_array = z*0.0 + 1.0
    return SL_array

def build_sl_array(z):
    SL_array = bottom_sponge(z, z_sl_bot, z_sl_top, slope, max_coeff)
    return SL_array
