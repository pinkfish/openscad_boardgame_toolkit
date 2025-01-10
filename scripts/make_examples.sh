#!/bin/bash

TOP_LEVEL=$(git rev-parse --show-toplevel)

echo $TOP_LEVEL
cd $TOP_LEVEL

cd examples

python ../scripts/make_files.py
