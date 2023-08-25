# encoding: utf-8

"""
Created by Arthur Scalercio
20.06.2023
Code to play with augmentation options and test on a single file
"""

__author__ = 'Arthur Scalercio'
from IO import conllud
from SP import augmenter
import codecs
import argparse

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-infile', type=str, default='./data/tubarao.conllu', help='UD file to augment')
    parser.add_argument('-outfile', type=str, default='./data/tubarao-shifted.conllu', help='Output file')
    parser.add_argument('-maxrot', type=int, default=3, help='Maximum number of rotation operations per sentence')
    parser.add_argument('-operation', type=str, default='obl', help='obl|advcl')
    args = parser.parse_args()
    # Rotates and crops with given probabilities and saves the results
    augment(args)
    create_file(args)

def augment(args):

    inFile = args.infile
    outfile = args.outfile
    operation = args.operation
    max_rotate = args.maxrot

    ud_reader = conllud.conllUD(inFile)
    ud_sents = ud_reader.sents
    loi = [u"nsubj", u"advmod", u"iobj", u"obj", u"obl", u"advcl", u"aux", u"punct", u"cop", u"mark", u"conj", u"csubj", u"xcomp", u"expl"]
    pl = operation
    # for predicate
    multilabs = [u"case", u"fixed", u"flat"]
    fout = codecs.open(outfile,'w','utf-8')

    for s in ud_sents:
        rotator = augmenter.rotator(s, aloi=loi, pl=pl, multilabs=multilabs, prob=1.0)
        augSents = rotator.rotate(maxshuffle=max_rotate)
        for augsent in augSents:
            for row in augsent:
                line = u"\t".join(row)
                fout.write(line)
                fout.write(u"\n")
            fout.write(u"\n")
    
    fout.close()

def create_file(args):
    print("\n\n")
    outfile = args.outfile    
    ud_reader = conllud.conllUD(outfile)
    for s in ud_reader.sents:
        line = ' '.join(s.tokenWords)
        line = line.replace(", ,", ",").replace(", .", ".").replace(", :", ":").replace(", ;", ";").replace(", !", "!").replace(", ?", "?")
        print(line)

if __name__ == "__main__":
    main()