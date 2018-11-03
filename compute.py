from numpy import exp, cos, linspace
import matplotlib.pyplot as plt
import os, time, glob
from merge import make_plot, merge_csv


def compute(fwd, rev, diode_spice, resolution=500):
    """Return filename of plot of the damped_vibration function."""
    print("[*]compute: ", end='')
    print(diode_spice)
    return make_plot(fwd, rev, diode_spice=diode_spice)


if __name__ == '__main__':
    print (compute(1, 0.1, 1, 20))