#!/usr/bin/env python3

import csv, os, sys
from collections import Counter

delchars = ''.join(c for c in map(chr, range(256)) if not c.isalpha())
alleraser = str.maketrans('', '', delchars)

## Translation map that erases most punctuation, including hyphens.
Punctuation = '.,():-—;"!?•$%@“”#<>+=/[]*^\'{}_■~\\|«»©&~`£·'
mosteraser = str.maketrans('', '', Punctuation)

lexicon = set()
with open('MainDictionary.tsv', encoding = 'utf-8') as f:
    for line in f:
        fields = line.split('\t')
        lexicon.add(fields[0])

def rejoin_hyphens(listoflines):
    fixedlist = list()

    for idx, line in enumerate(listoflines):
        line = line.strip()
        if line.endswith('-') and (idx + 1) < numpages:
            thesewords = line.split()
            nextline = listoflines(idx + 1)
            nextwords = nextline.split()
            theselen = len(thesewords)
            nextlen = len(nextwords)
            if theselen > 0 and nextlen > 0:
                lastword = thesewords[theselen -1]
                if len(lastword) > 0:
                    fixedword = lastword[0:-1]
                # that removes the hyphen
                firstword = nextwords[0]
                rejoined = firstword + firstword
                if rejoined.lower() in lexicon:
                    thesewords[-1] = rejoined
                    nextwords = nextwords[1: ]

def strip_punctuation(astring):
    global punctuple
    keepclipping = True
    suffix = ""
    while keepclipping == True and len(astring) > 1:
        keepclipping = False
        if astring.endswith(punctuple):
            suffix = astring[-1:] + suffix
            astring = astring[:-1]
            keepclipping = True
    keepclipping = True
    prefix = ""
    while keepclipping == True and len(astring) > 1:
        keepclipping = False
        if astring.startswith(punctuple):
            prefix = prefix + astring[:1]
            astring = astring[1:]
            keepclipping = True
    return(prefix, astring, suffix)

def zap_all_nonalpha(word):
    global alleraser
    return word.translate(alleraser)





