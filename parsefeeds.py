import feedparser
import datetime
from random import shuffle 

feedlist =  open("feedlist.txt", 'r')
#now = datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p")
now = datetime.datetime.utcnow().isoformat()

output = """<html>
        <head><title>Feed Court</title>
           <meta http-equiv="Content-Type" content="text/html; charset=utf8" />
           <meta http-equiv="refresh" content="600">
           <link rel='stylesheet' type='text/css' href='feedcourt.css'>
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
    f = feedparser.parse(url)
    # to debug which feed might be failing, uncomment this
    #print f['feed']['title']
    if f['feed']['title']:
    	site = f['feed']['title']
    else:
	site = f['feed']
    # make id by getting rid of spaces and non-alphanumerics
    siteid = filter(str.isalnum, site.strip().replace(" ","").encode("utf-8"))
    moreid = "more" + siteid 
    sitelink = f['feed']['link']
    output += """<div class='section' id='%s'>
                <div class='section_head'>
                <h2><a href='%s'>%s</a></h2>
                <div class='more' id='%s'> more </div>
                </div><div></div>""" %(siteid, sitelink, site, moreid) 
    for e in f.entries:
        # make main page link
        output += """<div class='entry'>
                  <a href='%s' target='_blank'>%s</a>
                  </div>""" %(e.link, e.title)
        # generate jumble page link for later
        jumblerow = """<span class='jumble'> <a href='%s' target='_blank'>%s</a><span class='jumblesite'><a href='%s'> ( %s ) </a></span></span> | """ %(e.link, e.title, sitelink, site)
        all_entries.append(jumblerow)

    output += "</div>"
   

output += "</div><div id='footer'> source code: <a href='https://github.com/bendybendy/feedcourt'> https://github.com/bendybendy/feedcourt </a> </body></html>"
index = open("index.html", 'w')
index.write(output.encode("utf-8"))

# finish the jumble page 
shuffle(all_entries)                   
for row in all_entries:   
    joutput +=row


joutput += "</div><div id='footer'> source code: <a href='https://github.com/bendybendy/feedcourt'> https://github.com/bendybendy/feedcourt </a> </body></html>"
index = open("jumble.html", 'w')
index.write(joutput.encode("utf-8"))

