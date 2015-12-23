import feedparser

feedlist =  open("feedlist.txt", 'r')

output = """<html>
        <head><title>Feed Court</title>
           <link rel='stylesheet' type='text/css' href='feedcourt.css'>
           <script src='feedcourt.js' type='text/javascript'> </script>
        </head>
        <body onload="pagelinks();">
           <div id='wrapper'>"""
for url in feedlist:
    f = feedparser.parse(url)
    site = f['feed']['title']
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
        output += """<div class='entry'>
                  <a href='%s' target='_blank'>%s</a>
                  </div>""" %(e.link, e.title)

    output += "</div>"
   

output += "</div></body></html>"
index = open("index.html", 'w')
index.write(output.encode("utf-8"))

