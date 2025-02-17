from django.http import HttpResponse
from django.template import loader
from django.db.models.query import QuerySet


from .models import BookRelease, Book


def index(request):
    book_all = Book.objects.all()    
    template = loader.get_template("book.html")    
    context = {
        "books": book_all
    }
    return HttpResponse(template.render(context, request))

