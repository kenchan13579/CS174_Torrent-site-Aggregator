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
    data = scrapper.scrape(req.GET["query"])
    print(len(data))
    return render(req,"result.html",{"test" : data},
        content_type="text/html")
