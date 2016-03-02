"""Test the custom K2 aperture masks created for the C9a late targets.

Usage
-----
Call `py.test` from the command line.
"""
import pandas

from K2fov import c9
from K2fov.fields import getKeplerFov

LATE_TARGETS = pandas.read_fwf('late_targets_K2C9a_v3.dat',
                               names=('ra', 'dec', 'channel', 'col', 'row',
                                      'peakmag', 'name', 'name2'))


def test_masks():
    """All the late targets should be covered."""
    c9fov = getKeplerFov(9)
    for idx, target in LATE_TARGETS.iterrows():
        ch, col, row = c9fov.getChannelColRow(target.ra, target.dec)
        assert c9.pixelInMicrolensRegion(int(ch), int(col), int(row))
        assert c9.maskInMicrolensRegion(int(ch), int(col), int(row), padding=4.99)


def test_magnitudes():
    """No event should be expected to be brighter than 12th mag."""
    assert (LATE_TARGETS['peakmag'] > 12).all()


def test_pixelcost():
    """The total pixel cost of all masks should not exceed 10,000 pixels."""
    masks = open('custom-late-target-masks-c9a.txt').readlines()
    pixelcost = sum([mask.count(';') + 1 for mask in masks])
    assert pixelcost < 10000
