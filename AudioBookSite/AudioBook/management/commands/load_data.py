from django.core.management.base import BaseCommand
from AudioBook.models import *

import sys
import json
import os
import copy



DIR_BOOK_MAIN = '/mnt/Archive/AudioBook/'
DIR_BOOK_FROM = '/mnt/Archive/AudioBookRaw/'

pathZip = '/mnt/Archive/AudioBook/'
pathPic = '/mnt/Archive/AudioBook/'

infoFullPath = 'full path'
infoParentCycleDB = 'parent cycle db'
infoParentCycle = 'parent cycle'
infoWriters = 'writers'
infoReaders = 'readers'

bookCount = 0

def IsCycle(name) -> bool:
   if name[len(name) - 1] == '+':
      return True
   return False  

def CutNumYearTitle(str):
   num = None
   year = None
   all = str

   end_year = str.find(" ")
   str_num_year = str[:end_year]
   s = str_num_year.split('-')
   if len(s) == 1:
      if s[0].isdigit():
         year = int(s[0])
         all = str[end_year+1:].strip()

   if len(s) == 2:
      if s[0].isdigit():
         num = int(s[0])
      if s[1].isdigit():
         year = int(s[1])
      all = str[end_year+1:].strip()

   return num, year, all

def CutBetween(str, bc, ec):
   res = []
   other = str

   if ( bc in str ) and ( ec in str ):
      s = str.find(bc)
      e = str.find(ec)

      other = str[:s]+str[e+1:]
      all = str[s+1:e]
      
      res = all.split(',')
      res = [s.strip() for s in res]
      
   return res, other


def addCycleDB(parent, num, year, title):
    c = Cycle.objects.all().filter(title=title)    
    if(len(c) == 0):
        cycle = Cycle(title=title)
        if parent != None:
            cycle.parent = parent
        if num != None:
            cycle.num = num
        if year != None:
            cycle.year = year
        cycle.save()
        return cycle
    return c[0]

def addCycleDir(bookinfo, curr_cycle_all):
  
   # print('add cycle ' + curr_cycle_all + ' ')
   # if bookinfo[infoParentCycle] != None:
   #    print(infoParentCycle + ' ' + bookinfo[infoParentCycle])

   booki = copy.deepcopy(bookinfo)

   num, year, str_othe = CutNumYearTitle(curr_cycle_all)
   
   writers, str_othe = CutBetween(str_othe, '(', ')')
   booki[infoWriters].extend(writers)
   readers, str_othe = CutBetween(str_othe, '[', ']')
   booki[infoReaders].extend(readers)

   str_othe = str_othe.strip()

   cycle = addCycleDB(booki[infoParentCycleDB], num, year, str_othe)
   booki[infoParentCycle] = str_othe
   booki[infoParentCycleDB] = cycle

   num = 1
   path = booki[infoFullPath]
   dirs = os.listdir(path)
   dirs.sort()
   for f in dirs:
      full_path = os.path.join(path, f)
      booki[infoFullPath] = full_path
      if os.path.isdir(full_path):
         if IsCycle(f):
            cycle = f[:-1]
            addCycleDir(booki, cycle)
         else:
            raise NameError('find directory not cycle:'+full_path) 
         
      if os.path.isfile(full_path):
         if addBook(booki, f, num):
            num += 1

def addWriterDir(bookinfo, writer):
   # print('add writer ' + writer)

   bookinfo[infoWriters].append(writer)

   path = bookinfo[infoFullPath]
   dirs = os.listdir(path)
   dirs.sort()

   num = 1
   for f in dirs:
      full_path = os.path.join(path, f)
      bookinfo[infoFullPath] = full_path
      if os.path.isdir(full_path):
         if IsCycle(f):
            cycle = f[:-1]
            addCycleDir(bookinfo, cycle)
      if os.path.isfile(full_path):
         if addBook(bookinfo, f, num):
            num += 1


def GetPiople(name_in_list):
    p = Piople.objects.all().filter(name_in_list=name_in_list)
    if(len(p) == 0):
        return None      
    return p[0]

