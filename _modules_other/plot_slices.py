"""
Plot planes from joint analysis files.

Usage:
    plot_slices.py EXP_NAME <files>... [--output=<dir>]

Options:
    EXP_NAME            # Name of experiment to add switchboard module path
    --output=<dir>      # Output directory [default: ./frames]

"""

import h5py
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.ioff()
from dedalus.extras import plot_tools
# Import modified version of plot bot
from plot_tools_mod import plot_bot_3d_mod

###############################################################################
# Helper functions

# Sets parameters according to the switchboard settings
def flip_the_switches(plot_all_variables, plot_sponge_profile, use_sst, T):
    if plot_all_variables:
        tasks = ['b', 'p', 'u', 'w']
        nrows, ncols = 2, 2
    else:
        tasks = ['w']
        if plot_sponge_profile:
            nrows, ncols = 1, 3
        else:
            nrows, ncols = 1, 2
    if use_sst:
        title_str = r'{:}, $t$ = {:2.3f}'
        time_factor = 1.0
    else:
        title_str = r'{:}, $t/T$ = {:2.3f}'
        time_factor = T
    return tasks, nrows, ncols, title_str, time_factor

# Adds the title to a frame
def add_frame_title(fig, file, index, title_func):
    title = title_func(file['scales/sim_time'][index])
    fig.suptitle(title, fontsize='large')

# Saves figure as a frame
def save_fig_as_frame(fig, file, index, savename_func, output, dpi):
    savename = savename_func(file['scales/write_number'][index])
    savepath = output.joinpath(savename)
    fig.savefig(str(savepath), dpi=dpi)
    fig.clear()

# Plots one frame of one task (b, p, u, or w)
def plot_one_task(n, ncols, mfig, file, task, index, x_lims, y_lims, n_clrbar_ticks):
    # Build subfigure axes
    i, j = divmod(n, ncols)
    axes = mfig.add_axes(i, j, [0, 0, 1, 1])
    # Call 3D plotting helper, slicing in time
    dset = file['tasks'][task]
    plot_bot_3d_mod(dset, 0, index, x_limits=x_lims, y_limits=y_lims, n_cb_ticks=n_clrbar_ticks, axes=axes, title=task, even_scale=True)

# Extracts relevant arrays from a vertical profile snapshot
def extract_vp_snapshot(task_name, snap_dir, vp_snaps):
    vp_snap_filepath = snap_dir + '/' + vp_snaps + '/' + vp_snaps + '_s1.h5'
    with h5py.File(vp_snap_filepath, mode='r') as file:
        data = file['tasks'][task_name]
        temp = data[()]
        hori = temp[0][0]
        z_   = file['scales']['z']['1.0']
        vert = z_[()]
    return hori, vert

def add_vp_buffers(ax, buffer, extra_buffer):
    xvals,yvals = ax.get_xlim(), ax.get_ylim()
    xrange = xvals[1]-xvals[0]
    # Check if its a constant vertical profile
    if xrange==0:
        xleft  = xvals[0] - extra_buffer
        xright = xvals[1] + extra_buffer
    else:
        xleft  = xvals[0] - buffer
        xright = xvals[1] + buffer
    ax.set_xlim(xleft, xright)
    yrange = yvals[1]-yvals[0]
    ytop   = yvals[1] + buffer
    ybott  = yvals[0]
    ax.set_ylim(ybott, ytop)

# Set a fixed aspect ratio on matplotlib plots regardless of axis units
def fixed_aspect_ratio(ax, ratio):
    # Does not work for twin axes plots
    xvals,yvals = ax.get_xlim(), ax.get_ylim()
    xrange = xvals[1]-xvals[0]
    yrange = yvals[1]-yvals[0]
    ax.set_aspect(ratio*(xrange/yrange), adjustable='box')

def plot_bp_on_left(bp_task_name, snap_dir, bp_snaps, mfig, buffer, extra_buffer, dis_ratio, ylims=None):
    axes0 = mfig.add_axes(0, 0, [0, 0, 1.3, 1])#, sharey=axes1)
    axes0.set_title('Background profile')
    axes0.set_xlabel(r'$N$ (s$^{-1}$)')
    axes0.set_ylabel(r'$z$ (m)')
    # Get arrays of background profile values
    hori, vert = extract_vp_snapshot(bp_task_name, snap_dir, bp_snaps)
    axes0.plot(hori, vert, 'k-')
    # Add buffers around the edge to make plot look nice
    add_vp_buffers(axes0, buffer, extra_buffer)
    # Force display aspect ratio
    fixed_aspect_ratio(axes0, dis_ratio)
    return axes0

