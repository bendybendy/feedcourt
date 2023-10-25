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

class fakeRequest:
  status_code = 200
  text = ""

for url in feedlist:
    if url[0] == '#' or url[0] == '!':
        continue

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
        try:
            r = requests.get(url.strip(), headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0',
                                                   'Accept-Encoding': 'gzip, deflate',
                                                   'Accept': 'application/atom+xml,application/rdf+xml,application/rss+xml,application/x-netcdf,application/xml;q=0.9,text/xml;q=0.2,*/*;q=0.1',
                                                   'A-Im': 'feed'})
        except Exception as e:
            r.status_code = 503 # Just assume a timeout or something

    # We only care if the feed is available
    if r.status_code == 200:
        # And can be parsed correcty
        try:
            f = feedparser.parse(r.text.encode('utf-8', 'surrogateescape').decode('utf-8'))

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
                print (url.strip() + " : Feed didn't have a title, likely an error (no update)")
        except Exception as e:
            if args.verbose:
                print ("   Feed is invalid, likely a bad character encoding.")
