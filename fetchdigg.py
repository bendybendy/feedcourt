import re
import requests
from bs4 import BeautifulSoup

page = requests.get("https://digg.com/trending/render/stories?from=0&size=20")
rss = open("/tmp/digg.rss", "w")

header = """<rss xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:media="http://search.yahoo.com/mrss/" xmlns:atom="http://www.w3.org/2005/Atom" version="2.0">
  <channel>
  <title>Digg Top Stories Today</title>
  <link>http://digg.com/view/all/popular/today</link>
  <description>Top stories today, parsed from digg.com</description>
  <language>en-us</language>
  <generator>diggtoday.sh</generator>
  <ttl>60</ttl>
"""
rss.write(header)

footer = """</channel>
</rss>"""

entries = page.json()

for e in entries["items"]:
    soup = BeautifulSoup(e["html"], 'html.parser')

    title = """<title>%s</title>""" %(soup.find("h2", class_="headline").get_text(strip=True))
    l = soup.find("a", itemprop="url").attrs["href"]
    if l[0] == '/':
        l = "https://digg.com" + l
    link  = """<link>%s</link>""" %(l)
    plink = """<guid isPermaLink="true">%s</guid>""" %(l)
    atom  = """<atom:link href="%s" rel="standout"/>""" %(l)
    d = soup.find("div", itemprop="description").get_text(strip=True) + " | " + re.sub("\s+", " ", soup.find("div", class_="metadata").get_text())
    description = """<description>%s</description>""" %(d)
    creator = """<dc:creator>%s<dc:creator>""" %(soup.find_all("a", itemprop="keywords")[0].get_text(strip=True))
    pub = """<pubDate>%s</pubDate>""" %(soup.find("time").attrs["datetime"])
    mediac = """<media:content medium="image" url="%s"/>""" %(soup.find("img").attrs["src"])
    mediad = """<media:description>%s</media:description>""" %(d)

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
