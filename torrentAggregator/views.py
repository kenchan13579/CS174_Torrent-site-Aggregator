from django.http import HttpResponse
from django.template import loader, RequestContext
from django.shortcuts import render
from . import scrapper
# Create your views here.
def index ( req ):
  template = loader.get_template("index.html")
  context = RequestContext(req , {
    "from" : "Ken"
  })
  return HttpResponse(template.render(context))

def search(req):
    parameter = {}
    if len(req.GET["query"]) <= 3:
        parameter["error"] = "Query too short"
    else :
        data = scrapper.scrape(req.GET["query"])
        if len(data) >= 0 :
            print(len(data))
            parameter["data"] = data
            parameter["dataLength"] = len(data)
        else:

            parameter["error"] = "No result found"
    return render(req,"result.html",parameter,
        content_type="text/html")
