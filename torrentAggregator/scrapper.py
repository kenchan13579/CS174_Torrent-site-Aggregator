import re
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from datetime import date, timedelta
## Global var
PB_DOMAIN = "http://thepiratebay.la"
PB_SEARCH_URL = PB_DOMAIN + "/search/"
KICKASS_DOMAIN = "http://kickasstorrents.video"
KICKASS_SEARCH_URL = KICKASS_DOMAIN + "/usearch/"
# scrape data from piratebay
def piratebayScrapper(query  , url=None):
    result = []
    searchURL = ""
    if url is None:
        res = re.match( r'\W*([a-zA-Z0-9\s]*)\W*' , query)
        if res.group(1) == "" : # if no pattern is matched , exit
            return
        searchURL = PB_SEARCH_URL + res.group(1).strip() + "/0/99/200"
        print(searchURL)
    else:
        searchURL = url
        print(url)
    req = Request(searchURL, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    soup = BeautifulSoup(webpage, "html.parser")
    rows = soup.select("tr")[1:] # get rid of the header row
    for row in rows:
        torrent = {} # an torrent obj
        newSoup = BeautifulSoup(str(row),"html.parser")
        link = newSoup.select("a.detLink")[0]
        torrent["title"] = link.string
        torrent["link"] = PB_DOMAIN + link["href"]
        sizeInfo = newSoup.select("font.detDesc")[0].contents
        if len(sizeInfo) == 4:
        #hard code for case when there is new video which will display as XX min ago
        # with <b> tag
            torrent["size"] = newSoup.select("font.detDesc b")[0].string
            res = re.match(r".*Size\s*(.*?),",sizeInfo[2])
            torrent["uploadTime"] = res.group(1).strip()
        else:
            sizeInfo = sizeInfo[0]
            res = re.match(r"Uploaded\s*(.*?),\s*Size(.*?),",sizeInfo);
            torrent["size"] = res.group(2).strip()
            torrent["uploadTime"] = res.group(1).strip()
        seedsAndLeech = newSoup.find_all('td',attrs={'align':'right'})
        torrent["seeds"] = re.findall(">(.*?)<" , str(seedsAndLeech[0]))
        torrent["leeches"] = re.findall(">(.*?)<" , str(seedsAndLeech[1]))

        theComment = newSoup.find('img', src="//thepiratebay.la/static/img/icon_comment.gif")
##        print(theComment)
        commentPattern = "title=\"This torrent has (.*?) comments.\""
        theComment = re.findall(commentPattern, str(theComment))
        torrent["numOfComments"] = "".join(theComment)
        if not theComment:
            torrent["numOfComments"] = "0"
        result.append(torrent) # add to the result
    if url is None:
        pagination = soup.select("div[align=center] a")[:-1]
        for p in pagination:
           result += piratebayScrapper(None, PB_DOMAIN+p["href"])
    return result

def kickassScrapper(query , url= None):
    result = []
    req = None
    if url is None:
        req = Request(KICKASS_SEARCH_URL+"/"+query, headers={'User-Agent': 'Mozilla/5.0'})
        print(req)
    else:
        print(url)
        req = url
    try :
        html = urlopen(req).read()
    except:
        return result
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("table.data tr")[1:] # ignore the first header row
    for row in rows:
        torrent = {}
        newSoup = BeautifulSoup(str(row),"html.parser")
        link = newSoup.select("a.cellMainLink")[0]
        torrent["link"] = KICKASS_DOMAIN+link["href"]
        torrent["title"] = "".join(re.findall(">(.*?)<", str(link)))
        try :
            torrent["numOfComments"] = newSoup.select(".icommentjs > .iconvalue")[0].string
        except:
            torrent["numOfComments"] = "0"
        columns = newSoup.select("td")
        torrent["size"] = columns[1].string
        torrent["uploadTime"] = getUploadTime(columns[3].string)
        torrent["seeds"] = columns[4].string
        torrent["leeches"] = columns[5].string

        result.append(torrent)
    if url == None:
        pagination = soup.select("a[data-page]")
        for p in pagination:
            result += kickassScrapper(None, KICKASS_DOMAIN+p["href"])
    return result

def getUploadTime(time) :
    res = re.match(r"([0-9]{1,2})\s([a-zA-Z]*)",time)
    num = res.group(1)
    month_OR_year = res.group(2)
    today = date.today()
    timeDifference = None
    if month_OR_year.find("month") != -1 :
        # 1 month -> 4weeks
        timeDifference = timedelta(weeks = int(num)*4)
    elif month_OR_year.find("year") !=-1:
        timeDifference = timedelta(days = int(num)*365)
    return (today - timeDifference)

def scrape(query):
    data  = []
  #  data += piratebayScrapper(query)
    data += kickassScrapper(query)
    return data
