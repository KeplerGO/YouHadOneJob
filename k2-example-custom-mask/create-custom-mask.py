"""Create custom aperture files for Matthew Penny's special request for C9.

This script creates files detailing custom apertures.
The format is: ID|SkyGroup|Flags|Row|Col|Delta;Delta;Delta

SkyGroups are as they were in Kepler Season 0, i.e. rotated by 180 degrees
"""
import pandas as pd
from K2fov import fields

# K2 skygroups are as they were in Kepler Season 0
# hence rotate the focal plane by 180 degrees
CHANNEL_2_SKYGROUP = {29: 53,
                      30: 54,
                      48: 40,
                      49: 33,
                      51: 35}

fov = fields.getKeplerFov(9)

delta_10_by_10_mask = ";".join(["{},{}".format(x, y)
                                for x in range(-4, 6, 1)
                                for y in range(-4, 6, 1)])

df = pd.read_csv("isolated-stars.csv")
with open("custom-isolated-stars.txt", "w") as out:
    out.write("Category: Isolated_Stars\n")
    #out.write("id|channel|refcol|refrow|delta\n")
    for idx, row in df.iterrows():
        ch, col, row = fov.getChannelColRow(row["ra"], row["dec"])
        skygroup = CHANNEL_2_SKYGROUP[int(ch)]
        out.write("NEW|{:d}|GO9002_LC,TAD_NO_HALO,TAD_NO_UNDERSHOOT_COLUMN,NO_SOC_PHOTOMETRY|{}|{}|{}\n".format(skygroup, int(row), int(col), delta_10_by_10_mask))

df = pd.read_csv("dark-clouds.csv")
with open("custom-dark-clouds.txt", "w") as out:
    out.write("Category: Dark_Clouds\n")
    #out.write("id|channel|refcol|refrow|delta\n")
    for idx, row in df.iterrows():
        ch, col, row = fov.getChannelColRow(row["ra"], row["dec"])
        skygroup = CHANNEL_2_SKYGROUP[int(ch)]
        out.write("NEW|{:d}|GO9003_LC,TAD_NO_HALO,TAD_NO_UNDERSHOOT_COLUMN,NO_SOC_PHOTOMETRY|{}|{}|{}\n".format(skygroup, int(row), int(col), delta_10_by_10_mask))
