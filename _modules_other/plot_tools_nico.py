"""
Plot planes from joint analysis files.
​
Usage:
    plot_2d_series.py <files>... [--output=<dir>]
​
Options:
    --output=<dir>  Output directory [default: ./frames]
​
"""
import sys
import os
from matplotlib import use, ticker
import numpy as np
import h5py
import matplotlib.pyplot as plt
from dedalus.extras import plot_tools
from dedalus.core.field import Field
hmdir = os.path.expanduser("~")
sys.path.append(hmdir+'/Dropbox/python_useful/obngfft')
​
use('Agg')
​
plt.ioff()
​
​
def title_func(sim_time): return 't = {:.3f} Tf'.format(
    0.5*sim_time*7.8e-5/np.pi)
​
​
def retrieve_3d(dset, normal_axis, normal_index, transpose=False):
    """
    Plot a 2d slice of the grid data of a 3d field. 3d in this particular case
    is (time, x, z)
​
    Based on dedalus.plot_tools.plot_bot_3d, though I just wanted to retrieve
    the data in numpy arrays and keep the plotting functions outside
​
    Parameters
    ----------
    field : field object
        Field to plot
    normal_axis: int or str
        Index or name of normal axis
    normal_index: int
        Index along normal direction to plot
    transpose : bool, optional
        Flag for transposing plot (default: False)
​
    Other keyword arguments are passed on to plot_bot.
​
    """
​
    # Wrap fields
    if isinstance(dset, Field):  # checks whether what I ask for is a field
        dset = plot_tools.FieldWrapper(dset)
​
    # Check dimension
    if len(dset.shape) != 3:
        raise ValueError("This function is for plotting 3d datasets only.")
​
    # Resolve axis name to axis index
    if isinstance(normal_axis, str):
        for axis, dim in enumerate(dset.dims):
            if normal_axis == dim.label:
                normal_axis = axis
                break
        else:
            raise ValueError("Axis name not found.")
​
    # Call general plotting function
    axes = (0, 1, 2)
    image_axes = axes[:normal_axis] + axes[normal_axis+1:]
    if transpose:
        image_axes = image_axes[::-1]
    data_slices = [slice(None), slice(None), slice(None)]
    data_slices[normal_axis] = normal_index
​
    xaxis, yaxis = image_axes
​
    # function below will fetch the file in x, z plane as well as the
    # meshgridded coordinates
    xmesh, ymesh, data = plot_tools.get_plane(dset, xaxis, yaxis,
                                              tuple(data_slices))
​
    return data, xmesh, ymesh
​
​
def prep_pics(file, tasks, start):
    """ Things that only have to be repeated once: coordinates, contour levels,
    colour limits, etc. """
    import pickle
    import ngobfftPy3 as tf
​
    dset = {}
    # clim = {}
    with open('clim.pkl', 'rb') as f:
        clim = pickle.load(f)
    with open('blevs.pkl', 'rb') as f:
        blevs = pickle.load(f)
​
    for fld in tasks:
        dset[fld] = file['tasks'][fld]
        # if fld == 'PV':
        #     clim[fld] = 2e-9  # np.abs(np.amin(dset[fld]))
        #     # print(clim[fld])
        # else:
        #     clim[fld] = np.amax(np.abs(dset[fld][:]))  # global extremum
​
    _, X, Z = retrieve_3d(file['tasks'][tasks[0]], 0, start)  # 0 is time axis
    X = np.delete(X, (0), axis=0)
    X = np.delete(X, (0), axis=1)
    Z = np.delete(Z, (0), axis=0)
    Z = np.delete(Z, (0), axis=1)
    # c_obj = plt.contour(X, Z, buoy, 10)
    # blevs = c_obj.levels  # that way I will always plot the same
​
    k = tf.k_of_x(X[0, :])
    K, _ = np.meshgrid(k, Z[:, 0])
​
    return clim, dset, blevs, K, X, X/1000, Z
​
​
def print_one_task(dadata, buoy, Xp, Z, lim, blevs, task, dpi, iteration,
                   output, title, im):
    fg, ax = plt.subplots(1, 1, figsize=(8, 4))
    cbax = ax.pcolormesh(Xp[:, im:], Z[:, im:], dadata[:, im:],
                         cmap='RdBu_r', vmin=-lim, vmax=lim)
    ax.contour(Xp[:, im:], Z[:, im:], buoy[:, im:],
               blevs, colors='k', linewidths=0.5, linestyles='-')
​
    ax.set_ylabel('$z$ (m)')
    ax.set_xlabel('$x$ (km)')
    if task == 'PV':
        ax.set_title(task + ' (s$^{-3}$), ' + title)
    else:
        ax.set_title(task + ' (m/s),' + title)
    cb = fg.colorbar(cbax, orientation='vertical', ax=ax)
    cb.formatter.set_powerlimits((0, 0))
    cb.update_ticks()
​
    plt.tight_layout()
​
    # Save figure
    savepath = output.joinpath('{0}_{1:06}.png'.format(task, iteration))
    fg.savefig(savepath, dpi=dpi)
    plt.close(fg)
​
​
def main(filename, start, count, output):
    """Save plot of specified tasks for given range of analysis writes."""
​
    # Plot settings
    tasks = ['u', 'v', 'PV']
    # scale = 2.5
    dpi = 150
