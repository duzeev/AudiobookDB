from django.db import models

class Piople(models.Model):
    name_in_list = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    nick_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        ret = str(self.id) + ':'
        if self.first_name != None:
            ret = self.first_name
            
        if self.middle_name != None:
            if len(ret) > 0: ret += ' '
            ret += self.middle_name

        if self.last_name != None:
            if len(ret) > 0: ret += ' '
            ret += self.last_name
            
        if self.nick_name != None:
            if len(ret) > 0: ret += ' '
            ret += f"({self.nick_name})"
            
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
    

class Book(models.Model):
    title = models.CharField(max_length=255)
    cycle = models.ForeignKey(Cycle, on_delete = models.CASCADE, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    num = models.IntegerField(blank=True, null=True)
    writers = models.ManyToManyField(Piople)
    releases = models.ManyToManyField(BookRelease)
    def __str__(self):
        return self.title



    
