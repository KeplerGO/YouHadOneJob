# Creates the custom aperture mask file for C9a & verify the correctness
all: parse mask test

# Creates `input/c9b-targetlist.csv`
parse:
	python parse-input.py

# Creates `output/custom-late-target-masks-c9a.txt`
mask:
	python create-c9b-masks.py

# Tests the contents of the mask file created by `make mask`
test:
	py.test
