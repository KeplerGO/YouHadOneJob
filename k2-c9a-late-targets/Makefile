# Creates the custom aperture mask file for C9a & verify the correctness
all: mask test

# Creates `output/custom-late-target-masks-c9a.txt`
mask:
	python create-masks.py

# Tests the contents of the mask file created by `make mask`
test:
	py.test
