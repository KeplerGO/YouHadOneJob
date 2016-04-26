"""Reads the C9b late targetlist delivered by Radek, augments it with the
pixel coordinates determined by Doug Caldwell, and carries out consistenty checks."""
import numpy as np
import pandas as pd

# The C9b late targets as delivered by Radek Poleski
targetlist_radek = pd.read_fwf('input/late_targets_K2C9b_v2.dat',
                               names=('ra', 'dec', 'k2fov_channel',
                                      'k2fov_col', 'k2fov_row',
                                      'peakmag', 'name'))
targetlist_radek.to_csv('input/late_targets_K2C9b_v2.dat.csv')

# Doug augmented Radek's table with pixel coordinates from the Kepler Matlab pipeline
targetlist_doug = pd.read_fwf('input/late_targets_K2C9b_v2_morc.dat',
                              names=('dc_ra', 'dc_dec', 'dc_module', 'dc_output',
                                     'dc_channel', 'dc_row', 'dc_col'),
                              comment='#')
targetlist_doug.to_csv('input/late_targets_K2C9b_v2_morc.dat.csv')

targetlist = targetlist_radek.join(targetlist_doug)
targetlist.to_csv('input/c9b-targetlist.csv')

################
# SANITY CHECKS
################

# Ensure both targetlists had the same target on each row
assert(np.all((targetlist.ra - targetlist.dc_ra) == 0.0))
assert(np.all((targetlist.dec - targetlist.dc_dec) == 0.0))
# Ensure both targetlists agree on the CCD channel
assert(np.all((targetlist.k2fov_channel - targetlist.dc_channel) == 0))
# K2fov is expected to be accurate to within 10px
delta = np.hypot(targetlist.k2fov_col - targetlist.dc_col,
                 targetlist.k2fov_row - targetlist.dc_row)
assert(np.all(delta < 10))

print("Pixel conversion offset: "
      "median {:.2f}, min {:.2f}, max {:.2f}".format(delta.median(), delta.min(), delta.max()))

# Are targets already in the microlensing region?
from K2fov import c9
for target in targetlist.itertuples():
    if c9.inMicrolensRegion(target.ra, target.dec, padding=5):
        print("Warning: {} already in superstamp".format(target.name))
