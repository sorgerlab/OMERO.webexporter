#!/usr/bin/env python

import os
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
        print "downloading " + url

        with open(outfile, "wb") as local_file:
            local_file.write(f.read())

    except urllib2.HTTPError, e:
        print "HTTP Error:", e.code, url
    except urllib2.URLError, e:
        print "URL Error:", e.reason, url


baseurl = 'http://localhost:8000/webexporter/'
outdir = 'test'
mkdir(outdir)

response = urllib2.urlopen(
    baseurl + 'get_files_for_obj/image/251'
)
files = json.load(response)

for f in files:
    outfile = os.path.join(outdir, f['name'])
    print f['id'], outfile
    downloadfile(baseurl + 'download_file/%s' % f['id'], outfile)
