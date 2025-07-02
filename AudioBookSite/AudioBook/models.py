from django.db import models

class Piople(models.Model):
    name_in_list = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    nick_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return make_full_name(self)

def make_full_name(piople : Piople) -> str:
    ret = ''
    if piople.first_name != None:
        ret += piople.first_name
    if piople.middle_name != None:
        if len(ret) > 0: ret += ' '
        ret += piople.middle_name
    if piople.last_name != None:
        if len(ret) > 0: ret += ' '
        ret += piople.last_name
    if piople.nick_name != None:
        if len(ret) > 0: ret += ' '
        ret += f"({piople.nick_name})"    
    return ret

class Cycle(models.Model):
    title = models.CharField(max_length=255)
    year = models.IntegerField(blank=True, null=True)
    num = models.IntegerField(blank=True, null=True)
    parent = models.ForeignKey("self", on_delete = models.CASCADE, blank=True, null=True)
    def __str__(self):
        return self.title

class BookRelease(models.Model):
    readers = models.ManyToManyField(Piople, blank=True)
    zip = models.CharField(max_length=512)
    pic = models.CharField(max_length=512)
    new = models.BooleanField(default=True)
    to_delete = models.BooleanField(default=False)    
    
    def __str__(self):
        ret = ''
        book = Book.objects.filter(releases__in=BookRelease.objects.filter(id=self.id))       
        for b in book:
            if len(ret) != 0:
                ret += ", "    
            ret += b.title
        book_release = BookRelease.objects.get(id=self.id)
        for reader in book_release.readers.all():
            ret +=  ", " + make_full_name(reader)
            
        return ret
    

class Book(models.Model):
    title = models.CharField(max_length=255)
    cycle = models.ForeignKey(Cycle, on_delete = models.CASCADE, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    num = models.IntegerField(blank=True, null=True)
    writers = models.ManyToManyField(Piople)
    releases = models.ManyToManyField(BookRelease)
    def __str__(self):
        return self.title

