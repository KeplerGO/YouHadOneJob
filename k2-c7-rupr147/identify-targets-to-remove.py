# -*- coding: utf-8 -*-
"""
K2 Campaign 7 includes a lot of targets which are likely members of the
Rupr 147 cluster.  We decided to cover the cluster using a large aperture mask,
rather than large numbers of individual stellar targets.  This script figures
out which EPIC ID's need to be removed from the target selection because their
pixels are covered by the large pixel aperture mask.
"""
from pylab import *
import datetime

from astropy.table import Table
from astropy.utils.console import ProgressBar

from K2fov import fov
from K2fov.K2onSilicon import getRaDecRollFromFieldnum


# By how many pixel does a target need to be inside the big aperture mask?
TOL = 4

# The output is a text file detailing the EPIC ID's of targets to remove
OUTPUT_FN = 'c7-targets-to-exclude.txt'


def get_kfov(campaign=7):
    """Returns a KeplerFov object for a given campaign."""
    ra, dec, scRoll = getRaDecRollFromFieldnum(campaign)
    # convert from SC roll to FOV coordinates
    # do not use the fovRoll coords anywhere else
    # they are internal to this script only
    fovRoll = fov.getFovAngleFromSpacecraftRoll(scRoll)
    ## initialize class
    kfov = fov.KeplerFov(ra, dec, fovRoll)
    return kfov


if __name__ == "__main__":
    out = open(OUTPUT_FN, 'w')
    out.write("epic_id,ra,dec\n")

    # This file details the aperture mask
    aper_mask = Table.read("go_lc_custom_Rup147_c7_oct2015_untrimmed.txt",
                     format="ascii",
                     names=('epic', 'chrot', 'flags', 'x', 'y', 'pixels'))

    figure(figsize=(8,6))
    for row in aper_mask:
        x, y = row["x"], row["y"]
        # All the pixel aperture masks are 50x50
        pl_mask = plot([x, x, x+50, x+50, x], [y, y+50, y+50, y, y],
                        lw=2, color="#999999")
        xlabel("row")
        ylabel("col")

    kfov = get_kfov()
    targets = Table.read("../targets/targets-x-epic.fits")
    for star in ProgressBar(targets):
        # Optimization
        if star['dec'] < -20 or star['ra'] < 286:
            continue

        ch, col, row = kfov.getChannelColRow(star['ra'], star['dec'])

        # The channel 32 aperture mask can be defined as the union of two rectangles:
        # a horizontal rectangle running from (row,col) = (442, 224) to (849, 529)
        # + a vertical rectangle vertical runs from (493, 173) to (798, 580)
        if ch == 32:
            if (
                ((442+TOL <= row) and (row <= 849+1-TOL) and (224+TOL <= col) and (col <= 529+1-TOL))
                or
                ((493+TOL <= row) and (row <= 798+1-TOL) and (173+TOL <= col) and (col <= 580+1-TOL))
                ):
                sc_exc = scatter(row, col, marker='x', edgecolor='red', lw=1, s=30, zorder=9)
                out.write("{},{},{}\n".format(star['id'], star['ra'], star['dec']))
            else:
                sc_inc = scatter(row, col, facecolor='blue', lw=0.2, s=5, zorder=9)

    # Now let's make the plot pretty
    title("Campaign 7 / channel 32", fontsize=22, fontweight=600)
    l = legend((sc_inc, sc_exc, pl_mask[0]),
               ("targets to keep", "targets to remove", "Rupr147 aperture masks"))
    l.set_zorder(999)
    l.get_frame().set_facecolor('white')
    xlim([250, 1050])
    ylim([0, 800])
    figtext(0.98, 0.02,
            """Crafted with $\\heartsuit$ by Geert on {}""".format(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')),
            fontsize=8, fontweight=400,
            ha="right")
    savefig("c7-channel32.png", dpi=150)
    close()

    out.close()
