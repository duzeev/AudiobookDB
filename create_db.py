from itertools import cycle
import psycopg2
import sys
import os
import copy

conn = None

DATABASE = 'daudiobookdb'
USER     = 'daudiobookuser'
PASSWORD = '1234'
HOST     = 'localhost'

pathZip = '/media/duzeev/Archive/AudioBook/'
pathPic = '/media/duzeev/Archive/AudioBook/'

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


def GetCycleId(title):
   cdb = conn.cursor()
   sql = 'SELECT id, year, title FROM cycle WHERE title = \'' + title + '\';'
   cdb.execute(sql)
   res = cdb.fetchone()
   if(res != None):
      return res[0]
   return None


def addCycleDB(id_parent, num, year, title) -> int:
   cdb = conn.cursor()
   
   id = GetCycleId(title)

   sql_f = 'title'
   sql_v = '\'' + title + '\''

   if(num != None):
      sql_f += ', num'
      sql_v += ', \'' + str(num) + '\''

   if(year != None):
      sql_f += ', year'
      sql_v += ', \'' + str(year) + '\''

   if(id_parent != None):
      sql_f += ', parent_id'
      sql_v += ', \'' + str(id_parent) + '\''

   if id == None:
      sql = 'INSERT INTO cycle(' +  sql_f + ') VALUES(' +  sql_v + ')'
      cdb.execute(sql)
      id = GetCycleId(title)
   else:
      sql_f = 'id, ' + sql_f
      sql_v = '\'' + str(id) + '\', '+ sql_v
      sql = 'UPDATE cycle SET(' +  sql_f + ') = (' +  sql_v + ')' + ' WHERE id = '+ str(id) +';'
      cdb.execute(sql)

   return id

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

   id = addCycleDB(booki[infoParentCycleDB], num, year, str_othe)
   booki[infoParentCycle] = str_othe
   booki[infoParentCycleDB] = id

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


def GetPiopleId(name_in_list):
   cdb = conn.cursor()
   sql = 'SELECT * FROM piople WHERE name_in_list = \'{}\';'.format(name_in_list)
   cdb.execute(sql)
   res = cdb.fetchone()
   if(res == None):
      return None      
   return res[0]

def AddPiople(id, name_in_list): 
   
   fio = name_in_list.split()

   count = 0

   sql_f = 'name_in_list'
   sql_v = '\'' + name_in_list + '\''
   if len(fio) > 0:
      sql_f += ', first_name'
      sql_v += ', \'' + fio[0] + '\''     
      count += 1
   if len(fio) > 1:
      sql_f += ', last_name'
      sql_v += ', \'' + fio[1] + '\''
      count += 1
   if len(fio) > 2:
      sql_f += ', middle_name'
      sql_v += ', \'' + fio[2] + '\''
      count += 1
   if len(fio) > 3:
      sql_f += ', nick_name'
      sql_v += ', \'' + fio[3] + '\''
      count += 1


   if count == 1:
      if id == None:
         sql = 'INSERT INTO piople(name_in_list, nick_name) VALUES(\'{0}\', \'{1}\')'.format(name_in_list, fio[0])
      else:
         sql = 'UPDATE piople SET(name_in_list, nick_name) = (\'{0}\', \'{1}\')' + ' WHERE id = {2};'.format(name_in_list, fio[0], str(id))
   else:
      if id == None:
         sql = 'INSERT INTO piople({0}) VALUES({1})'.format(sql_f, sql_v)
      else:
         sql_f = 'id, ' + sql_f
         sql_v = '\'' + str(id) + '\', ' + sql_v
         sql = 'UPDATE piople SET({0}) = ({1})' + ' WHERE id = {2};'.format(sql_f, sql_v, str(id))
      
   cdb = conn.cursor()
   cdb.execute(sql)
   return GetPiopleId(name_in_list)

