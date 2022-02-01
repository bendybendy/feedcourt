"""
    The goal of this script is to read through the list of feeds
    then pull the latest version. If it is available and updated, 
    cache the feed in a known local path for the parsing script
    to read.

    FUTURE: Record in the database each time the cache is updated for a feed and 
    failures

    FUTURE: Process links in the database for future analysis/search engine
"""
import requests
import feedparser

import re
import html
from bs4 import BeautifulSoup

import argparse
import pathlib

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--output', help="Specify the output folder", type=pathlib.Path, default=pathlib.Path('.'))
parser.add_argument('-f', '--feedlist', help="The text file of feeds to load", type=argparse.FileType('r'), default="feedlist.txt")
parser.add_argument('-v', '--verbose', help="Be more verbose", action="store_true")
args = parser.parse_args()

feedlist = args.feedlist

pattern = re.compile('[\W_]+')
noquote = re.compile("[\"\']")

ACCEPT_HEADER = "application/atom+xml,application/rdf+xml,application/rss+xml,application/x-netcdf,application/xml;q=0.9,text/xml;q=0.2,*/*;q=0.1"
ACCEPT_LANG = "en-US,en;q=0.5"
USER_AGENT = "UniversalFeedParser/%s +http://feedparser.org/" % feedparser.__version__
USER_AGENT = "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:96.0) Gecko/20100101 Firefox/96.0"

class fakeRequest:
  status_code = 200
  text = ""

for url in feedlist:
    cachefile = str(args.output.resolve()) + '/' + pattern.sub('', url) + ".rss"
    if args.verbose:
        print (url.strip())
        print ("  " + cachefile)

    # Check to see if this is a local file
    if url.strip().startswith("file:///"):
        r = fakeRequest()
        with open (url.strip()[7:], 'r') as f:
            r.text = f.read()
    else:
        r = requests.get(url.strip(), headers={'user-agent': USER_AGENT, 'accept': ACCEPT_HEADER, 'accept-language': ACCEPT_LANG})

    # We only care if the feed is available
    if r.status_code == 200:
        # And can be parsed correcty
        f = feedparser.parse(r.text)

        if args.verbose:
            print ("  " + str(f.bozo))
            if f.bozo:
                print ("  " + "Warning or error found! Will still update")
                print ("    " + f.bozo_exception.getMessage())
                print ("    " + str(f.bozo_exception.getLineNumber()))
                print ("    " + r.text)

        if "title" in f['feed'] and f['feed']['title']:
            site = f['feed']['title']
        else:
            site = f['feed']

        if isinstance(site, str):
            with open(cachefile, 'w') as o:
                o.write(r.text)
        elif args.verbose:
            print ("  Feed didn't have a title, likely an error (no update)")
        else:
            print (url.strip() + " : bad update")
 
