#!/bin/sh
export PYTHONIOENCODING=utf-8

echo "Testing rotation"
python augment.py \
   -infile "./data/tubarao.conllu" \
   -outfile "./data/tubarao-shifted-obl-final.conllu" \
   -maxrot 3 \
   -prob 0.3 \
   -operation "rotate"

echo "Done, check your output files"