def AddGetPiopleDB(lst):
   ret = []

   for w in lst:
      id = GetPiopleId(w)
      if id == None:
         id = AddPiople(id, w)
      ret.append(str(id))

   return ret

def FindBookId(title):
   sql = 'SELECT * FROM book WHERE title = \'' + title + '\';' 
   cdb = conn.cursor()
   cdb.execute(sql)
   res = cdb.fetchone()
   if res == None:
      return None      
   return res[0]

def AddBookDB(id, title, cycle, year, num, writersDB):
   sql_f = 'title, year, num'
   sql_v = '\'' + title + '\' ,\'' + str(year) + '\' ,\'' + str(num) + '\''

   if cycle != None:
      sql_f += ', cycle_id'
      sql_v +=  ', \'' + str(cycle) + '\''

   if id == None:
      sql = 'INSERT INTO book(' +  sql_f + ') VALUES(' +  sql_v + ')'
      # print('INSERT book ' + str(num) + ' ' + str(year) + ' ' + title)
   else:
      sql_f = 'id, ' + sql_f
      sql_v = '\'' + str(id) + '\', ' + sql_v
      sql = 'UPDATE book SET(' +  sql_f + ') = (' +  sql_v + ')' + ' WHERE id = '+ str(id) + ';'
      # print('UPDATE book ' + str(num) + ' ' + str(year) + ' ' + title)
            
   cdb = conn.cursor()
   cdb.execute(sql)

   id = FindBookId(title)

   for w in writersDB:
      sql = 'SELECT * FROM book_writer WHERE book_id = \'' + str(id) + '\' AND writer_id = ' + str(w) +  ';' 
      cdb.execute(sql)
      res = cdb.fetchone()
      if res == None:
         sql = 'INSERT INTO book_writer(book_id, writer_id) VALUES(\'' + str(id) + '\', \'' + str(w) +'\')'
         cdb.execute(sql)
       
   return id

def FindRelease(book_id, zip):
   sql = 'SELECT * FROM book_release WHERE book_id = \'' + str(book_id) + '\' AND zip = \'' +  zip + '\';'
   cdb = conn.cursor()
   cdb.execute(sql)
   res = cdb.fetchone()
   if res == None:
      return None      
   return res[0]


def AddUpdateRelease(book_id, zip, pic, readersDB):
   cdb = conn.cursor()

   release_id = FindRelease(book_id, zip)
   if release_id == None:
      sql = 'INSERT INTO book_release(book_id, zip, pic) VALUES(\'' + str(book_id) + '\', \'' + zip + '\', \'' + pic +'\');'
      cdb.execute(sql)
      release_id = FindRelease(book_id, zip)


   for reader_id in readersDB:
      sql = 'SELECT * FROM release_reader WHERE release_id = \'' + str(release_id) + '\' AND reader_id = ' + str(reader_id) +  ';' 
      cdb.execute(sql)
      res = cdb.fetchone()
      if res == None:
         sql = 'INSERT INTO release_reader(release_id, reader_id) VALUES(\'' + str(release_id) + '\', \'' + str(reader_id) +'\')'
         cdb.execute(sql)

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
      with open(txt, 'r') as file:
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
      print('!!!!!!!!! year < num : ' + full_path)
      num, year = year, num

   id = FindBookId(title)
   id = AddBookDB(id, title, booki[infoParentCycleDB], year, num, writersBD)

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

   AddUpdateRelease(id, relative_path_zip, relative_path_pic, readersBD)

   print('*', end='', flush = True)

   bookCount += 1

   return True

def scanRoot(path):

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
      conn.commit()
      print(' '+str(bookCount))

def main() -> int:
   #establishing the connection
   global conn

   conn = psycopg2.connect(
      database = DATABASE, user = USER, password = PASSWORD, host = HOST
   )
   conn.autocommit = True
   scanRoot(pathZip)

   #Closing the connection
   conn.close()
   print('ALL DONE ... ')
   return 0

if __name__ == '__main__':
   sys.exit(main())
