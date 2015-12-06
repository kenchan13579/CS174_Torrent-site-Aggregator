import re
import time
from datetime import date
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from datetime import date, timedelta
import threading
## Global var
PB_DOMAIN = "http://thepiratebay.la"
PB_SEARCH_URL = PB_DOMAIN + "/search/"
KICKASS_DOMAIN = "http://kickasstorrents.video"
KICKASS_SEARCH_URL = KICKASS_DOMAIN + "/usearch/"

'''
scrape data from piratebay
'''
def piratebayScrapper(query , result , url=None):
    searchURL = ""
    if url is None:
        res = re.match( r'\W*([a-zA-Z0-9\s]*)\W*' , query)
         # check query is valid if no pattern is matched , exit
        if res.group(1) == "" :
            return
        searchURL = PB_SEARCH_URL + res.group(1).strip() + "/0/99/200"
        print(searchURL)
    else:
        #will scrape pagination links
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
        torrent["quality"] = getQuality(torrent['title'])
        torrent["link"] = PB_DOMAIN + link["href"]
        sizeInfo = newSoup.select("font.detDesc")[0].contents
        if len(sizeInfo) == 4:
        #hard code for case when there is new video which will display as XX min ago
        # with <b> tag
            #formatter formats the data to make uniform.
            #Here it adjusts to Kickasstorrents time and size formats
            timeFormatter = newSoup.select("font.detDesc b")[0].string
            timeFormatter = parseDate(timeFormatter)
            torrent["uploadTime"] = timeFormatter
            res = re.match(r".*Size\s*(.*?),",sizeInfo[2])
            formatter = res.group(1).strip()
            formatter = formatter.replace("i", "")
            torrent["size"] = formatter
        else:
            sizeInfo = sizeInfo[0]
            res = re.match(r"Uploaded\s*(.*?),\s*Size(.*?),",sizeInfo);
            formatter = res.group(2).strip()
            formatter = formatter.replace("i","")
            torrent["size"] = formatter
            formatter = res.group(1).strip()
            formatter = formatter.split("\\xa0")
            formatter = formatter[0]
            formatter = parseDate(formatter)
            torrent["uploadTime"] = formatter
        seedsAndLeech = newSoup.find_all('td',attrs={'align':'right'})
        seeds = re.findall(">(.*?)<" , str(seedsAndLeech[0]))
        leeches = re.findall(">(.*?)<" , str(seedsAndLeech[1]))
        torrent["seeds"] = "".join(seeds)
        torrent["leeches"] = "".join(leeches)

        theComment = newSoup.find('img', src="//thepiratebay.la/static/img/icon_comment.gif")
        commentPattern = "title=\"This torrent has (.*?) comments.\""
        theComment = re.findall(commentPattern, str(theComment))
        torrent["numOfComments"] = "".join(theComment)
        torrent["from"] = "Pirate Bay"
        if not theComment:
            torrent["numOfComments"] = "0"
        result.append(torrent) # add to the result
    if url is None:
        pagination = soup.select("div[align=center] a")[:-1]
        thread_list = [] # list to store threads
        for p in pagination:
            ## create threads and put them into the list first
            thread_list.append(threading.Thread(target=piratebayScrapper , args=(None,result, PB_DOMAIN+p["href"])))
        # run the threads !
        for t in thread_list:
            t.start()
        # wait for them to finish
        for t in thread_list:
            t.join()

'''
scrapper for kickass torrent
'''
def kickassScrapper(query ,result, url= None):
    req = None
    if url is None:
        req = Request(KICKASS_SEARCH_URL+"/"+query, headers={'User-Agent': 'Mozilla/5.0'})
    else:
        # pagination links
        req = url
    try :
        # the pagination links seem to prohibit scraper
        print(req)
        html = urlopen(req).read()
    except Exception as e:
        print(e)
        return
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("table.data tr")[1:] # ignore the first header row
    for row in rows:
        torrent = {}
        newSoup = BeautifulSoup(str(row),"html.parser")
        link = newSoup.select("a.cellMainLink")[0]
        torrent["link"] = KICKASS_DOMAIN+link["href"]
        torrent["title"] = "".join(re.findall(">(.*?)<", str(link)))
        torrent["quality"] = getQuality(torrent['title'])
        try :
            torrent["numOfComments"] = newSoup.select(".icommentjs > .iconvalue")[0].string
        except:
            torrent["numOfComments"] = "0"
        columns = newSoup.select("td")
        torrent["size"] = parseSize(columns[1].contents)
        print(torrent["size"])
        torrent["uploadTime"] = getUploadTime(columns[3].string)
        torrent["seeds"] = columns[4].string
        torrent["leeches"] = columns[5].string
        torrent["from"] = "Kickass Torrents"
        result.append(torrent)
    if url == None:
        pagination = soup.select("a[data-page]")
        for p in pagination:
            print(KICKASS_DOMAIN+p["href"])
            kickassScrapper(None, result,KICKASS_DOMAIN+p["href"])

'''
parse kickass's date format to mmm-dd-yyyy
'''
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
    elif month_OR_year.find("day") != -1:
        timeDifference = timedelta(days = int(num))
    else:
        timeDifference = timedelta(days=0)
    return (today - timeDifference)

'''
    start scraping and return an array of filtered torrent obj sorted by # of seeds
'''
def scrape(query ,filters=None):
    result = []
    piratebayScrapper(query,result)
    kickassScrapper(query,result)
    if filters is not None:
        for key,val in filters.items():
            result = list(filter(lambda torrent: torrent[str(key)] == val ,result))
    result = sorted(result, key = lambda torrent : int(torrent["seeds"]) , reverse = True)
    return result

#input can be mm-dd hh:MM or mm-dd yyyy
def parseDate(dateString):
    result = ""
    theString = dateString.split("-")
    second = theString[1]
    if  second[5] != ":":
        theMonth = int(theString[0])
        theYear = second[3:7]
        theDay = second[0:2]
        result = convertDate(int(theMonth), int(theDay), int(theYear))
    else:
        theMonth = int(theString[0])
        theYear = 2015
        theDay = second[0:2]
        result = convertDate(int(theMonth), int(theDay), theYear)
    return result

def convertDate(m, d, y):
    if y == 0:
        tdate = date(year=2015,month=m,day=d)
    else:
        tdate = date(month=m,day=d, year =y)
    return tdate
    #return str(tdate.strftime("%b %m, %Y"))

'''
    Get quality of the torrent video based on keyword in the title
    720,1080,or none
'''
def getQuality(title):
    if title.find("720") != -1 :
        return "720p"
    elif title.find("1080") != -1:
        return "1080p"
    else:
        return "Unknown"

'''
    Get size from kickass parse e.g. -> 15 <span>GB</span>
'''
def parseSize(contents):
    if len(contents) == 1 :
        return contents[0].string
    elif len(contents) == 0 :
        return None
    else:
        return contents[0].string + contents[1].string
test = []
kickassScrapper("avenger" , test )
print(len(test))
