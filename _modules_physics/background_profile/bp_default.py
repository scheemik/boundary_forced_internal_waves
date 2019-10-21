# Parameters and settings for the background density profile
#   Default background profile
"""
Description:

This is the default file for background profile settings for the Dedalus experiment. This file will be used when there has been no other background profile file specified.
"""

import numpy as np
# To import vertical profile helper functions
import sys
sys.path.append("../") # Adds higher directory to python modules path
import vert_profile_functs as vpf

###############################################################################
# Background profile parameters

# Number of interfaces in well-mixed layer(s) region
n       = 0                     # []
# Bottom boundary of mixed layer(s)
ml_b    = -0.30                 # [m]
# Top boundary of mixed layer(s)
ml_t    = -0.22                 # [m]
# Slope of transition between region
slope   = 200.0                 # []
# Characteristic stratification above mixed layer(s)
N_1     = 0.95                  # [rad/s]
# Characteristic stratification below mixed layer(s)
N_2     = 1.24                  # [rad/s]

###############################################################################
# Background profile function

def Repro_profile(z, n, ml_b, ml_t, slope, N_1, N_2):
    """
    A function to reproduce the vertical density profiles of Ghaemsaidi et al. 2016
    z       = array of vertical values from z_b to z_t
    n       = number of interfaces in well-mixed layer
    ml_b    = bottom of mixed layer
    ml_t    = top of mixed layer
    slope   = slope of tanh functions
    N_1     = value
    """
    # initialize array of values to be returned
    values = 0*z
    # Add upper stratification
    values += vpf.tanh_(z, N_1, slope, ml_t)
    # Add lower stratification
    values += vpf.tanh_(z, N_2, -slope, ml_b)
    # Find height of staircase region
    H = ml_t - ml_b
    # If there are steps to be added...
    if (n > 0):
        # calculate height of steps
        height = H / float(n)
        # calculate height of pseudo delta bumps as midpoint between N1 and N2
        bump_h = max(N_1, N_2) - 0.5*abs(N_1-N_2)
        for i in range(n):
            c_i = z_b + (height/2.0 + i*height)
            values += vpf.tanh_bump(z, bump_h, slope, c_i, 0.05)
    return values

def build_bp_array(z):
    BP_array = Repro_profile(z, n, ml_b, ml_t, slope, N_1, N_2)
    return BP_array
