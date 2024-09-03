import sys
import os 
import shutil
import zipfile
import time
import datetime


print(sys.argv)

pathFrom = sys.argv[1]
pathZip  = sys.argv[2]
pathPic  = sys.argv[3]

ReWriteAll = False

countAllBooks = 0 
countCurrendBook = 0

def doZip(path, files):
    relative_path_from = os.path.relpath(path, pathFrom)
    path_zip = os.path.join(pathZip, relative_path_from)
    path_zip, file_base_name = os.path.split(path_zip)
    os.makedirs(path_zip, exist_ok=True)
    file_zip = os.path.join(path_zip, file_base_name) + '.zip'
    if ReWriteAll or (not os.path.exists(file_zip)):
        print(file_zip)
        with zipfile.ZipFile(file_zip, mode="w") as archive:
            for f in files:
                filename=os.path.join(path, f)
                archive.write(filename=filename, arcname=f, compresslevel=8)

list_not_pic = ['.mp3', '.txt']

def doPic(path, files):
    relative_path_from = os.path.relpath(path, pathFrom)

    file_pic = ''
    file_pic_ext = ''
    for f in files:
        r, ext = os.path.splitext(os.path.join(path, f))
        if not ( ext.lower() in list_not_pic):
            if len(f) > len(file_pic):
                file_pic = f
                file_pic_ext = ext

    if len(file_pic_ext) > 0:
        file_pic_from = os.path.join(path, file_pic)
        file_pic_to = os.path.join(pathPic, relative_path_from) + file_pic_ext
        if ReWriteAll or (not os.path.exists(file_pic_to)):
            path_pic, fl = os.path.split(file_pic_to)
            os.makedirs(path_pic, exist_ok=True)
            shutil.copy2(file_pic_from,  file_pic_to)
            print(file_pic_to)
    else:
        raise NameError('Not found picture:' + path)

def doText(path):
    relative_path_from = os.path.relpath(path, pathFrom)
    path_txt = os.path.join(pathZip, relative_path_from)
    path_txt, file_base_name = os.path.split(path_txt)
    text_file_name = file_base_name + '.txt'
    file_to = os.path.join(path_txt, text_file_name) 
    file_from = os.path.join(path, text_file_name) 
    if os.path.exists(file_from) and (ReWriteAll or (not os.path.exists(file_to))) :
        shutil.copy2(file_from,  file_to)
        print(file_to)

def is_begin_minus(path) -> bool:
    
    path_next = path
    while(True):
        folder_path, folder_name = os.path.split(path_next)
        path_next = folder_path
        if len(folder_name) == 0:
            break

        if(folder_name[0] == '-'):
            return True
            
    return False

for currentpath, folders, files in os.walk(pathFrom):
    if(len(folders) == 0) and (len(files) != 0) and (files[0] != '-') and not is_begin_minus(currentpath):
        countAllBooks += 1    

time1 = datetime.datetime.fromtimestamp(time.mktime(time.gmtime()))
for currentpath, folders, files in os.walk(pathFrom):
    if(len(folders) == 0) and (len(files) != 0) and (files[0] != '-') and not is_begin_minus(currentpath):
        doZip(currentpath, files)
        doPic(currentpath, files)
        doText(currentpath)
        countCurrendBook += 1
        per = (countCurrendBook/countAllBooks)*100
        time2 = datetime.datetime.fromtimestamp(time.mktime(time.gmtime()))
        diff = time2 - time1
        print("{:.2f}% {}/{} {} {}".format(per, countCurrendBook, countAllBooks, diff, diff.total_seconds()))
