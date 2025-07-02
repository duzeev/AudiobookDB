from django.http import HttpResponse
from django.template import loader
from django.db.models.query import QuerySet


from .models import BookRelease, Book, Piople


def index(request):
    book_all = Book.objects.all()    
    template = loader.get_template("books_list.html")
    context = {
        "books": book_all
    }
    return HttpResponse(template.render(context, request))

def news(request):
    book_all = Book.objects.filter(releases__in=BookRelease.objects.filter(new=True))
    template = loader.get_template("books_list.html")
    context = {
        "books": book_all
    }
    return HttpResponse(template.render(context, request))


def author(request, id):
    p = Piople.objects.get(id=id)
    author = Book.objects.filter(writers__id=id)
    reader = Book.objects.filter(releases__in=BookRelease.objects.filter(readers__id=id))
    template = loader.get_template("author.html")    
    context = {
        "title": p,
        "author": author,
        "reader": reader
    }
    return HttpResponse(template.render(context, request))

def cycle(request, id):
    cycle = Book.objects.filter(releases__in=BookRelease.objects.filter(readers__id=id))
    template = loader.get_template("cycle.html")    
    context = {
        "title": p,
        "author": author,
        "reader": reader
    }
    return HttpResponse(template.render(context, request))
