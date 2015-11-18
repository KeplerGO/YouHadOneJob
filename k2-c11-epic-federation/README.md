# k2-c11-epic-federation

The software used to create the K2 EPIC catalogs was found to
struggle during the creation of the Campaign 11 catalog:
the very large number of sources near the Galactic Center
caused the software to be slow and run out of memory.

The solution adopted was to create 25 "mini-catalogues" for C11,
and federate them into a single catalogue using the three scripts
present in this directory.  These scripts also took care of
removing the objects already included in the EPIC catalogs
for C2 and C9, which overlap with C11.

No other field will experience a similar source density in the
near future, hence these scripts were developed for a single use.

