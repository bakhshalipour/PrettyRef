#! /usr/bin/env python3

import sys
import argparse

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import homogenize_latex_encoding
from bibtexparser.customization import convert_to_unicode

from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase

import re
import string


def read_bib_file(file_name):
    with open(file_name, encoding='utf-8') as bibtex_file:
        parser = BibTexParser(common_strings=True)
        bib_database = bibtexparser.load(bibtex_file, parser=parser)
        return bib_database
    


def write_bib_file(bib_database, file_name='output.bib'):
    writer = BibTexWriter()
    writer.indent = '    '     #Indent entries with 4 spaces instead of one
    writer.comma_first = True  #Place the comma at the beginning of the line
    with open(file_name, 'w', encoding='utf-8') as bibfile:
        bibfile.write(writer.write(bib_database))
    


def convert_title(original_title):
    new_title = re.sub(r'\\([^\s]+)', '', original_title)   #Remove patterns like \&
    new_title = re.sub(r'\W+', '', new_title)
    new_title = new_title.lower()
    return new_title



def check_for_duplicate(bib_database):
    titles = {}
    for bibitem in bib_database.entries:
        if not 'title' in bibitem.keys():
            print("[Warning]", bibitem['ID'], "has no title!")
        else:
            title = convert_title(bibitem['title'])
            if title in titles.keys():
                print("[Info] Duplicated entries: {} and {}".format(titles[title], bibitem['ID']))
            titles[title] = bibitem['ID']



def capitalize_judiciously(title):
    #Python's built-in functions like title() and capwords() wouldn't
    #immediately work here. E.g., prepositions, CMP should not be converted to Cmp.

    #I somewhat follow this: <http://www.superheronation.com/2011/08/16/words-that-should-not-be-capitalized-in-titles/>
    articles = ['a', 'an', 'the']
    coordinate_conjunctions = ['for', 'and', 'nor', 'but', 'or', 'yet', 'so']
    prepositions = ['at', 'by', 'for', 'from', 'of', 'on', 'to', 'with', 'without', 'in', 'but']

    dont_capitalize = articles + coordinate_conjunctions + prepositions

    strings = title.split(':')
    new_strings = []

    for string in strings:
        words = string.split()
        new_words = []

        for word in words:
            new_word = word

            #The first/last word should be capitalized even if it is, say, an article.
            if not word.lower() in dont_capitalize or len(new_words) == 0 or len(new_words) == len(words) - 1:
                new_word = word[:1].upper() + word[1:]

            if not '-' in new_word:
                new_words.append(new_word)
                continue

            #E.g., Low-cost --> Low-Cost
            subwords = new_word.split('-')
            new_subwords = []

            for subword in subwords:
                new_subwords.append(subword[:1].upper() + subword[1:])

            new_word = "-".join(new_subwords)

            new_words.append(new_word)

        new_strings.append(" ".join(new_words))

    return ": ".join(new_strings)



def capitalize_titles(bib_database):
    for bibitem in bib_database.entries:
        if 'title' in bibitem.keys():
            #Final titles in the output file would be sth like this: title = {{A Low-Overhead Solution for a Problem}}
            bibitem['title'] = '{' + capitalize_judiciously(bibitem['title'].replace('{', '').replace('}', '')) + '}'
    return bib_database



def remove_further_names(authors, threshold):
    names = authors.split('and')
    if len(names) < threshold:
        return authors
    return names[0] + 'and others'



def make_et_al(bib_database, threshold=3):
    for bibitem in bib_database.entries:
        if 'author' in bibitem.keys():
            x = bibitem['author']
            bibitem['author'] = remove_further_names(bibitem['author'], threshold)
    return bib_database



def make_brief(bib_database):

    #Keys I've frequently seen so far
    #{'author', 'howpublished', 'ID', 'issue_date', 'booktitle', 'ENTRYTYPE',
    #'volume', 'number', 'journal', 'numpages', 'edition', 'year', 'location',
    #'organization', 'pages', 'articleno', 'month', 'address', 'title', 'publisher',
    #'isbn', 'doi', 'issn', 'issue_date', 'keywords', 'url', 'series'}

    remove_list = ['volume', 'number', 'numpages', 'edition', 'location',
    'organization', 'pages', 'articleno', 'month', 'address', 'publisher', 'isbn',
    'doi', 'issn', 'issue_date', 'keywords', 'url', 'series', 'publisher']

    for i, bibitem in enumerate(bib_database.entries):
        for k in remove_list:
            if not k in bibitem.keys():
                continue
            del bib_database.entries[i][k]

    return bib_database



def get_abbr_name(venue_name):
    if not '(' in venue_name:
        return venue_name   #No abbreviation is provided

    if not ')' in venue_name:
        print('[Warning] Strange bibitem: venue_name = {}'.format(venue_name), file=sys.stderr)
        return venue_name   #Don't bother!

    return venue_name[venue_name.find("(")+1 : venue_name.rfind(")")]



def make_venue_abbr(bib_database):
    for i, bibitem in enumerate(bib_database.entries):
        if 'journal' in bibitem.keys():
            bib_database.entries[i]['journal'] = get_abbr_name(bibitem['journal'])
        elif 'booktitle' in bibitem.keys():
            bib_database.entries[i]['booktitle'] = get_abbr_name(bibitem['booktitle'])

    return bib_database



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="set input bibtex file")
    parser.add_argument("-c", "--capitalize", help="capitalize titles", action="store_true")
    parser.add_argument("-e", "--et-al", help="use et al. instead of full list of authors", action="store_true")
    parser.add_argument("-t", "--threshold", help="use et al. for papers with >= THRESHOLD", type=int, default=3)
    parser.add_argument("-b", "--brief", help="keep only important fields in the bibitems", action="store_true")
    parser.add_argument("-a", "--abbreviate", help="abbreviate venue names", action="store_true")
    parser.add_argument("-o", "--output", help="set output bibtex file")
    args = parser.parse_args()

    if not args.input:
        print('[Error] No input file is provided. See \'{} --help\''.format(sys.argv[0]), file=sys.stderr)
        exit(1)

    print('[Progress] Reading input file...')
    bib_database = read_bib_file(args.input)
    print('[Progress] Reading input file done')

    print('[Progress] Checking for duplicated bibitems...')
    check_for_duplicate(bib_database)
    print('[Progress] Checking for duplicated bibitems done')

    if args.capitalize:
        print('[Progress] Capitalizing titles...')
        bib_database = capitalize_titles(bib_database)
        print('[Progress] Capitalizing titles done')

    if args.et_al:
        print('[Progress] Converting publications with >= {} authors to et al. format...'.format(args.threshold))
        bib_database = make_et_al(bib_database, threshold=args.threshold)
        print('[Progress] Converting to et al. format done')

    if args.brief:
        print('[Progress] Excluding unimportant fields from bibitems...')
        bib_database = make_brief(bib_database)
        print('[Progress] Excluding unimportant fields done')

    if args.abbreviate:
        print('[Progress] Abbreviating venue names...')
        bib_database = make_venue_abbr(bib_database)
        print('[Progress] Abbreviating done...')

    print('[Progress] Producing output bibtex file...')
    output_filename = args.output if args.output else 'pretty_' + args.input
    write_bib_file(bib_database, output_filename)
    print('[Progress] Produced output bibtex file to {}'.format(output_filename))

    exit(0)

