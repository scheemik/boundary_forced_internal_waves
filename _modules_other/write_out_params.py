"""
If the keep (-k) option is set to 1, this script will write out
parameters of the experiment to the relevant log file

Usage:
    write_out_params.py NAME

Options:
    NAME	            # -n, Name of simulation run

"""

import sys
import numpy as np
# For adding arguments when running
from docopt import docopt

###############################################################################

# Read in parameters from docopt
if __name__ == '__main__':
    arguments = docopt(__doc__)
    NAME = str(arguments['NAME'])

###############################################################################
# Fetch parameters from switchboard file

import sys
switch_path = "../" + NAME
sys.path.insert(0, switch_path) # Adds higher directory to python modules path
import switchboard as sbp

# Grid resolution
nx      = int(sbp.n_x)
nz      = int(sbp.n_z)
# Domain size
Lx      = float(sbp.L_x)
Lz      = float(sbp.L_z) # not including the sponge layer
# Timing of simulation
use_sst = sbp.use_stop_sim_time
stop_t  = sbp.stop_sim_time
if use_sst==False:
    sim_period_stop  = sbp.stop_n_periods

# Characteristic stratification [rad/s]
N0     = float(sbp.N_0)
# Wavenumber
k      = float(sbp.k)
# Forcing oscillation frequency
omega  = float(sbp.omega)
# Angle of beam w.r.t. the horizontal
theta  = float(sbp.theta)
# Oscillation period = 2pi / omega
T      = float(sbp.T)
# Forcing amplitude modifier
A      = float(sbp.A)
# Horizontal wavelength
lam_x  = sbp.lam_x

###############################################################################
# Write out to file

# Name of log file
logfile = '../' + NAME + '/LOG_' + NAME + '.txt'
# Write params to log file
with open(logfile, 'a') as the_file:
    the_file.write('--Simulation Parameters--\n')
    the_file.write('\n')
    the_file.write('Horizontal grid points:       n_x = ' + str(nx) + '\n')
    the_file.write('Vertical   grid points:       n_z = ' + str(nz) + '\n')
    the_file.write('\n')
    if use_sst==False:
        the_file.write('Sim Runtime (periods):              ' + str(sim_period_stop) + '\n')
    the_file.write('Sim Runtime (seconds):              ' + str(stop_t) + '\n')
    the_file.write('\n')
    the_file.write('--Simulation Domain Parameters--\n')
    the_file.write('\n')
    the_file.write('Horizontal extent (m):        L_x = ' + str(Lx) + '\n')
    the_file.write('Vertical   extent (m):        L_z = ' + str(Lz) + '\n')
    the_file.write('\n')
    the_file.write('--Boundary Forcing Parameters--\n')
    the_file.write('\n')
    the_file.write('Characteristic wavenumber:      k = ' + str(k) + '\n')
    the_file.write('\n')
    the_file.write('Forcing frequency (s^-1):   omega = ' + str(omega) + '\n')
    the_file.write('Forcing angle (rad):        theta = ' + str(theta) + '\n')
    the_file.write('Forcing angle (deg):        theta = ' + str(theta*180/np.pi) + '\n')
    the_file.write('\n')
    the_file.write('Forcing period (s):             T = ' + str(T) + '\n')
    the_file.write('Forcing amplitude:              A = ' + str(A) + '\n')
    the_file.write('\n')
    the_file.write('Horizontal wavelength (m):  lam_x = ' + str(lam_x) + '\n')
