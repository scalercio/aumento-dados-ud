#!/bin/sh
export PYTHONIOENCODING=utf-8

echo "Testing rotation"
python augment.py \
   -infile "./data/leopardo-ok.conllu" \
   -outfile "./data/leopardo-shifted-obl-final.conllu" \
   -maxrot 3 \
   -operation "obl"

echo "Done, check your output files"
