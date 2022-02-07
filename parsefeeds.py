import feedparser
import datetime
from random import shuffle 

import re
import html
from bs4 import BeautifulSoup

import argparse
import pathlib

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

def get_entry_metadata (e):
    """
    We're looking for 4 items which we will return in a list (or the empty string)
    1. The target link
    2. thumbnail image
    3. comments link
    4. tooltip text ... plain text ONLY!
    """

    thumbnail = None
    comments = None
    tooltip = None
    link = e.link
    
    if "media_thumbnail" in e:
        if "url" in e.media_thumbnail[0]:
            thumbnail = e.media_thumbnail[0]["url"]

    if thumbnail is None and "media_content" in e and len(e.media_content[0]) > 0:
        if "url" in e.media_content[0]:
            thumbnail = e.media_content[0]["url"]
    
    if "comments" in e:
        comments = e.comments

    if "content" in e or "description" in e:
        if "content" in e:
            soup = BeautifulSoup(e.content[0]["value"], 'html.parser')
        else:
            soup = BeautifulSoup(e.description, 'html.parser')
        
        if thumbnail is None and soup.find('img'):
            img = soup.find('img')
            if "src" in img.attrs:
                thumbnail = img.attrs["src"]

        [i.replace_with(i['alt']) for i in soup.find_all('img', alt=True)]
        tooltip = soup.get_text()

        reddit = soup.find_all('a')[-2:]
        if len(reddit) == 2 and reddit[0].get_text() == '[link]' and reddit[1].get_text() == '[comments]':
            link = reddit[0].attrs["href"]
            comments = reddit[1].attrs["href"]
            tooltip = tooltip[:-(len("[link] [comments] "))] # Remove extra text at the end for Reddit

    # tooltips get too long....
    if tooltip:
        t = tooltip.split(" ")
        if len(t) > 50:
            tooltip = " ".join(t[:50]) + "..."
        else:
            tooltip = " ".join(t[:50])

    # Filter out images that come from feedburner
    if tooltip and "feeds.feedburner.com" in tooltip:
        tooltip = None

    return (link, thumbnail, comments, tooltip)

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--output', help="Specify the output folder", type=pathlib.Path, default=pathlib.Path('.'))
parser.add_argument('-f', '--feedlist', help="The text file of feeds to load", type=argparse.FileType('r'), default="feedlist.txt")
parser.add_argument('-i', '--input', help="The folder of cached RSS feeds to use", type=pathlib.Path, default=pathlib.Path('.'))
parser.add_argument('-c', '--cached', help="Use a cached directory of RSS feeds instead", action="store_true")
parser.add_argument('-v', '--verbose', help="Be more verbose", action="store_true")
args = parser.parse_args()

feedlist = args.feedlist
#now = datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p")
now = datetime.datetime.utcnow().isoformat()

pattern = re.compile('[\W_]+')
noquote = re.compile("[\"\']")

output = """<html>
        <head><title>Fresh News</title>
           <meta http-equiv="Content-Type" content="text/html; charset=utf8" />
           <link rel='stylesheet' type='text/css' href='feedcourt.css'>
           <link rel='stylesheet' type='text/css' href='tooltip.min.css'>
           <link href="apple-touch-icon.png" rel="apple-touch-icon" />
           <link href="apple-touch-icon-76x76.png" rel="apple-touch-icon" sizes="76x76" />
           <link href="apple-touch-icon-120x120.png" rel="apple-touch-icon" sizes="120x120" />
           <link href="apple-touch-icon-152x152.png" rel="apple-touch-icon" sizes="152x152" />
           <link href="apple-touch-icon-180x180.png" rel="apple-touch-icon" sizes="180x180" />
           <link href="icon-hires.png" rel="icon" sizes="192x192" />
           <link href="icon-normal.png" rel="icon" sizes="128x128" />
           <script src='feedcourt.js' type='text/javascript'> </script>
        </head>
        <body onload="loadroutine();">
           <div id='header'><h1>Feed Court</h1>
                <p> |  a wall of text rss aggregator  |  updated: <span id='utcupdate'>%s</span> | 
           """ %now

#init list for jumbling entries  
all_entries = []
# make a copy of the header for the jumble page 
joutput = output

#start the wrapper divs and header  
output +="<span class='sorter'><a href='./jumble.html'> jumble </a> </span></p></div> <div id='wrapper'>" 
joutput +="<span class='sorter'><a href='./'> sort </a></span> </p></div> <div id='jumblewrapper'>" 

for url in feedlist:
    if url[0] == '#':
        url = url[1:]
    if args.cached and url[0] != '!':
        cachefile = str(args.input.resolve()) + '/' + pattern.sub('', url.strip()) + ".rss"
        if args.verbose:
            print (cachefile)
        f = feedparser.parse(cachefile)
    else:
        if url[0] == '!':
            url = url[1:]
        f = feedparser.parse(url)

    if "title" in f['feed'] and f['feed']['title']:
        site = f['feed']['title']
    else:
        site = f['feed']
    if args.verbose:
        print (site)
    # make id by getting rid of spaces and non-alphanumerics
    siteid = pattern.sub('', site.strip().replace(" ",""))
    moreid = "more" + siteid 
    sitelink = f['feed']['link']
    output += """<div class='section' id='%s'>
                <div class='section_head'>
                <h2><a href='%s'>%s</a></h2>
                <div class='more' id='%s'> more </div>
                </div><div></div>""" %(siteid, sitelink, site, moreid) 
    for e in f.entries:

        # make main page link
        thumbnail = comments = tooltip = ""
        entry = get_entry_metadata (e)

        if entry[1]:
            thumbnail = """<div class='iconholder'><span class='icon' style='background-image: url("%s");'></span></div>
            """ %(noquote.sub('', entry[1]))

        if entry[2]:
            comments = """<div class='comments'><a href='%s' target='_blank'>Comments &gt;</a></div>""" %(noquote.sub('', entry[2]))
        
        # Add tooltips, but enact a text length (not just word length)
        if entry[3]:
            tooltip = """ data-tooltip='%s' aria-describedby='tooltipText' tabindex='0'""" %(html.escape(entry[3][:1000]))

        output += """<div class='entry'>
                  <a href='%s' target='_blank'%s>%s%s</a>
                  %s
                  </div>""" %(entry[0], tooltip, thumbnail, e.title, comments)
        # generate jumble page link for later
        jumblerow = """<span class='jumble'> <a href='%s' target='_blank'>%s</a><span class='jumblesite'><a href='%s'> ( %s ) </a></span></span> | """ %(entry[0], e.title, sitelink, site)
        all_entries.append(jumblerow)

    output += "</div>"

output += """</div><div id='footer'> 
             source code: <a href='https://github.com/bendybendy/feedcourt'> https://github.com/bendybendy/feedcourt </a>
             <div class='tooltip-container' role='alertdialog' id='tooltipText' aria-hidden='true' aria-live='polite'></div>
             <script defer src='tooltip.min.js' type='text/javascript'></script>
            </body></html>"""
index = open(str(args.output.resolve()) + "/index.html", 'w')
index.write(output)

# finish the jumble page 
shuffle(all_entries)                   
for row in all_entries:   
    joutput +=row

joutput += "</div><div id='footer'> source code: <a href='https://github.com/bendybendy/feedcourt'> https://github.com/bendybendy/feedcourt </a> </body></html>"
index = open(str(args.output.resolve()) + "/jumble.html", 'w')
index.write(joutput)

