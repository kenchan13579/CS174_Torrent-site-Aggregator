from django.http import HttpResponse
from django.template import loader, RequestContext
# Create your views here.
def index ( req ):
  template = loader.get_template("index.html")
  context = RequestContext(req , {
    "from" : "Ken" 
  })
  return HttpResponse(template.render(context))