​
    def savename_func(write): return 'wu_{:06}.png'.format(write)
​
    with h5py.File(filename, mode='r') as file:
​
        clim, dset, blevs, K, X, Xp, Z = prep_pics(file, tasks, start)
​
        for index in range(start, start+count):
            buoy, _, _ = retrieve_3d(file['tasks']['b'], 0, index)
​
            fig, axs = plt.subplots(len(tasks), 1, sharex=True, sharey=True,
                                    figsize=(10, 12))
​
            iteration = file['scales/write_number'][index]
            savename = savename_func(iteration)
            savepath = output.joinpath(savename)
            title = title_func(file['scales/sim_time'][index])
​
            for n, task in enumerate(tasks):
                # dset = file['tasks'][task]
                dadata, _, _ = retrieve_3d(dset[task], 0, index)
                # 0 is time axis
​
                lim = 0.7*clim[task]
                im = max(Xp.shape)//2
                cbax = axs[n].pcolormesh(Xp[:, im:], Z[:, im:], dadata[:, im:],
                                         cmap='RdBu_r', vmin=-lim, vmax=lim)
                axs[n].contour(Xp[:, im:], Z[:, im:], buoy[:, im:], blevs,
                               colors='k', linewidths=0.5, linestyles='-')
                axs[n].set_ylabel('$z$ (m)')
                if task == 'PV':
                    axs[n].set_title(task + ' (s$^{-3}$)')
                else:
                    axs[n].set_title(task + ' (m/s)')
                cb = fig.colorbar(cbax, orientation='vertical', ax=axs[n])
                cb.formatter.set_powerlimits((0, 0))
                cb.update_ticks()
​
                print_one_task(dadata, buoy, Xp, Z, lim, blevs, task, dpi,
                               iteration, output, title, im)
​
            axs[-1].set_xlabel('$x$ (km)')
            # Add time title
            # title_height = 1 - 0.5 * mfig.margin.top / mfig.fig.y
            fig.suptitle(title, ha='left')
​
            plt.tight_layout()
​
            # Save figure
            fig.savefig(str(savepath), dpi=dpi)
​
            plt.close(fig)
​
​
def HistBE(filename, start, count, output):
    """ Histograms, Beginning vs. End, for specific quantities ."""
​
    # Plot settings
    tasks = ['b', 'v']
    # scale = 2.5
    dpi = 100
    nbins = 100  #
​
    def savename_func(write): return 'hist_{:06}.png'.format(write)
​
    def hist4bar(some_data, num_of_bins):
        """ histogram, prepped for plotting by bar function (that way I only
        have to compute the initial histogram once). Returns frequencies and
        instead of bin edges, returns bin centers and widths """
        ZehHist, ZehBins = np.histogram(some_data.flatten(), bins=num_of_bins)
        width = 0.7 * (ZehBins[1] - ZehBins[0])
        array_of_centers = 0.5 * (ZehBins[:-1] + ZehBins[1:])
​
        return ZehHist, width, array_of_centers
​
    with h5py.File(filename, mode='r') as file:
        # below: future dics for histograms
        hst0 = {}  # frequencies
        wdt0 = {}  # bin widths
        ctr0 = {}  # bin centers
​
        for index in range(start, start+count):
​
            fig, axs = plt.subplots(len(tasks), 1, figsize=(5, 10),
                                    sharey=True, sharex=True)
​
            title = title_func(file['scales/sim_time'][index])
​
            for n, task in enumerate(tasks):
                dset = file['tasks'][task]
                dadata, _, _ = retrieve_3d(dset, 0, index)  # 0 is time axis
                if index == start:
                    # we store the initial values in memory for comparing later
                    d0, _, _ = retrieve_3d(dset, 0, index)
                    # histogram takes a while, we compute now
                    hst0[n], wdt0[n], ctr0[n] = hist4bar(d0, nbins)
​
                axs[n].bar(ctr0[n], hst0[n], align='center', width=wdt0[n],
                           alpha=0.5, lw=0.5, color='orange',
                           label='initial distr.')
​
                hst, wdt, ctr = hist4bar(dadata, nbins)
                axs[n].bar(ctr, hst, align='center', width=wdt,
                           alpha=0.5, lw=0.5, color='red', label=title)
​
                axs[n].legend()
​
                axs[n].set_ylabel('freq. (# of grid cells)')
                axs[n].set_title(task + ' histograms')
​
            axs[0].set_xlabel('$b$ (m\,s$^2$)')
            axs[1].set_xlabel('$v$ (m\,s$^{-1}$)')
​
            plt.tight_layout()
​
            # Save figure
            savename = savename_func(file['scales/write_number'][index])
            savepath = output.joinpath(savename)
            fig.savefig(str(savepath))
​
            plt.close(fig)
​
​
if __name__ == "__main__":
​
    import pathlib
    from docopt import docopt
    from dedalus.tools import logging
    from dedalus.tools import post
    from dedalus.tools.parallel import Sync
​
    args = docopt(__doc__)
​
    output_path = pathlib.Path(args['--output']).absolute()
    # Create output directory if needed
    with Sync() as sync:
        if sync.comm.rank == 0:
            if not output_path.exists():
                output_path.mkdir()
    post.visit_writes(args['<files>'], main, output=output_path)
    # 1post.visit_writes(args['<files>'], HistBE, output=output_path)