# Adds sponge layer profile on top of background profile plot
def add_sponge_profile(sl_task_name, snap_dir, sl_snaps, mfig, buffer, extra_buffer, dis_ratio, ylims=None):
    axes0 = mfig.add_axes(0, 2, [0, 0, 1.3, 1])
    axes0.set_title('Sponge layer')
    axes0.set_xlabel(r'$\nu$ (m$^{2}$/s)')
    axes0.set_ylabel(r'$z$ (m)')
    # Get arrays of background profile values
    hori, vert = extract_vp_snapshot(sl_task_name, snap_dir, sl_snaps)
    axes0.plot(hori, vert, 'k-')
    # Add buffers around the edge to make plot look nice
    add_vp_buffers(axes0, buffer, extra_buffer)
    # Force display aspect ratio
    fixed_aspect_ratio(axes0, dis_ratio)
    return axes0

###############################################################################
def main(filename, start, count, output):
    """Save plot of specified tasks for given range of analysis writes."""

    # To import the switchboard
    import sys
    switch_path = "../" + NAME
    sys.path.insert(0, switch_path) # Adds higher directory to python modules path
    import switchboard as sbp

    # Get relevant parameters from switchboard used in loop
    plot_all        = sbp.plot_all_variables
    #bp_task_name    = sbp.bp_task_name
    n_clrbar_ticks  = sbp.n_clrbar_ticks
    #T               = sbp.T
    # Display parameters
    x_f             = sbp.x_0 + sbp.L_x_dis
    z_b             = sbp.z_t - sbp.L_z_dis

    # Calculate aspect ratio
    AR = sbp.L_x_dis / sbp.L_z_dis
    # Set tuples for display boundaries
    x_lims = [sbp.x_0, x_f]
    y_lims = [z_b, sbp.z_t]

    # Change the size of the text overall
    font = {'size' : sbp.font_size}
    plt.rc('font', **font)
    # Set parameters based on switches
    tasks, nrows, ncols, title_str, time_factor = flip_the_switches(plot_all, sbp.plot_sponge, sbp.use_stop_sim_time, sbp.T)
    # Plot settings
    scale   = sbp.scale
    dpi     = sbp.dpi
    title_func = lambda sim_time: title_str.format(NAME, sim_time/time_factor)
    savename_func = lambda write: 'write_{:06}.png'.format(write)
    # Layout
    image = plot_tools.Box(AR, 1)
    pad = plot_tools.Frame(0.2, 0.2, 0.15, 0.15)
    margin = plot_tools.Frame(0.3, 0.2, 0.1, 0.1)

    # Create multifigure
    mfig = plot_tools.MultiFigure(nrows, ncols, image, pad, margin, scale)
    fig = mfig.figure
    # Plot writes
    with h5py.File(filename, mode='r') as file:
        for index in range(start, start+count):
            for n, task in enumerate(tasks):
                if (plot_all == False):
                    # Plot stratification profile on the left
                    ax0 = plot_bp_on_left(sbp.bp_task_name, sbp.snapshots_dir, sbp.bp_snap_dir, mfig, sbp.buffer, sbp.extra_buffer, sbp.vp_dis_ratio, y_lims)
                    if sbp.plot_sponge:
                        ax1 = add_sponge_profile(sbp.sl_task_name, sbp.snapshots_dir, sbp.sl_snap_dir, mfig, sbp.buffer, sbp.extra_buffer, sbp.vp_dis_ratio, y_lims)
                    # shift n so that animation is on the right side
                    n = 1
                plot_one_task(n, ncols, mfig, file, task, index, x_lims, y_lims, n_clrbar_ticks)
            # Add title to frame
            add_frame_title(fig, file, index, title_func)
            # Save figure
            save_fig_as_frame(fig, file, index, savename_func, output, dpi)
    plt.close(fig)

###############################################################################
if __name__ == "__main__":

    import pathlib
    from docopt import docopt
    from dedalus.tools import logging
    from dedalus.tools import post
    from dedalus.tools.parallel import Sync

    args = docopt(__doc__)

    NAME = str(args['EXP_NAME'])

    output_path = pathlib.Path(args['--output']).absolute()
    # Create output directory if needed
    with Sync() as sync:
        if sync.comm.rank == 0:
            if not output_path.exists():
                output_path.mkdir()
    post.visit_writes(args['<files>'], main, output=output_path)
