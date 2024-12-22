#!/bin/bash

set -x

# Generate SVGs of puzzle solutions
puzzle svgs --solution puzzles solutions

# Generate puzzle features
puzzle features puzzles features.csv

# Get timing data
source ./get-stats.sh

# Run notebook
jupyter nbconvert --to notebook --execute daily-stats.ipynb
