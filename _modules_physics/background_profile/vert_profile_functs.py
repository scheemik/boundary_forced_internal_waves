"""
A script containing helper functions to create certain features in a vertical profile
Kinda like defining the puzzle pieces. The full puzzle is assembled elsewhere

Modified by Mikhail Schee, June 2019

"""

###############################################################################

import numpy as np

def tanh_(z, height, slope, center):
    # initialize array of values to be returned
    values = 0*z
    # calculate step
    values = 0.5*height*(np.tanh(slope*(z-center))+1)
    return values

def cosh2(z, height, slope, center):
    # initialize array of values to be returned
    values = 0*z
    # calculate step
    values = height/(np.cosh(slope*(z-center))**2.0)
    #values = (height*slope)/(2.0*(np.cosh(slope*(z-center)))**2.0)
    return values

def tanh_bump(z, height, slope, center, width):
    # initialize array of values to be returned
    values = 0*z
    # calculate sides of bump
    c_l, c_r = (center-width/2.0), (center+width/2.0)
    # add left side
    values += tanh_(z, height, slope, c_l)
    # add right side
    values += tanh_(z, height, -slope, c_r)
    # correct for added height
    values -= height
    return values
