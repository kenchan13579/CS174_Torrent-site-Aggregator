from django.http import HttpResponse
from django.template import loader, RequestContext
from django.shortcuts import render
from . import scrapper
# Create your views here.
def index ( req ):
  return render(req,"index.html")

def search(req):
    parameter = {}
    if len(req.GET["query"]) <= 2:
        parameter["error"] = "Query too short"
    else :
        filters = {}
        data = []
        if "quality" in req.GET and len(req.GET["quality"])>0:
          filters["quality"] = req.GET["quality"]

        if len(filters)==0 :
          data = scrapper.scrape(req.GET["query"])
        else :
          data = scrapper.scrape(req.GET["query"] , filters)

        if len(data) >= 0 :
            print("Number of Result {}".format(len(data))  )
            parameter["data"] = data
            parameter["dataLength"] = len(data)
        else:
            parameter["error"] = "No result found"
    return render(req,"result.html",parameter,
        content_type="text/html")
