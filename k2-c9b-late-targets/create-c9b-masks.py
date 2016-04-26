"""Create the custom apertures for K2 C9b late microlensing targets.
"""
from collections import OrderedDict
import json
import numpy as np
import pandas as pd

INVESTIGATION_ID = 'GO9005_LC'

# Basic facts about a Kepler channel
SCIENCE_ROWS = (20, 1043)  # (min, max) row number
SCIENCE_COLS = (12, 1111)  # (min, max) col number
KEPLER_CHANNEL_SHAPE = (1070, 1132)  # (nrows, ncols)

# Dictionary to maps K2 channel numbers onto skygroup numbers
CHANNEL_TO_SKYGROUP = dict(np.genfromtxt('input/channel_to_skygroup_season_0.txt', dtype=int))

# Definition of a 5x5 and a 11x11 mask
MASK_5_BY_5 = ";".join(["{},{}".format(x, y)
                        for x in range(-2, 3, 1)
                        for y in range(-2, 3, 1)])
MASK_11_BY_11 = ";".join(["{},{}".format(x, y)
                          for x in range(-5, 6, 1)
                          for y in range(-5, 6, 1)])


class CustomApertureFile(object):

    def __init__(self):
        self.masks = []

    def add_target(self, channel, col, row, name=''):
        """Add a C9 late target."""
        channel, col, row = int(channel), int(col), int(row)
        self.add_mask(channel, col, row, mask=MASK_11_BY_11, name=name)
        # The science team requested extra 'outrigger' pixel masks
        self.add_mask(channel, col-30, row-20, mask=MASK_5_BY_5, name=name + '-context-a')
        self.add_mask(channel, col-20, row+30, mask=MASK_5_BY_5, name=name + '-context-b')
        self.add_mask(channel, col+20, row-30, mask=MASK_5_BY_5, name=name + '-context-c')
        self.add_mask(channel, col+30, row+20, mask=MASK_5_BY_5, name=name + '-context-d')

    def add_mask(self, channel, col, row, mask, name=''):
        """Add a mask definition."""
        # First, verify that the mask does not cross an edge
        row_min = row + min([int(delta.split(',')[0]) for delta in mask.split(';')])
        row_max = row + max([int(delta.split(',')[0]) for delta in mask.split(';')])
        col_min = col + min([int(delta.split(',')[1]) for delta in mask.split(';')])
        col_max = col + max([int(delta.split(',')[1]) for delta in mask.split(';')])
        if row_min < SCIENCE_ROWS[0] or row_max > SCIENCE_ROWS[1] \
           or col_min < SCIENCE_COLS[0] or col_max > SCIENCE_COLS[1]:
            print('Warning: {} not entirely on silicon (ch col row) = ({} {} {})'.format(name, channel, col, row))
            return None
        # If we're not crossing the edge, then add the mask
        flags = INVESTIGATION_ID + ',TAD_NO_HALO,TAD_NO_UNDERSHOOT_COLUMN,NO_SOC_PHOTOMETRY'
        maskdict = OrderedDict([
                               ('name', name),
                               ('channel', channel),
                               ('skygroup', int(CHANNEL_TO_SKYGROUP[channel])),
                               ('row', row),
                               ('col', col),
                               ('mask', mask),
                               ('flags', flags),
                               ('vertices_col', [col_min, col_max, col_max, col_min]),
                               ('vertices_row', [row_min, row_min, row_max, row_max]),
                               ('npix', mask.count(';') + 1)
                               ])
        self.masks.append(maskdict)

    def pixelcost(self):
        """Returns the total number of pixels used in the masks."""
        return sum([mask['npix'] for mask in self.masks])

    def write(self, output_fn):
        """Write the custom apertures to the format required by Kepler."""
        with open(output_fn, "w") as out:
            out.write('Category: Ongoing_Microlens_Events_C9b\n')
            for mask in self.masks:
                out.write('NEW|{skygroup:d}|{flags}|{row}|{col}|{mask}\n'.format(**mask))

    def write_json(self, output_fn):
        """Dump the mask definitions into a json file."""
        json.dump({'masks': self.masks}, open(output_fn, 'w'), indent=True)


if __name__ == '__main__':
    apfile = CustomApertureFile()
    targetlist = pd.read_csv('input/c9b-targetlist.csv')
    for idx, target in targetlist.iterrows():
        apfile.add_target(target.dc_channel, target.dc_col, target.dc_row, name=target['name'])
    apfile.write('output/custom-late-target-masks-c9b.txt')
    apfile.write_json('output/k2-c9b-late-targets.json')

    # Print a little summary
    print('Number of targets: {}'.format(len(targetlist)))
    print('Number of masks: {}'.format(len(apfile.masks)))
    print('Total pixel cost: {}'.format(apfile.pixelcost()))
