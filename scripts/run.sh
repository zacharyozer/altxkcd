#!/bin/bash

export PYTHONPATH=/home/41000/lib/python:$PYTHONPATH
export PATH=/home/41000/bin:$PATH

python /home/41000/data/scripts/altxkcd/src/altxkcd.py updateComic $1 $2 $3
