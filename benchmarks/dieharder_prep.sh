#!/bin/bash
echo "Running Dieharder PRNG tests against KHAN Cipher payload..."
# -a runs all tests, -g 201 reads from file
dieharder -a -g 201 -f benchmarks/data/khan_1GB.bin
