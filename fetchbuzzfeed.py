import re
import requests
import json

from bs4 import BeautifulSoup

from datetime import datetime, timezone
local_time = datetime.now(timezone.utc)
build_time = local_time.strftime("%a, %d %b %Y %H:%M:%S %z")

page = requests.get("https://www.buzzfeed.com/")
soup = BeautifulSoup(page.text, 'html.parser')

l = soup.find(id='__NEXT_DATA__')

y = json.loads(l.text)

rss = open("buzzfeed.rss", "w")

header = """<rss xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:media="http://search.yahoo.com/mrss/" xmlns:snf="http://www.smartnews.be/snf" version="2.0">
<channel>
<title>BuzzFeed - Trending</title>
<link>https://www.buzzfeed.com/index</link>
<atom:link href="https://www.buzzfeed.com/index.xml" rel="self"/>
<language>en</language>
<copyright>Copyright 2024 BuzzFeed, Inc.</copyright>
<description>BuzzFeed has breaking news, vital journalism, quizzes, videos, celeb news, Tasty food videos, recipes, DIY hacks, and all the trending buzz you’ll want to share with your friends. Copyright BuzzFeed, Inc. All rights reserved.</description>
<lastBuildDate>{}</lastBuildDate>
<managingEditor>editor@buzzfeed.com (https://www.buzzfeed.com/about)</managingEditor>
<webMaster>editor@buzzfeed.com (https://www.buzzfeed.com/about)</webMaster>
<image>
<url>https://webappstatic.buzzfeed.com/static/images/public/rss/logo.png</url>
<title>BuzzFeed - Top Stories</title>
<link>https://www.buzzfeed.com/index</link>
</image>""".format(build_time)

rss.write(header)

footer = """</channel>
</rss>"""

items = y["props"]["pageProps"]["moreStories"]

for e in items:
    title = """<title>%s</title>""" %(e["name"])
    l = e["source_uri"]
    if l[0] == '/':
        l = "https://www.buzzfeed.com" + l
    link  = """<link>%s</link>""" %(l)
    plink = """<guid isPermaLink="true">%s</guid>""" %(l)
    atom  = """<atom:link href="%s" rel="standout"/>""" %(l)
    description = """<description>%s</description>""" %(e["description"])
    creator = """<dc:creator>%s</dc:creator>""" %(e["authors"][0]["name"])
    pub = """<pubDate>%s</pubDate>""" %(e["created_at"])
    thumbs = e["thumbnails"][0]["sizes"]
    thumb = [thumb for thumb in thumbs if thumb["size"] == "small"][0]
    mediac = """<media:content medium="image" url="%s"/>"""%(thumb["url"])
    if "alt_text" in thumb:
       mediad= """<media:description>%s</media:description>""" %(thumb["alt_text"])
    else:
       mediad = ""

    out = """<item>
      %s
      %s
      %s
      %s
      %s
      %s
      %s
      %s
      %s
    </item>""" %(title,link, plink, atom, description, creator, pub, mediac, mediad)

    rss.write(out)

rss.write(footer)
rss.close()
