#!/usr/bin/env python3

# parsefeaturejsons.py

# classes and functions that can unpack the extracted feature files
# created by HTRC, and convert them into a .csv that is easier to
# manipulate

import csv, os, sys, bz2, random, json
from collections import Counter

import numpy as np
import pandas as pd

# import utils
currentdir = os.path.dirname(__file__)
libpath = os.path.join(currentdir, '../lib')
sys.path.append(libpath)

import SonicScrewdriver as utils

abspath = os.path.abspath(__file__)
thisdirectory = os.path.dirname(abspath)
namepath = os.path.join(thisdirectory, 'PersonalNames.txt')
placepath = os.path.join(thisdirectory, 'PlaceNames.txt')
romanpath = os.path.join(thisdirectory, 'RomanNumerals.txt')

with open(namepath, encoding = 'utf-8') as f:
    personalnames = set([x.strip().lower() for x in f.readlines()])

with open(placepath, encoding = 'utf-8') as f:
    placenames = set([x.strip().lower() for x in f.readlines()])

with open(placepath, encoding = 'utf-8') as f:
    placenames = set([x.strip().lower() for x in f.readlines()])

daysoftheweek = {'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'}
monthsoftheyear = {'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december'}

def normalize_token(token):
    ''' Normalizes a token by lowercasing it and by bundling
    certain categories together. The lists of personal and place names
    are never going to be all-inclusive; you have to be aware of that,
    and deactivate this in corpora where it could pose a problem.
    '''

    global personalnames, placenames, daysoftheweek, monthsoftheyear

    token = token.lower()
    if len(token) < 1:
        return token
    elif token[0].isdigit() and token[-1].isdigit():
        return "#arabicnumeral"
    elif token in daysoftheweek:
        return "#dayoftheweek"
    elif token in monthsoftheyear:
        return "#monthoftheyear"
    elif token in personalnames:
        return "#personalname"
    elif token in placenames:
        return "#placename"
    else:
        return token

def normalize_token_for_page(token):
    ''' Normalizes a token by lowercasing it and by bundling
    certain categories together. The lists of personal and place names
    are never going to be all-inclusive; you have to be aware of that,
    and deactivate this in corpora where it could pose a problem.
    '''

    global personalnames, placenames, daysoftheweek, monthsoftheyear, romannumerals

    if token = "I":
        return token
        # uppercase I is not usually a roman numeral!

    token = token.lower()
    if len(token) < 1:
        return token
    elif token[0].isdigit() and token[-1].isdigit():
        return "#arabicnumeral"
    elif token in daysoftheweek:
        return "#dayoftheweek"
    elif token in monthsoftheyear:
        return "#monthoftheyear"
    elif token in personalnames:
        return "#personalname"
    elif token in placenames:
        return "#placename"
    elif token in romannumerals:
        return "#romannumeral"
    else:
        return token

