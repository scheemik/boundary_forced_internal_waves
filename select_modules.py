# Module selection for Dedalus experiment
"""
Description:

This file contains the selection of the physics modules for this experiment. Based on the selected modules, this script will move and rename the relevant files before the experiment is executed, if needed.
"""

import numpy as np

###############################################################################
# Select physics modules

# Boundary forcing
bf_module       = 'bf_default'
# Background profile
bp_module       = 'bp_default'
# Sponge layer
sl_module       = 'sl_default'

###############################################################################
################    Shouldn't need to edit below here    #####################
###############################################################################
# Imports for preparing physics modules
from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
from shutil import copy2, rmtree
import os

def add_p_module(p_module_dir, p_module, module_name_str):
    # Move the physics module file up one directory level
    pm_path = p_module_dir + module_name_str + '/' + p_module + '.py'
    if os.path.isfile(pm_path):
        copy2(pm_path, p_module_dir + module_name_str + '.py')
        print('Using ' + p_module + '.py')
    # else:
    #     print(p_module + '.py not found. Was it selected previously?')

# If this is the root thread, then do all this stuff
if rank==0:
    print('Preparing physics modules')
    print('')
    # Add path to _modules-physics so python knows to look there on imports
    import sys
    p_module_dir = './_modules_physics/'

    add_p_module(p_module_dir, bf_module, 'boundary_forcing')
    add_p_module(p_module_dir, bp_module, 'background_profile')
    add_p_module(p_module_dir, sl_module, 'sponge_layer')

###############################################################################
# Cleaning up the _modules-physics directory tree
    for some_dir in os.scandir(p_module_dir):
        # Iterate through subdirectories in _modules-physics
        if some_dir.is_dir():
            dir=some_dir.name
            # If the directory isn't __pycache__, then delete it
            if dir!='__pycache__':
                dir_path = p_module_dir + dir
                rmtree(dir_path, ignore_errors=True)
