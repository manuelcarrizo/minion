from django.http import HttpResponse


# Create your views here.
def index(request):
    index_data = open("src/web/templates/index.html", "r").read()
    return HttpResponse(index_data, content_type="text/html")
