#!/usr/bin/env python

import os
import sys
import errno
import hashlib
import urllib2
import json

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


baseurl = 'http://localhost:8000/webexporter/'
# baseurl = 'https://lincs-omero.hms.harvard.edu/webexporter/'

outdir = 'test'
mkdir(outdir)

response = urllib2.urlopen(
    # baseurl + 'get_files_for_obj/plate/3111'
    # baseurl + 'get_files_for_obj/dataset/201'
    # baseurl + 'get_files_for_obj/image/51'
    baseurl + 'get_files_for_obj/project/102'
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
