# PrettyRef
Making bibtex files prettier for scientific papers


## What is this?
This is a script that takes a bibtex file and produces a prettier one! It gets a bibtex file filled with items from say, *Google Scholar* and/or somewhere else, and manipulates the items. Essentially, the script provides the following features/options:

- Capitalize the title of items

- Concision: Use *et al.* instead of all authors' names, exclude trifle entries from the items (e.g., no *doi*), abbreviate venue names (e.g., *ISCA* instead of *International Symposium on Computer Architecture*)

- Check for duplicated entries (useful when the bibtex file is built by combining the bibtex files of several previous/other projects)

## Requirement
- Python 3.x
- [BibtexParser](https://bibtexparser.readthedocs.io)

## How to use

#### Help Message
    $ ./pretty_ref.py --help

#### Examples
    $ ./pretty_ref.py ref.bib -c -o output_ref.bib
Takes `ref.bib` as input, capitalizes (`-c`) the title of papers, and writes the output to `output_ref.bib`

    $ ./pretty_ref.py my_ref.bib --capitalize --et-al -t=3
Capitalizes (`--capitalize`) the items, uses *et al.* (`--et-al`) for papers with more than 3 authors (`-t=3`), writes the output to `new_my_ref.bib` file
