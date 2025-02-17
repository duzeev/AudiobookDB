from django.contrib import admin
from .models import Piople
from .models import Cycle
from .models import Book
from .models import BookRelease

# Register your models here.
admin.site.register(Piople)
admin.site.register(Cycle)
admin.site.register(Book)
admin.site.register(BookRelease)
