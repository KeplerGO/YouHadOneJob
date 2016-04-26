"""Test the custom K2 aperture masks created for the C9b late targets.

Usage
-----
Call `py.test` from the command line.
"""
import pandas

from K2fov import c9

LATE_TARGETS = pandas.read_csv('input/c9b-targetlist.csv')


def test_masks():
    """All the late targets should be covered."""
    for idx, target in LATE_TARGETS.iterrows():
        ch, col, row = target.dc_channel, target.dc_col, target.dc_row
        assert c9.pixelInMicrolensRegion(int(ch), int(col), int(row))
        assert c9.maskInMicrolensRegion(int(ch), int(col), int(row), padding=4.99)


def test_magnitudes():
    """No event should be expected to be brighter than 12th mag."""
    assert (LATE_TARGETS['peakmag'] > 12).all()


def test_pixelcost():
    """The total pixel cost of all masks should not exceed 10,000 pixels."""
    masks = open('output/custom-late-target-masks-c9b.txt').readlines()
    pixelcost = sum([mask.count(';') + 1 for mask in masks])
    assert pixelcost < 15000


if __name__ == '__main__':
    import pytest
    pytest.main()
