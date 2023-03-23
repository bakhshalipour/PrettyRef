#! /usr/bin/env python3

'''
This script takes (1) a path and (2) a bib file. It checks all .tex files under
(1) and finds all the "used" citations. Then it removes unused citations from (2).
'''

import sys, os
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
    writer.indent = '    '     # Indent entries with 4 spaces instead of one
    writer.comma_first = True  # Place the comma at the beginning of the line
    with open(file_name, 'w', encoding='utf-8') as bibfile:
        bibfile.write(writer.write(bib_database))
    


def remove_unused_citations(bib_database, used_citations):
    for i, bibitem in enumerate(bib_database.entries):
        # TODO: change this. add the ones that match instead of remove unmatches
        if bibitem['ID'] not in used_citations:
            del bib_database.entries[i]

    return bib_database


def read_citations(file):
    assert os.path.exists(file)
    assert file.endswith('.tex')
    tex_file = open(file, 'r+')
    unique_citations = set()

    pattern = r'\\cite{(.*?)}'
    for line in tex_file:
        citations = re.findall(pattern, line)
        if len(citations) == 0: continue
        for c in citations:
            for individual_cite in c.strip().split(','):
                unique_citations.add(individual_cite.strip())
    return unique_citations




def read_all_tex_files(path):
    assert os.path.exists(path)

    tex_files = []
    unique_citations = set()

    for file in os.listdir(path):
        if file.endswith('.tex'):
            tex_files.append(file)
            for c in read_citations(os.path.join(path, file)):
                unique_citations.add(c)

    return tex_files, unique_citations



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="input path")
    parser.add_argument("bibfile", help="input bibfile")
    parser.add_argument("-o", "--output", help="set output bibtex file")
    args = parser.parse_args()

    if not args.path or not args.bibfile:
        print('[Error] No input file is provided. See \'{} --help\''.format(sys.argv[0]), file=sys.stderr)
        exit(1)

    print('[Progress] Reading input tex files...')
    tex_files, used_citations = read_all_tex_files(args.path)
    print('[Progress] {} tex files are read. Found {} unique citations'.format(len(tex_files), len(used_citations)))

    print('[Progress] Reading bibfile...')
    bib_database = read_bib_file(args.bibfile)
    print('[Progress] Reading bibfile done')

    print('[Progress] Removing unused citations...')
    bib_database = remove_unused_citations(bib_database, used_citations)
    print('[Progress] Removing unused citations done')

    print('[Progress] Producing output bibtex file...')
    output_filename = args.output if args.output else 'new_' + args.bibfile
    write_bib_file(bib_database, output_filename)
    print('[Progress] Produced output bibtex file to {}'.format(output_filename))

    exit(0)