class VolumeFromJson:

    # Mainly a data object that contains page-level wordcounts
    # for a volume.

    def __init__(self, volumepath, volumeid):
        '''initializes a LoadedVolume by reading wordcounts from
        a json file'''

        if volumepath.endswith('bz2'):
            with bz2.open(volumepath, mode = 'rt', encoding = 'utf-8') as f:
                thestring = f.read()
        else:
            with open(volumepath, encoding = 'utf-8') as f:
                thestring = f.read()

        thejson = json.loads(thestring)
        assert thejson['id'] == volumeid
        # I require volumeid to be explicitly passed in,
        # although I could infer it, because I don't want
        #any surprises.

        self.volumeid = thejson['id']

        pagedata = thejson['features']['pages']
        self.numpages = len(pagedata)
        self.pagecounts = []
        self.totalcounts = Counter()
        self.totaltokens = 0
        self.bodytokens = 0

        self.sentencecount = 0
        self.linecount = 0
        typetokenratios = []

        chunktokens = 0
        typesinthischunk = set()
        # a set of types in the current 10k-word chunk; progress
        # toward which is tracked by chunktokens

        for i in range(self.numpages):
            thispagecounts = Counter()
            thisbodytokens = 0
            thisheadertokens = 0
            thispage = pagedata[i]

            linesonpage = int(thispage['lineCount'])
            sentencesonpage = int(thispage['body']['sentenceCount'])
            self.sentencecount += sentencesonpage
            self.linecount += linesonpage
            # I could look for sentences in the header or footer, but I think
            # that would overvalue accidents of punctuation.

            bodywords = thispage['body']['tokenPosCount']
            for token, partsofspeech in bodywords.items():
                lowertoken = token.lower()
                typesinthischunk.add(lowertoken)
                # we do that to keep track of types -- notably, before nortmalizing
                normaltoken = normalize_token(lowertoken)

                for part, count in partsofspeech.items():
                    thisbodytokens += count
                    chunktokens += count
                    thispagecounts[normaltoken] += count

                    if chunktokens > 10000:
                        typetoken = len(typesinthischunk) / chunktokens
                        typetokenratios.append(typetoken)
                        typesinthischunk = set()
                        chunktokens = 0

            headerwords = thispage['header']['tokenPosCount']
            for token, partsofspeech in headerwords.items():
                lowertoken = token.lower()
                normaltoken = "#header" + normalize_token(lowertoken)

                for part, count in partsofspeech.items():
                    thisheadertokens += count
                    thispagecounts[normaltoken] += count

            # You will notice that I treat footers (mostly) as part of the body
            # Footers are rare, and rarely interesting.

            footerwords = thispage['footer']['tokenPosCount']
            for token, partsofspeech in footerwords.items():
                lowertoken = token.lower()
                typesinthischunk.add(lowertoken)
                # we do that to keep track of types -- notably before nortmalizing
                normaltoken = normalize_token(lowertoken)

                for part, count in partsofspeech.items():
                    thisbodytokens += count
                    chunktokens += count
                    thispagecounts[normaltoken] += count

            self.pagecounts.append(thispagecounts)

            for key, value in thispagecounts.items():
                self.totalcounts[key] += value

            self.totaltokens += thisbodytokens
            self.totaltokens += thisheadertokens
            self.bodytokens += thisbodytokens


        if len(typetokenratios) < 1 or chunktokens > 5000:
            # We do this only if we have to, or if the chunk is large
            # enough to make it reasonable evidence.

            chunktokens = chunktokens + 1     # Laplacian correction aka kludge
            typetoken = len(typesinthischunk) / chunktokens

            predictedtt = 4.549e-01 - (5.294e-05 * chunktokens) + (2.987e-09 * pow(chunktokens, 2))
            # That's an empirical quadratic regression on observed data from many genres

            extrapolatedtt =  0.2242 * (typetoken / predictedtt)
            # We infer what typetoken *would* be for a 10k word chunk of this vol, given that it's
            # typetoken for an n-word chunk.

            if extrapolatedtt > 0.6:
                extrapolatedtt = 0.6
            if extrapolatedtt < 0.1:
                extrapolatedtt = 0.1
            # Let's be realistic.

            typetokenratios.append(extrapolatedtt)

        self.typetoken = sum(typetokenratios) / len(typetokenratios)
        self.sentencelength = self.bodytokens / (self.sentencecount + 1)
        self.linelength = self.totaltokens / self.linecount

        # We are done with the __init__ method for this volume.

        # When I get a better feature sample, we'll add some information about initial
        # capitalization.

    def write_volume_features(self, outpath, override = False):
        if os.path.isfile(outpath) and not override:
            print('Error: you are asking me to override an existing')
            print('file without explicitly specifying to do so in your')
            print('invocation of write_volume_features.')

        with open(outpath, mode = 'w', encoding = 'utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['feature', 'count'])
            for key, value in self.totalcounts.items():
                writer.writerow([key, value / self.totaltokens])
            writer.writerow(['#sentencelength', self.sentencelength])
            writer.writerow(['#typetoken', self.typetoken])
            writer.writerow(['#linelength', self.linelength])

    def get_volume_features(self):
        '''
        Just like write_volume_features, except we return them
        as a dictionary.
        '''

        outdict = Counter()
        if self.totaltokens < 1:
            return outdict, 0

        else:

            for key, value in self.totalcounts.items():
                outdict[key] = value / self.totaltokens
            outdict['#sentencelength'] = self.sentencelength
            outdict['#typetoken'] = self.typetoken
            outdict['#linelength'] = self.linelength

            return outdict, self.totaltokens

    def append_volume_features(self, outpath):
        ''' This is probably the way to do it. Initialize the file with
        a header, and then add a bunch of volumes to the same file,
        incorporating a column that distinguishes them by docid.
        '''

        with open(outpath, mode = 'a', encoding = 'utf-8') as f:
            writer = csv.writer(f)
            for key, value in self.totalcounts.items():
                writer.writerow([self.volumeid, key, value / self.totaltokens])
            writer.writerow([self.volumeid, '#sentencelength', self.sentencelength])
            writer.writerow([self.volumeid, '#typetoken', self.typetoken])
            writer.writerow([self.volumeid, '#linelength', self.linelength])

class PagelistFromJson:

    # A data object that contains page-level wordcounts
    # for a volume,

    def __init__(self, volumepath, volumeid):
        '''initializes a LoadedVolume by reading wordcounts from
        a json file'''

        if volumepath.endswith('bz2'):
            with bz2.open(volumepath, mode = 'rt', encoding = 'utf-8') as f:
                thestring = f.read()
        else:
            with open(volumepath, encoding = 'utf-8') as f:
                thestring = f.read()

        thejson = json.loads(thestring)
        assert thejson['id'] == volumeid
        # I require volumeid to be explicitly passed in,
        # although I could infer it, because I don't want
        #any surprises.

        self.volumeid = thejson['id']

        pagedata = thejson['features']['pages']
        self.numpages = len(pagedata)
        self.pages = []

        # in this data structure, a volume is a list of pages

        for i in range(self.numpages):
            thispage = dict()
            # each page  is a dictionary that contains categories of
            # features, most obviously wordcounts:
            thispage['tokens'] = Counter()

            thispage['totaltokens'] = 0
            thispage['totalcapitalized'] = 0
            thispage['wordsperline'] = 0
            self.pages.append(thispage)

        self.totalcounts = Counter()
        self.totaltokens = 0

        self.sentencecount = 0
        self.linecount = 0
        typetokenratios = []

        chunktokens = 0
        typesinthischunk = set()
        # a set of types in the current 10k-word chunk; progress
        # toward which is tracked by chunktokens

        for i in range(self.numpages):
            thispagecounts = Counter()
            thisbodytokens = 0
            thisheadertokens = 0
            thispage = pagedata[i]

            linesonpage = int(thispage['lineCount'])
            sentencesonpage = int(thispage['body']['sentenceCount'])
            self.sentencecount += sentencesonpage
            self.linecount += linesonpage
            # I could look for sentences in the header or footer, but I think
            # that would overvalue accidents of punctuation.

            bodywords = thispage['body']['tokenPosCount']
            for token, partsofspeech in bodywords.items():
                lowertoken = token.lower()
                typesinthischunk.add(lowertoken)
                # we do that to keep track of types -- notably, before nortmalizing
                normaltoken = normalize_token(lowertoken)

                for part, count in partsofspeech.items():
                    thisbodytokens += count
                    chunktokens += count
                    thispagecounts[normaltoken] += count

                    if chunktokens > 10000:
                        typetoken = len(typesinthischunk) / chunktokens
                        typetokenratios.append(typetoken)
                        typesinthischunk = set()
                        chunktokens = 0

            headerwords = thispage['header']['tokenPosCount']
            for token, partsofspeech in headerwords.items():
                lowertoken = token.lower()
                normaltoken = "#header" + normalize_token(lowertoken)

                for part, count in partsofspeech.items():
                    thisheadertokens += count
                    thispagecounts[normaltoken] += count

            # You will notice that I treat footers (mostly) as part of the body
            # Footers are rare, and rarely interesting.

            footerwords = thispage['footer']['tokenPosCount']
            for token, partsofspeech in footerwords.items():
                lowertoken = token.lower()
                typesinthischunk.add(lowertoken)
                # we do that to keep track of types -- notably before nortmalizing
                normaltoken = normalize_token(lowertoken)

                for part, count in partsofspeech.items():
                    thisbodytokens += count
                    chunktokens += count
                    thispagecounts[normaltoken] += count

            self.pagecounts.append(thispagecounts)

            for key, value in thispagecounts.items():
                self.totalcounts[key] += value

            self.totaltokens += thisbodytokens
            self.totaltokens += thisheadertokens
            self.bodytokens += thisbodytokens


        if len(typetokenratios) < 1 or chunktokens > 5000:
            # We do this only if we have to, or if the chunk is large
            # enough to make it reasonable evidence.

            chunktokens = chunktokens + 1     # Laplacian correction aka kludge
            typetoken = len(typesinthischunk) / chunktokens

            predictedtt = 4.549e-01 - (5.294e-05 * chunktokens) + (2.987e-09 * pow(chunktokens, 2))
            # That's an empirical quadratic regression on observed data from many genres

            extrapolatedtt =  0.2242 * (typetoken / predictedtt)
            # We infer what typetoken *would* be for a 10k word chunk of this vol, given that it's
            # typetoken for an n-word chunk.

            if extrapolatedtt > 0.6:
                extrapolatedtt = 0.6
            if extrapolatedtt < 0.1:
                extrapolatedtt = 0.1
            # Let's be realistic.

            typetokenratios.append(extrapolatedtt)

        self.typetoken = sum(typetokenratios) / len(typetokenratios)
        self.sentencelength = self.bodytokens / (self.sentencecount + 1)
        self.linelength = self.totaltokens / self.linecount

        # We are done with the __init__ method for this volume.

        # When I get a better feature sample, we'll add some information about initial
        # capitalization.

    def write_volume_features(self, outpath, override = False):
        if os.path.isfile(outpath) and not override:
            print('Error: you are asking me to override an existing')
            print('file without explicitly specifying to do so in your')
            print('invocation of write_volume_features.')

        with open(outpath, mode = 'w', encoding = 'utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['feature', 'count'])
            for key, value in self.totalcounts.items():
                writer.writerow([key, value / self.totaltokens])
            writer.writerow(['#sentencelength', self.sentencelength])
            writer.writerow(['#typetoken', self.typetoken])
            writer.writerow(['#linelength', self.linelength])

    def get_volume_features(self):
        '''
        Just like write_volume_features, except we return them
        as a dictionary.
        '''

        outdict = Counter()
        if self.totaltokens < 1:
            return outdict, 0

        else:

            for key, value in self.totalcounts.items():
                outdict[key] = value / self.totaltokens
            outdict['#sentencelength'] = self.sentencelength
            outdict['#typetoken'] = self.typetoken
            outdict['#linelength'] = self.linelength

            return outdict, self.totaltokens

    def append_volume_features(self, outpath):
        ''' This is probably the way to do it. Initialize the file with
        a header, and then add a bunch of volumes to the same file,
        incorporating a column that distinguishes them by docid.
        '''

        with open(outpath, mode = 'a', encoding = 'utf-8') as f:
            writer = csv.writer(f)
            for key, value in self.totalcounts.items():
                writer.writerow([self.volumeid, key, value / self.totaltokens])
            writer.writerow([self.volumeid, '#sentencelength', self.sentencelength])
            writer.writerow([self.volumeid, '#typetoken', self.typetoken])
            writer.writerow([self.volumeid, '#linelength', self.linelength])

if __name__ == "__main__":

    meta = pd.read_csv('/Users/tunder/Dropbox/python/train20/bzipmeta.csv', dtype = 'object', index_col = 'docid')
    for index, row in meta.iterrows():
        inpath = row['filepath']
        vol = VolumeFromJson(inpath, index)
        outpath = '/Volumes/TARDIS/work/train20/' + utils.clean_pairtree(index) + '.csv'
        vol.write_volume_features(outpath, override = True)



