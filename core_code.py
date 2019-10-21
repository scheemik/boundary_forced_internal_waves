"""
Core code of Dedalus script

Modified by Mikhail Schee from the script for 2D Rayleigh-Benard convection in the Dedalus example files.

This script is NOT meant to be run directly.

The parameters of an experiment are controlled through the switchboard file.
To start a new experiment, run the `make_new_exp.sh` script using the `-n` flag to specify the experiment's name and the `-s` flag to specify the switchboard file.
    $ sh make_new_exp.sh -n my_new_exp -s switchboard-default.py

This will create a new directory for your experiment under `_experiments`. Edit the switchboard file in that directory to specify the parameters of the experiment before running.

To run an experiment, run the `run.sh` script with the `-n`, `-c`, `-l`, `-v` flags, as specified in that script's header. Running an experiment again will overwrite the old outputs.
    $ sh run.sh -n my_new_exp -c 2 -l 1 -v 1

---
This script can restart the simulation from the last save of the original
output to extend the integration.  This requires that the output files from
the original simulation are merged, and the last is symlinked or copied to
`restart.h5`.

To run the original example and the restart, you could use:
    $ mpiexec -n 4 python3 rayleigh_benard.py
    $ mpiexec -n 4 python3 -m dedalus merge_procs snapshots
    $ ln -s snapshots/snapshots_s2.h5 restart.h5
    $ mpiexec -n 4 python3 rayleigh_benard.py

The simulations should take a few process-minutes to run.

"""

import numpy as np
from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()

import time
import pathlib

from dedalus import public as de
from dedalus.extras import flow_tools

import logging
logger = logging.getLogger(__name__)

###############################################################################
# Checking command line arguments
import sys
# Arguments must be passed in the correct order
arg_array = sys.argv
filename = str(arg_array[0])
switchboard = str(arg_array[1])

if rank==0:
    # Check number of arguments passed in
    if (len(arg_array) != 2):
        print("Wrong number of arguments passed to core code")
        print("")
    #print('Core code filename:', filename)
    #print('Using switchboard:', switchboard)
    #print("")

###############################################################################
# Import SwitchBoard Parameters (sbp)
#   This also runs the switchboard file, which will move files around
import switchboard as sbp

# Call parameters by sbp.some_param. For example:
nx = sbp.n_x #256
nz = sbp.n_z #64

###############################################################################
# Create bases and domain
x_basis = de.Fourier('x',   nx, interval=(sbp.x_sim_0, sbp.x_sim_f), dealias=sbp.dealias)
z_basis = de.Chebyshev('z', nz, interval=(sbp.z_sim_f, sbp.z_sim_0), dealias=sbp.dealias)
domain = de.Domain([x_basis, z_basis], grid_dtype=np.float64)
# Get x and z grids into variables. Used for BP and initial conditions
x = domain.grid(0)
z = domain.grid(1)

###############################################################################
# 2D Boussinesq hydrodynamics
problem = de.IVP(domain, variables=['p','b','u','w','bz','uz','wz'])
# From Nico: all variables are dirchlet by default, so only need to
#   specify those that are not dirchlet (variables w/o top & bottom bc's)
problem.meta['p','bz','uz','wz']['z']['dirichlet'] = False
# Parameters for the equations of motion
problem.parameters['NU'] = sbp.nu
problem.parameters['KA'] = sbp.kappa
problem.parameters['N0'] = sbp.N_0

###############################################################################
# Forcing from the boundary

# Polarization relation from boundary forcing file
PolRel = sbp.PolRel
# Creating forcing amplitudes
for fld in ['u', 'w', 'b']:#, 'p']:
    BF = domain.new_field()
    BF.meta['x']['constant'] = True  # means the NCC is constant along x
    BF['g'] = PolRel[fld]
    problem.parameters['BF' + fld] = BF  # pass function in as a parameter.
    del BF
