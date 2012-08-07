#!/bin/bash

export PYTHONPATH=${HOME}/lib/python:$PYTHONPATH
export PATH=${HOME}/bin:$PATH

python /home/41000/data/scripts/altxkcd/src/altxkcd.py updateComic $1 $2 $3
