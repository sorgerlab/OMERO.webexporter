#!/usr/bin/env python

import os
import sys
import errno
import hashlib
import urllib2
import json
import argparse

parser = argparse.ArgumentParser(
    description='Download files for specified OMERO object'
)
parser.add_argument(
    'baseurl',
    type=str,
    help='The base URL of the server. e.g. "https://example.com"'
)
parser.add_argument(
    'type',
    type=str,
    choices=set(['project', 'dataset', 'image', 'screen', 'plate']),
    help='The type of object to download, e.g. "plate" or "dataset"'
)
parser.add_argument(
    'id',
    type=int,
    help='The ID of the object to download, e.g. "123"'
)
parser.add_argument(
    'outdir',
    type=str,
    help='The directory to write to, e.g. "output_dir"'
)

args = parser.parse_args()

def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def sha1file(path):
    sha1 = hashlib.sha1()
    f = open(path, 'rb')
    try:
        sha1.update(f.read())
    finally:
        f.close()
    return sha1.hexdigest()

def downloadfile(url, outfile):
    try:
        f = urllib2.urlopen(url)
        print "%s [Downloading]" % url

        with open(outfile, "wb") as local_file:
            local_file.write(f.read())

    except urllib2.HTTPError, e:
        print "HTTP Error:", e.code, url
    except urllib2.URLError, e:
        print "URL Error:", e.reason, url


baseurl = "%s/webexporter/" % args.baseurl
outdir = args.outdir

mkdir(outdir)

response = urllib2.urlopen(
    "%sget_files_for_obj/%s/%i" % (baseurl, args.type, args.id)
)
files = json.load(response)

for f in files:
    outfile = os.path.join(outdir, f['name'])

    # If this fils is already present
    if os.path.isfile(outfile):
        # If the hash is correct, continue
        if sha1file(outfile) == f['hash']:
            print "%s (%s) [OK]" % (f['id'], outfile)
            continue
        # Otherwise delete it before attempting to download again
        else:
            print "%s (%s) [Removing]" % (f['id'], outfile)
            os.remove(outfile)

    # Download the file
    downloadfile(baseurl + 'download_file/%s' % f['id'], outfile)

    # Check the hash to ensure the file has downloaded correctly,
    # Throw an errior
    if sha1file(outfile) != f['hash']:
        print 'Error downloading "%s", please retry' % f['id']
        sys.exit(1)