# Parameters for boundary forcing
problem.parameters['kx']        = sbp.k_x
problem.parameters['kz']        = sbp.k_z
problem.parameters['omega']     = sbp.omega
problem.parameters['grav']      = sbp.g # can't use 'g': Dedalus uses that for grid
problem.parameters['T']         = sbp.T # [s] period of oscillation
problem.parameters['nT']        = sbp.nT # number of periods for the ramp
# Spatial window and temporal ramp for boundary forcing
problem.parameters['slope']     = sbp.bf_slope
problem.parameters['left_edge'] = sbp.bfl_edge
problem.parameters['right_edge']= sbp.bfr_edge
problem.substitutions['window'] = sbp.window
problem.substitutions['ramp']   = sbp.ramp
# Substitutions for boundary forcing (see C-R & B eq 13.7)
problem.substitutions['fu']     = sbp.fu
problem.substitutions['fw']     = sbp.fw
problem.substitutions['fb']     = sbp.fb
#problem.substitutions['fp']     = sbp.fp

###############################################################################
# Sponge Layer (SL) as an NCC
SL = domain.new_field()
SL.meta['x']['constant'] = True  # means the NCC is constant along x
SL_array = sbp.build_sl_array(z)
SL['g'] = SL_array
problem.parameters['SL'] = SL

###############################################################################
# Background Profile (BP) as an NCC
BP = domain.new_field()
BP.meta['x']['constant'] = True  # means the NCC is constant along x
BP_array = sbp.build_bp_array(z)
BP['g'] = BP_array
problem.parameters['BP'] = BP

###############################################################################
# Equations of motion (non-linear terms on RHS)
#   Mass conservation equation
problem.add_equation("dx(u) + wz = 0")
#   Equation of state (in terms of buoyancy)
problem.add_equation("dt(b) - KA*(dx(dx(b)) + dz(bz))"
                    + "= -((N0*BP)**2)*w - (u*dx(b) + w*bz)")
#   Horizontal momentum equation
problem.add_equation("dt(u) -SL*NU*dx(dx(u)) - NU*dz(uz) + dx(p)"
                    + "= - (u*dx(u) + w*uz)")
#   Vertical momentum equation
problem.add_equation("dt(w) -SL*NU*dx(dx(w)) - NU*dz(wz) + dz(p) - b"
                    + "= - (u*dx(w) + w*wz)")
# Required for solving differential equations in Chebyshev dimension
problem.add_equation("bz - dz(b) = 0")
problem.add_equation("uz - dz(u) = 0")
problem.add_equation("wz - dz(w) = 0")

###############################################################################
# Boundary contitions
#	Using Fourier basis for x automatically enforces periodic bc's
#   Left is bottom, right is top
# Solid top/bottom boundaries
problem.add_bc("left(u) = 0")
problem.add_bc("right(u) = right(fu)")
# Free top/bottom boundaries
#problem.add_bc("left(uz) = 0")
#problem.add_bc("right(uz) = 0")
# No-slip top/bottom boundaries?
problem.add_bc("left(w) = 0", condition="(nx != 0)") # redunant in constant mode (nx==0)
problem.add_bc("right(w) = right(fw)")
# Buoyancy = zero at top/bottom
problem.add_bc("left(b) = 0")
problem.add_bc("right(b) = right(fb)")
# Sets gauge pressure to zero in the constant mode
problem.add_bc("left(p) = 0", condition="(nx == 0)") # required because of above redundancy

###############################################################################
# Build solver
solver = problem.build_solver(de.timesteppers.RK222)
logger.info('Solver built')

###############################################################################
# Initial conditions or restart
if not pathlib.Path(sbp.restart_file).exists():

    # Initial conditions
    #x = domain.grid(0)
    #z = domain.grid(1)
    b = solver.state['b']
    bz = solver.state['bz']

    # Random perturbations, initialized globally for same results in parallel
    gshape = domain.dist.grid_layout.global_shape(scales=1)
    slices = domain.dist.grid_layout.slices(scales=1)
    rand = np.random.RandomState(seed=42)
    noise = rand.standard_normal(gshape)[slices]

    # Linear background + perturbations damped at walls
    zb, zt = z_basis.interval
    pert =  1e-3 * noise * (zt - z) * (z - zb)
    b['g'] = pert * 0.0 # F * pert
    b.differentiate('z', out=bz)

    # Timestepping and output
    dt = sbp.dt
    stop_sim_time = sbp.stop_sim_time
    fh_mode = 'overwrite'

