"""Plots the special masks for c9b on top of the Kepler CCD mosaic
to enable a visual sanity check."""
from K2fov import c9
import pandas as pd

targetlist = pd.read_csv('input/c9b-targetlist.csv')

p = c9.C9FootprintPlot()
p.plot_outline(annotate_channels=True, annotate_late_targets=True)
p.fig.tight_layout()
#p.fig.savefig(output_fn)
p.fig.show()
