import numpy as np
import matplotlib
import matplotlib.pyplot as plt

from dedalus.extras import plot_tools

# To import the switchboard
import sys
that_path = "./_modules_physics/background_profile"
sys.path.append(that_path)
import bp_default as bp
that_path = "./_modules_physics/sponge_layer"
sys.path.append(that_path)
import sl_default as sl

def build_bp_array(z):
    BP_array = z*0.0 + 1.0
    return BP_array

def fixed_aspect_ratio(ax, ratio):
    '''
    Set a fixed aspect ratio on matplotlib plots
    regardless of axis units
    '''
    xvals,yvals = ax.get_xlim(), ax.get_ylim()

    xrange = xvals[1]-xvals[0]
    yrange = yvals[1]-yvals[0]
    ax.set_aspect(ratio*(xrange/yrange), adjustable='box')

# Plotting function for sponge layer, background profile, etc.
def test_plot(hori, vert, plt_title, x_label=None, y_label=None, x_lims=None, y_lims=None):
    #with plt.rc_context({'axes.edgecolor':'white', 'text.color':'white', 'axes.labelcolor':'white', 'xtick.color':'white', 'ytick.color':'white', 'figure.facecolor':'black'}):
    fg, ax = plt.subplots(1,1)
    ax.set_title(plt_title)
    if x_label != None:
        ax.set_xlabel(x_label)
    if y_label != None:
        ax.set_ylabel(y_label)
    if x_lims != None:
        ax.set_xlim(x_lims)
    if y_lims != None:
        ax.set_ylim(y_lims)
    ax.plot(hori, vert, 'k-')
    plt.grid(True)
    fixed_aspect_ratio(ax, 2.0)
    return fg

z_b = -0.5
z_t =  0.0
n = 0
ml_b = -0.38
ml_t = -0.2
slope = 120
N_1 = 0.95
N_2 = 1.05

z = np.linspace(z_b, z_t, 100)
a = sl.build_sl_array(z)

x_lims = [0, 0.5]
y_lims = [z_b, z_t]

plt_title = 'Plot title'
x_label = r'$\nu$ (s$^{-1}$)'
y_label = r'$z$ (m)'

#fg = test_plot(a, z, plt_title, x_label, y_label, x_lims, y_lims)
fg = test_plot(a, z, plt_title, x_label, y_label)
plt.show()
