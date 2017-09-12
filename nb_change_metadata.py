"""This script modifies metadata of a Jupyter notebook

No data is modified in place: a new directory is created with the modified
output. That directory is identified by a ``_nb_change_metadata`` suffix.

TODO: Consider changing this into a script to edit arbitrary json files.

"""

import os
import shutil
import fnmatch
import json
import argparse
import sys
from collections import OrderedDict


def list_all_notebooks(rootdir):
    "List all Jupyter Notebooks under rootdir and its subdirs."
    for dirname, _, files in os.walk(rootdir):
        notebooks = (os.path.join(dirname, f) for f in files if fnmatch.fnmatch(f, '*.ipynb'))
        yield from notebooks


def nbk_modify_metadata(nbk_fpath, metadata_updates):
    "Replace metadata of notebook at nbk_fpath."
    with open(nbk_fpath) as f:
        nbk_data = json.load(f, object_hook=OrderedDict)
        nbk_data['metadata'].update(metadata_updates)
    with open(nbk_fpath) as f:
        json.dump(nbk_data, f, indent=2)


def parse_args(argv=None):
    "Parse input arguments."
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(dest='rootdir', metavar='rootdir', nargs=1)
    parser.add_argument('-u', '--update', metavar='key:val', required=True,
                        dest='updates', action='append', nargs='+',
                        help='notebook metadata updates in key:val pairs')
    args = parser.parse_args(argv)
    return args


def main(args):
    "Execute the main script: replace metadata in notebooks."
    # Make a working copy of the root directory
    rootdir = os.path.abspath(args.rootdir)
    new_rootdir = rootdir + '_nb_change_metadata'
    shutil.copytree(args.rootdir, new_rootdir)
    # Build the updates dictionary
    updates = dict(keyval.split(':') for keyval in args.updates)
    # Update metadata of notebooks
    notebooks = list_all_notebooks(new_rootdir)
    for nbk in notebooks:
        nbk_modify_metadata(nbk, updates)
    # If we got here, then there were no errors.
    return 0


if __name__ == "__main__":
    args = parse_args()
    status = main(args)
    sys.exit(status)