else:
    # Restart
    write, last_dt = solver.load_state(restart_file, -1)

    # Timestepping and output
    dt = last_dt
    stop_sim_time = sbp.stop_sim_time + sbp.restart_add_time
    fh_mode = 'append'

###############################################################################
# Integration parameters
solver.stop_sim_time  = stop_sim_time # deliberately not sbp
solver.stop_wall_time = sbp.stop_wall_time * 60.0 # to get minutes
solver.stop_iteration = sbp.stop_iteration

###############################################################################
# Analysis
def add_new_file_handler(snapshot_directory):
    return solver.evaluator.add_file_handler(snapshot_directory, sim_dt=sbp.snap_dt, max_writes=sbp.snap_max_writes, mode=fh_mode)
# Add file handler for snapshots and output state of variables
snapshots = add_new_file_handler(sbp.snapshots_dir)
snapshots.add_system(solver.state)
# Add file handler for bp snaps and add corresponding task
if sbp.take_bp_snaps:
    bp_snapshots = add_new_file_handler(sbp.snapshots_dir + '/' + sbp.bp_snap_dir)
    bp_snapshots.add_task(sbp.bp_task, layout='g', name=sbp.bp_task_name)
# Add file handler for sl snaps and add corresponding task
if sbp.take_sl_snaps:
    sl_snapshots = add_new_file_handler(sbp.snapshots_dir + '/'  + sbp.sl_snap_dir)
    sl_snapshots.add_task(sbp.sl_task, layout='g', name=sbp.sl_task_name)

###############################################################################
# CFL
CFL = flow_tools.CFL(solver, initial_dt=dt, cadence=sbp.CFL_cadence,
                     safety=sbp.CFL_safety, max_change=sbp.CFL_max_change,
                     min_change=sbp.CFL_min_change, max_dt=sbp.CFL_max_dt,
                     threshold=sbp.CFL_threshold)
CFL.add_velocities(('u', 'w'))

###############################################################################
# Flow properties
flow = flow_tools.GlobalFlowProperty(solver, cadence=sbp.flow_cadence)
flow.add_property(sbp.flow_property, name=sbp.flow_name)

###############################################################################
# Set logger parameters if using stop_time or stop_oscillations
use_sst = sbp.use_stop_sim_time
if use_sst:
    endtime_str   = 'Sim end time: %f'
    iteration_str = 'Iteration: %i, Time: %e, dt: %e'
    time_factor   = 1.0
else:
    endtime_str   = 'Sim end period: %f'
    iteration_str = 'Iteration: %i, t/T: %e, dt/T: %e'
    time_factor   = sbp.T

###############################################################################
# Main loop
try:
    logger.info(endtime_str %(solver.stop_sim_time/time_factor))
    logger.info('Starting loop')
    start_time = time.time()
    while solver.ok:
        # Adaptive time stepping controlled from switchboard
        if (sbp.adapt_dt):
            dt = CFL.compute_dt()
        dt = solver.step(dt)
        if (solver.iteration-1) % 10 == 0:
            logger.info(iteration_str %(solver.iteration, solver.sim_time/time_factor, dt/time_factor))
            logger.info(sbp.flow_log_message.format(flow.max(sbp.flow_name)))
            if np.isnan(flow.max(sbp.flow_name)):
                raise NameError('Code blew up it seems')
except:
    logger.error('Exception raised, triggering end of main loop.')
    raise
finally:
    end_time = time.time()
    logger.info('Iterations: %i' %solver.iteration)
    logger.info(endtime_str %(solver.sim_time/time_factor))
    logger.info('Run time: %.2f sec' %(end_time-start_time))
    logger.info('Run time: %f cpu-hr' %((end_time-start_time)/60/60*domain.dist.comm_cart.size))
