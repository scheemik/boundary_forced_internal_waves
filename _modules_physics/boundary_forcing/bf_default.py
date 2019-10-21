# Parameters and settings for boundary forcing
#   Default boundary forcing
"""
Description:

This is the default file for boundary forcing settings for the Dedalus experiment. This file will be used when there has been no other boundary forcing file specified.
"""

import numpy as np
# To import the switchboard
import sys
sys.path.append("..") # Adds higher directory to python modules path
import switchboard as sbp

###############################################################################
# Boundary forcing parameters

# Non-linear system of 3 equations with 6 unknowns, need to specify 3:
# 1. Characteristic stratification (eventually from the background profile)
N_0     = 1.0                   # [rad/s]
# 2. Characteristic wavenumber
k       = 45                    # [m^-1]
# 3. Oscillation frequency
omega   = 0.7071                # [rad s^-1]
# Use the equations given in Cushman-Roisin and Beckers ch 13 for the rest:
# 4. Angle of beam w.r.t. the horizontal (eq 13.6, dispersion relation)
theta   = np.arccos(omega/N_0)  # [rad]
# 5. Horizontal wavenumber = k*cos(\theta)
k_x     = k*omega/N_0           # [m^-1]
# 6. Vertical wavenumber
k_z     = k*np.sin(theta)       # [m^-1]

# Other parameters specified by relations
# Horizontal wavelength
lam_x   = 2*np.pi / k_x         # [m]
# Oscillation period = 2pi / omega
T       = 2*np.pi / omega       # [s]

###############################################################################
# Dedalus syntax substitutions for spatial window and temporal ramp
#window    = "1" # effectively, no window
window    = "(1/2)*(tanh(slope*(x-left_edge))+1)*(1/2)*(tanh(slope*(-x+right_edge))+1)"
ramp      = "(1/2)*(tanh(4*t/(nT*T) - 2) + 1)"
# Forcing amplitude modifier
A         = 2.0e-4
# Forcing amplitude ramp (number of oscillations)
nT        = 3.0
# Slope of window edges
bf_slope  = 35
# Number of horizontal wavelengths that fit into the window
win_lams  = 1
# Width of window
win_width = lam_x * win_lams
# Check if 1/2 window width fits to the left of display domain
Dis_buff_x= sbp.Dis_buff_x
if (0.5 * win_width < Dis_buff_x):
    # It will fit, put 1/2 on left, 1/2 on right
    x_sim_0  = sbp.x_sim_0
    bfl_edge = x_sim_0 - lam_x/2.0
    bfr_edge = x_sim_0 + lam_x/2.0
else:
    # It will not fit, put as far left as possible
    x_0      = sbp.x_0
    bfl_edge = x_0
    bfr_edge = x_0 + lam_x

###############################################################################
# Polarization relation from Cushman-Roisin and Beckers eq (13.7)
#   (signs implemented in substitutions below)
PolRel = {'u': A*(sbp.g*omega*k_z)/(N_0**2*k_x),
          'w': A*(sbp.g*omega)/(N_0**2),
          'b': A*sbp.g}
          #'p': A*(g*(omega**2)*kz)/((N0**2)*(kx**2))}
          #'p': A*(g*rho_0*kz)/(kx**2+kz**2)} # relation for p not used

###############################################################################
# Substitutions for boundary forcing (see C-R & B eq 13.7)
fu      = "-BFu*sin(kx*x + kz*z - omega*t)*window*ramp"
fw      = " BFw*sin(kx*x + kz*z - omega*t)*window*ramp"
fb      = "-BFb*cos(kx*x + kz*z - omega*t)*window*ramp"
fp      = "-BFp*sin(kx*x + kz*z - omega*t)*window*ramp"