def AddPiople(name_in_list): 
   
    fio = name_in_list.split()    
    p = Piople(name_in_list=name_in_list)
   
    if len(fio) == 1:
        p.nick_name = fio[0]
    elif len(fio) == 2:
        p.first_name = fio[0]
        p.last_name = fio[1]
    elif len(fio) == 3:
        p.first_name = fio[0]
        p.middle_name = fio[1]
        p.last_name = fio[2]
    else:
        print("long FIO !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        
    p.save()
    return p


def AddGetPiopleDB(lst):
   ret = []

   for w in lst:
      id = GetPiople(w)
      if id == None:
         id = AddPiople(w)
      ret.append(id)
      
   return ret


def AddUpdateBookDB(title, cycle, year, num, writersDB):
    book = None
    
    b = Book.objects.all().filter(title=title)
    if(len(b) == 0): 
        book = Book(title=title, cycle=cycle, year=year, num=num)
    else:
        book = b[0]
    
    book.save()
    book.writers.set(writersDB)
    book.save()
    return book


def AddUpdateRelease(book_id, zip, pic, readersDB):
    book_release = None
    r = BookRelease.objects.all().filter(pic=pic, zip=zip)
    if(len(r) == 0):
        book_release = BookRelease(zip=zip, pic=pic)
        book_release.save()        
    else:
        book_release = r[0]
        
    release_in_book = book_id.releases.all()
    if r not in release_in_book:
        book_id.releases.add(book_release)
    
    book_release.to_delete = False
    book_release.readers.set(readersDB)
    book_release.save()

def addBook(bookinfo, book, counter):

    global  bookCount

    booki = copy.deepcopy(bookinfo)

    full_path = booki[infoFullPath]
    full_name, ext = os.path.splitext(full_path)
    if ext != '.zip':
        return False
    full_dir, name_ext = os.path.split(full_path)
    txt = full_name+'.txt'
    if os.path.exists(txt):
        with open(txt, mode="r", encoding="utf-8") as file:
            book = file.read().rstrip()

    book_name, ext = os.path.splitext(book)

    num, year, str_othe = CutNumYearTitle(book_name)
    if num == None:
        num = counter

    writers, str_othe = CutBetween(str_othe, '(', ')')
    booki[infoWriters].extend(writers)
    readers, str_othe = CutBetween(str_othe, '[', ']')
    booki[infoReaders].extend(readers)
    title = str_othe.strip()

    writersBD = AddGetPiopleDB(booki[infoWriters])
    readersBD = AddGetPiopleDB(booki[infoReaders])

    # print(' writers ' + writersBD + ' readers ' + readersBD)

    if year == None:
        raise NameError('Can\'t set book year:' + full_path)

    if year < num:
        # print('!!!!!!!!! year < num : ' + full_path)
        num, year = year, num

    id = AddUpdateBookDB(title, booki[infoParentCycleDB], year, num, writersBD)
    relative_path_zip = os.path.relpath(full_path, pathZip)

    picFile = None
    relative_path_dir_pic = os.path.split(relative_path_zip)[0]
    full_dir_pic = os.path.join(pathPic, relative_path_dir_pic)
    dirs = os.listdir(full_dir_pic)

    zipFileBase, zipFileExt = os.path.splitext(name_ext)

    for f in dirs:
        ffull = os.path.join(full_dir_pic, f)
        fname, fext = os.path.splitext(f)

        if (fname == zipFileBase) and ((fext != zipFileExt)):
            picFile = ffull
            break


    if picFile == None:
        raise NameError('Can\'t find picture file for:'+full_path)

    relative_path_pic = os.path.relpath(picFile, pathPic)

    relative_path_zip = relative_path_zip.replace("\\", "/")
    relative_path_pic = relative_path_pic.replace("\\", "/")

    AddUpdateRelease(id, relative_path_zip, relative_path_pic, readersBD)

    print('*', end='', flush = True)

    bookCount += 1

    return True

def scanRootDir(path):
   global bookCount

   dirs = os.listdir(path)
   dirs.sort()

   num = 1
   for f in dirs:
      print('{:<40}'.format(f), end='', flush = True)
      bookCount  = 0
      full_path = os.path.join(path, f)
      if os.path.isdir(full_path):
         bookinfo = {}
         bookinfo[infoFullPath] = full_path
         bookinfo[infoParentCycle] = None
         bookinfo[infoParentCycleDB] = None
         bookinfo[infoWriters] = []
         bookinfo[infoReaders] = []
         if IsCycle(f):
            cycle = f[:-1]
            addCycleDir(bookinfo, cycle)
         else:
            addWriterDir(bookinfo, f)
      if os.path.isfile(full_path):
         if addBook(bookinfo, f, num):
            num += 1
      print(' '+str(bookCount))

def beforeUpdate():
    all_bookrelease = BookRelease.objects.all()
    print('beforeUpdate: NOW:' + str(len(all_bookrelease)))
    
    all_bookrelease.update(new=False)
    all_bookrelease.update(to_delete=True)

def afterUpdate():    
    delete_bookrelease = BookRelease.objects.filter(to_delete=True)
    to_delete = len(delete_bookrelease)
    for r in delete_bookrelease:
        r.delete()
        
    new_bookrelease = BookRelease.objects.filter(new=True)        
    all_bookrelease = BookRelease.objects.all()
    print('afterUpdate: NOW:' + str(len(all_bookrelease)))
    print('afterUpdate: DELETED:' + str(to_delete))
    print('afterUpdate: NEW:' + str(len(new_bookrelease)))
    
    
        
class Command(BaseCommand):    
    def handle(self, *args, **options):
        beforeUpdate()
        scanRootDir(pathZip)
        afterUpdate()
        print('finished')