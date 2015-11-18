"""Define the tiles that make up a campaign catalogue.

The output of this script is a plot of the catalogue tiling,
and a json text file describing the tiles.
"""
import json

import matplotlib.pyplot as pl

from K2fov import fov
from K2fov import projection as proj
from K2fov.K2onSilicon import getRaDecRollFromFieldnum

from config import CAMPAIGN

# Configuration
TILE_RA = 252    # Tiling start (ra)
TILE_DEC = -32   # Tiling start (dec)
TILE_SIZE = 4    # Width/height of each square tile
TILE_NO_RA = 5   # Number of tiles in RA direction
TILE_NO_DEC = 5  # Number of tiles in Dec direction


def get_fov(campaign):
    ra, dec, scRoll = getRaDecRollFromFieldnum(campaign)
    fovRoll = fov.getFovAngleFromSpacecraftRoll(scRoll)
    return fov.KeplerFov(ra, dec, fovRoll)


if __name__ == "__main__":
    output = {"tiles": {}}  # Dict that will be written as a JSON file

    f = get_fov(CAMPAIGN)

    pl.figure(figsize=(16, 9))
    ph = proj.PlateCaree()
    f.plotPointing(ph, showOuts=False, plot_degrees=False,
                   mod3="white", colour="gray", lw=5,
                   solid_capstyle="round", solid_joinstyle="round")

    for x in range(TILE_NO_RA):
        for y in range(TILE_NO_DEC):
            ra = TILE_RA + x * TILE_SIZE
            dec = TILE_DEC + y * TILE_SIZE
            tile_def = {
                        "ra1": ra - .5*TILE_SIZE,
                        "dec1": dec - .5*TILE_SIZE,
                        "ra2": ra + .5*TILE_SIZE,
                        "dec2": dec + .5*TILE_SIZE
                        }

            r = pl.Rectangle((tile_def["ra1"], tile_def["dec1"]),
                             width=TILE_SIZE,
                             height=TILE_SIZE,
                             facecolor="none",
                             lw=4, zorder=999)
            pl.axes().add_artist(r)
            pl.scatter(ra, dec,
                       marker="x", s=40, lw=2,
                       edgecolor="black", zorder=999)
            print("{},{}".format(ra, dec))

            tile_fn = "ra{:.1f}_de{:.1f}_r{}.dmc.dat".format(ra, dec, "2.8")
            output["tiles"][tile_fn] = tile_def

    # Write the JSON file
    json.dump(output, open("c{}-tiles.json".format(CAMPAIGN), "w"), indent=True)

    # Write the plot
    pl.xlabel("R.A. [deg]")
    pl.ylabel("Dec [deg]")
    pl.title("EPIC tiling for C11")
    pl.xlim([249, 271])
    pl.ylim([-35, -13])
    pl.xticks(range(249, 271, 1))
    pl.yticks(range(-35, -13, 1))
    pl.grid()
    pl.tight_layout()
    pl.savefig("c11-tiles.png")
    pl.close()
