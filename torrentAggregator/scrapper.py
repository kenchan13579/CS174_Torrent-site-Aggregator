import re
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
PB_DOMAIN = "http://thepiratebay.la"
piratebayURL = "http://thepiratebay.la/search/"
kickassURL = "http://kickasstorrents.video/usearch"
def piratebayScrapper(query  , url=None):
    result = []
    searchURL = ""
    if url is None:
        res = re.match( r'\W*([a-zA-Z0-9\s]*)\W*' , query)
        if res.group(1) == "" : # if no pattern is matched , exit
            return
        searchURL = piratebayURL + res.group(1).strip() + "/0/99/200"
    else:
        searchURL = url
        print(url)
    req = Request(searchURL, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    soup = BeautifulSoup(webpage, "html.parser")
    rows = soup.select("tr")[1:] # get rid of the header row
    for row in rows:
        torrent = {}
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
        torrent["theSeeds"] = re.findall(">(.*?)<" , str(seedsAndLeech[0]))
        torrent["theLeeches"] = re.findall(">(.*?)<" , str(seedsAndLeech[1]))
        result.append(torrent)
    if url is None:
        pagination = soup.select("div[align=center] a")[:-1]
        for p in pagination:
           result += piratebayScrapper(None, PB_DOMAIN+p["href"])
    return result
print(len(piratebayScrapper("maze runner" )))
