# Fresh News 

Live at: [xkahn.com](https://xkahn.com/)

I missed the old Popurls site -- [Popurls](http://web.archive.org/web/20151031011257/http://popurls.com/) -- and don't like the replacement [Upstract](https://upstract.com/) 

Ben Donnelly did some of the hard work of replicating the Popurls site at [http://feedcourt.bendonnelly.com/](http://feedcourt.bendonnelly.com/). He published his code on [Github](https://github.com/bendybendy/feedcourt).

I took his initial code and made a number of modifications:

## UI:

 * Make fonts bigger for desktop
 * Alter the MORE buttons to work even if the page is still loading
 * Add an image preview for news items, if available
 * Add secondary content on items (comments typically) if available
 * Add a tooltip on hover with any additional details
 * Add a "freshness" score for the feed to highlight broken feeds

## Backend

 * Split generation into 3 steps: feed loading, feed caching, and page construction

### Feed loading

 * Add non-RSS support for Buzzfeed after their RSS feeds stopped updating 1/23/2024
 * Add non-RSS support for Digg after their RSS feeds went away some time in the distant past
 * Add support for "unstable" RSS feeds that tend to go down often by silently allowing their failures
 * For more stable RSS feeds, yell loudly when there is a problem
 * Add a verbose option to feed loading to aid debugging when things go wrong

### Feed caching

 * Store the last known good load of followed feeds
 * Cache is currently kept off the web server, but this could be used to update feeds on the page using the local feed store

### Page construction

 * Support the UI changes above
 * Add special support for reddit feeds to display:
   * Author of the post
   * subreddit of the post
   * Display links to old.reddit.com instead of www.reddit.com
   * Add support for Reddit images and videos

## Requires
[Python feedparser](http://pythonhosted.org/feedparser/introduction.html)

