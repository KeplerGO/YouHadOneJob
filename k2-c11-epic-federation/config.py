"""Configure the epikfabrik here."""

# Campaign number
CAMPAIGN = 11

# Where to find and store our files?
ROOT_DIR = "/home/gb/proj/epic/c{}".format(CAMPAIGN)
TILED_CATS_DIR = ROOT_DIR + "/tiled-cats"
CROPPED_CATS_DIR = ROOT_DIR + "/cropped-cats"
FINAL_CAT_DIR = ROOT_DIR + "/final-cat"

# How to execute stilts?
STILTS = "nice java -XX:+UseConcMarkSweepGC -Xmx2000m " \
         "-jar /home/gb/bin/topcat-full.jar -stilts"

# Remove objects which already appear in these pre-existing catalogs;
# this file must have four columns: EPIC,RA,DEC,KEPMAG;
# make sure to remove duplicate entries from this file w/ internal crossmatch!
PREVIOUS_CATALOG = "../mast/epic-c2-c9.fits"

# Cross-matching radius in arcsec
MATCHING_RADIUS = 0.05

# Where to start EPIC numbering?
EPIC_START = 229228999

# Make sure the directories exists
import os
for dir in [CROPPED_CATS_DIR, FINAL_CAT_DIR]:
    try:
        os.makedirs(dir)
    except FileExistsError:
        pass
