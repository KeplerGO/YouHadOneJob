"""Takes the cone-shaped per-module catalogues and turns them into epic tiles.
"""
import os
import json

import numpy as np

from astropy import log
from astropy.utils.console import ProgressBar

from config import CAMPAIGN, TILED_CATS_DIR, CROPPED_CATS_DIR


def write_cropped_catalogue(input_path, output_path,
                            ra1, dec1, ra2, dec2):
    """Take a circular tile catalogue and crop it to the desired square."""
    log.info("Writing {}".format(output_path))
    out = open(output_path, "w")
    for line in open(input_path, "r").readlines():
        spl = line.split("|")
        ra, dec = float(spl[9]), float(spl[10])
        if (ra >= tile["ra1"] and
                ra < tile["ra2"] and
                dec >= tile["dec1"] and
                dec < tile["dec2"]):
            out.write(line)
    out.close()


if __name__ == "__main__":
    tiles = json.load(open("c{}-tiles.json".format(CAMPAIGN)))
    tiled_cats_filenames = tiles["tiles"].keys()
    for input_fn in tiled_cats_filenames:
        tile = tiles["tiles"][input_fn]
        input_path = os.path.join(TILED_CATS_DIR, os.path.basename(input_fn))
        output_path = os.path.join(CROPPED_CATS_DIR, os.path.basename(input_fn + "-cropped"))
        write_cropped_catalogue(input_path, output_path,
                                tile["ra1"], tile["dec1"],
                                tile["ra2"], tile["dec2"])
