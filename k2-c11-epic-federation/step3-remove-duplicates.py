"""
Cross-match all the *-cropped mini-catalogs in a directory
with an existing catalogue, and produce new mini-catalogs
containing only the objects that were not already in the
existing catalog (to within a MATCHING_RADIUS).

The output is the *.dmc.dat file.
"""
import os
import re
import glob

from astropy import log
from astropy.utils.console import ProgressBar

from config import (CROPPED_CATS_DIR,
                    FINAL_CAT_DIR,
                    STILTS,
                    PREVIOUS_CATALOG,
                    MATCHING_RADIUS,
                    EPIC_START)

def syscall(cmd):
    """Calls a system command and returns its status."""
    log.info(cmd)
    status = os.system(cmd)
    if status != 0:
        log.error("System call returned {}\n"
                  "command was: {}".format(status, cmd))
    return status


def convert_to_csv(fn):
    """Converts a file from pipe-delimited to comma-delimited."""
    if os.path.exists(fn + ".csv"):
        log.info("Skipping creating {} -- file already exists.".format(fn))
    else:
        syscall("""sed "s/|/,/g" {0} > {0}.csv""".format(fn))


def remove_duplicates_from_tiles(fn):
    """Removes any source appearing more than once at the same position
    from the tiled catalogues."""
    cfg = {"stilts": STILTS,
           "fn_input": fn + ".csv",
           "fn_output": fn + "-without-duplicates.csv",
           "matching_radius":  MATCHING_RADIUS*1.1
           }
    cmd = """{stilts} tmatch1 \
             in={fn_input} ifmt=csv \
             matcher=sky params={matching_radius} \
             values="col10 col11" \
             action=keep1 out={fn_output} ofmt=csv""".format(**cfg)
    syscall(cmd)


def remove_duplicates(fn):
    cfg = {"stilts": STILTS,
           "fn_input": fn + "-without-duplicates.csv",
           "fn_output": fn + "-matched.csv",
           "fn_ref_catalog": PREVIOUS_CATALOG,
           "matching_radius":  MATCHING_RADIUS
           }
    cmd = """{stilts} tmatch2 \
             in1={fn_input} ifmt1=csv \
             in2={fn_ref_catalog} ifmt2=fits \
             matcher=sky params={matching_radius} \
             values1="col10 col11" values2="col2 col3" \
             join=1not2 out={fn_output} ofmt=csv""".format(**cfg)
    syscall(cmd)


def merge(output_fn):
    """Merges all CROPPED_CATS_DIR/*matched.csv files into a single file.

    Merges all matched tables into a single catalog,
    albeit skipping the header lines that stilts added.
    """
    cmd = """cat {}/*matched.csv | \
             grep -v "col1,col2," > {}
             """.format(CROPPED_CATS_DIR, output_fn)
    syscall(cmd)


def assign_epicids(input_fn, output_fn):
    """Assigns EPIC IDs to each row in the catalog.

    This is pretty memory intense at present :-(
    """
    # Open the input
    log.info("Opening {}".format(input_fn))
    infile = open(input_fn, "r")
    # Open the output
    log.info("Writing {}".format(output_fn))
    outfile = open(output_fn, "w")
    # Start numbering!
    epic_id = EPIC_START
    for line in infile.readlines():
        # We assume that the EPIC ID is the first column
        # in a pipe-delimited csv file
        outfile.write(re.sub("^.[^,]*", str(epic_id), line))
        epic_id += 1
    # Clean up
    outfile.close()
    infile.close()


def convert_to_dmc(input_fn, output_fn):
    """Convert from csv to pipe-delimited.
    """
    syscall("""sed "s/,/|/g" {} > {}""".format(input_fn, output_fn))


if __name__ == "__main__":
    input_filenames = glob.glob(os.path.join(CROPPED_CATS_DIR, "*-cropped"))
    log.info("Converting cropped catalogues into csv format")
    ProgressBar.map(convert_to_csv,
                    input_filenames,
                    multiprocess=True, step=1)

    log.info("Removing objects appearing twice in the cropped tiles")
    ProgressBar.map(remove_duplicates_from_tiles,
                    input_filenames,
                    multiprocess=True, step=1)

    log.info("Removing objects already in EPIC with stilts "
             "using a {} arcsec matching radius".format(MATCHING_RADIUS))
    ProgressBar.map(remove_duplicates,
                    input_filenames,
                    multiprocess=True, step=1)

    merge_fn = os.path.join(FINAL_CAT_DIR, "merged.dmc.csv")
    log.info("Merging the tiles into {}".format(merge_fn))
    merge(output_fn=merge_fn)

    merge_with_epicid_fn = os.path.join(FINAL_CAT_DIR, "merged.dmc.csv-numbered")
    log.info("Assigning epicids -- writing {}".format(merge_with_epicid_fn))
    assign_epicids(input_fn=merge_fn, output_fn=merge_with_epicid_fn)

    final_fn = os.path.join(FINAL_CAT_DIR, "final-result.dmc.dat")
    log.info("Writing {}".format(final_fn))
    convert_to_dmc(input_fn=merge_with_epicid_fn, output_fn=final_fn)
