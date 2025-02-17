from flask import Flask
from flask import render_template

import sys
import psycopg2


port  = 80
      
if(len(sys.argv) > 1):
    port  = sys.argv[1]

conn = None

DATABASE    = 'daudiobookdb'
DB_USER     = 'daudiobookuser'
DB_PASSWORD = '1234'
DB_HOST     = 'localhost'

app = Flask(__name__)
# app.debug = True

alphabet_count = []

def make_alphabet_counts():
    alphabet = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЭЮЯ ABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789'
    al = {}
    for a in alphabet:
        al[a] = 0

    cdb = conn.cursor()
    sql = 'SELECT first_name, last_name, nick_name FROM piople;'
    cdb.execute(sql)
    res = cdb.fetchall()
    for r in res:
        if r[0] != None: al[r[0].upper()[0]] += 1
        if r[1] != None: al[r[1].upper()[0]] += 1
        if r[2] != None: al[r[2].upper()[0]] += 1
    
    for k, v in zip(al.keys(), al.values()):
        alphabet_count.append([k, v])

def get_name(id_name_list):
    rstr = ''
    if id_name_list[1] != None: rstr += id_name_list[1] + ' '
    if id_name_list[2] != None: rstr += id_name_list[2] + ' '
    if id_name_list[3] != None: rstr += id_name_list[3] + ' '
    if id_name_list[4] != None: rstr += '"{}"'.format(id_name_list[4])
    return rstr.strip()


def str_append_list_join(s, n):
    l1 = []
    i = 0
    while i < n:
        l1.append(s)
        i += 1
    return ''.join(l1)


def make_list_from_title(title:str):
    ret = title.split('=')
    ret = [s.strip() for s in ret]
    return ret


def make_cycle_list_small(cycle_id):
    if cycle_id == None:
        return None

    cdb = conn.cursor()
    cline = []
    ccycle  = cycle_id
    while(ccycle != None):
        sql  = 'SELECT id, title, parent_id FROM cycle WHERE id = \'' + str(ccycle) + '\' ;'
        cdb.execute(sql)
        res = cdb.fetchone()
        if res == None:
            break
        cline.insert(0, [res[0], res[1], ''])
        ccycle = res[2]

    i = 0
    for c in cline:
        c[2] = str_append_list_join('--', i+1) + ' '
        i += 1

    return cline


const_str_cycle_first = '|----'
const_str_cycle_midle = '----'

def make_cycle_list_root(root_cycle_id, books):
    cdb = conn.cursor()
    clist = []
    sql  = 'SELECT id, title, parent_id FROM cycle WHERE id = \'{}\';'.format(str(root_cycle_id))
    cdb.execute(sql)
    res = cdb.fetchone()

    if res == None:
        return None

    clist.append([False, 0, res[0], res[1], const_str_cycle_first])

    was = True
    while(was):
        was = False

        for i in range(len(clist)):
            cur = clist[i]
            if (cur[0] == False):
                cur[0] = True
                sql  = 'SELECT id, title, parent_id FROM cycle WHERE parent_id = \'{}\';'.format(str(cur[2]))
                cdb.execute(sql)
                res = cdb.fetchall()
                for r in res:
                    s = '|' + str_append_list_join(const_str_cycle_midle, cur[1]+1) + const_str_cycle_midle
                    clist.insert(i+1, [False, cur[1]+1, r[0], r[1], s])
                was = True

                sql = 'SELECT id, title, year, cycle_id, num FROM book WHERE cycle_id = \'' + str(cur[2]) + '\' ORDER BY num;'
                cdb.execute(sql)
                res_books = cdb.fetchall()
                if len(res_books) > 0:
                    for b in res_books:
                        books.append(make_book(b[0], b[1], b[2], b[3]))

                break

    return clist

            
def make_full_cycle_list(cycle_id):
    if cycle_id == None:
        return None

    cdb = conn.cursor()

    root_cycle_id = cycle_id
    cur_cycle_id = cycle_id
    while(cur_cycle_id != None):
        sql  = 'SELECT id, title, parent_id FROM cycle WHERE id = \'{}\';'.format(str(cur_cycle_id))
        cdb.execute(sql)
        res = cdb.fetchone()
        if res == None:
            break
        root_cycle_id = cur_cycle_id
        cur_cycle_id = res[2]

    books = []
    return make_cycle_list_root(root_cycle_id, books)


def make_release_reader(id):
    cdb = conn.cursor()

    sql  = 'SELECT piople.id, piople.first_name, piople.last_name, piople.middle_name, piople.nick_name '
    sql += 'FROM release_reader, piople '
    sql += 'WHERE release_reader.reader_id = piople.id AND release_reader.release_id = \'' + str(id) + '\';'
    cdb.execute(sql)
    res = cdb.fetchall()

    readers = []
    for r in res:
        readers.append([r[0], get_name(r)])

    return readers

def make_book(id, title, year, cycle_id):
    cdb = conn.cursor()

    book = {}
    book['id'] = id
    book['title'] = make_list_from_title(title)
    book['year'] = year
    book['cycles'] = make_cycle_list_small(cycle_id)

    writers = []
    sql  =  '''SELECT piople.id, piople.first_name, piople.middle_name, piople.last_name, piople.nick_name
            FROM book_writer, piople 
            WHERE book_writer.writer_id = piople.id AND book_writer.book_id = '{}';'''.format(str(id))
    cdb.execute(sql)
    res_book_writers = cdb.fetchall()
    for w in res_book_writers:
        writers.append([w[0], get_name(w)])
    
    book['writers'] = writers

    realiases = []
    sql  = 'SELECT id, book_id, zip, pic, new FROM book_release WHERE book_id = \'{}\';'.format(str(id))
    cdb.execute(sql)
    for rel in cdb.fetchall():
        realiases.append( [rel[0], make_release_reader(rel[0]), rel[2], rel[3], rel[4]])
    book['realiases'] = realiases

    return book




@app.route('/cycle/<id>/')
def cycle(id):

    id = int(id)

    cycle_list = make_full_cycle_list(id)
    for c in cycle_list:
        if c[2] == id:
            c[4] += '>'
        else:
            c[4] += ' '

    books = []
    books.clear()
    make_cycle_list_root(id, books)

    st = ' \
        <ul class="tree"> \
            <li> \
                <details open> \
                    <summary>Планеты гиганты</summary> \
                    <ul> \
                        <li> \
                            <details open> \
                                <summary>Газовые</summary> \
                                <ul> \
                                    <li>Юпитер</li> \
                                    <li>Сатурн</li> \
                                </ul> \
                            </details> \
                        </li> \
                        <li> \
                            <details open> \
                                <summary>Ледяные</summary> \
                                <ul> \
                                    <li>Уран</li> \
                                    <li>Нептун</li> \
                                </ul> \
                            </details> \
                        </li> \
                    </ul> \
                </details> \
            </li> \
        </ul> \
    '


    return render_template("cycles.html", st=st, cycle_list=cycle_list, books=books, alphabet_count=alphabet_count)

@app.route('/author/<id>/')
def author(id):
    cdb = conn.cursor()

    sql = 'SELECT id, first_name, last_name, middle_name, nick_name FROM piople WHERE id = \'{}\';'.format(str(id))
    cdb.execute(sql)
    res = cdb.fetchone()
    if(res == None):
        return ''

    author_name = [res[0], get_name(res)]

    books_writer = []
    sql = '''
        SELECT b.id, b.title, b.year, b.cycle_id 
        FROM book_writer bw, book b 
        WHERE bw.book_id = b.id AND bw.writer_id = '{}'
        ORDER BY b.year; 
        '''.format(str(id))
    cdb.execute(sql)
    res_books = cdb.fetchall()
    if len(res_books) > 0:
        for b in res_books:
            books_writer.append(make_book(b[0], b[1], b[2], b[3]))

    books_voice = []
    sql =  '''  
        SELECT b.id, b.title, b.year, b.cycle_id
        FROM release_reader rr, book_release br, book b 
        WHERE rr.release_id = br.id AND br.book_id = b.id AND rr.reader_id = '{}'
        ORDER BY b.year; 
        '''.format(str(id))
    cdb.execute(sql)
    res_voice = cdb.fetchall()
    if len(res_voice) > 0:
        for b in res_voice:
            books_voice.append(make_book(b[0], b[1], b[2], b[3]))

    return render_template("author.html", author_name=author_name, books=[books_writer, books_voice], alphabet_count=alphabet_count)

@app.route('/news/')
def news():

    sql = 'SELECT  book_id FROM book_release WHERE new = \'TRUE\' GROUP BY book_id;'
    cdb = conn.cursor()
    cdb.execute(sql)
    res = cdb.fetchall()

    books = []
    if(res != None):
        for book in res:
            print(book[0])

            sql = 'SELECT id, title, year, num FROM book WHERE id = \'' + str(book[0]) + '\' ORDER BY num;'
            cdb = conn.cursor()
            cdb.execute(sql)
            res_books = cdb.fetchall()
            if len(res_books) > 0:
                for b in res_books:
                    books.append(make_book(b[0], b[1], b[2], b[3]))

    return render_template("news.html", books=books, alphabet_count=alphabet_count)


def get_count_for_piople(id):
    cdb = conn.cursor()
    author_count = 0
    sql = 'SELECT COUNT(*) FROM book_writer WHERE writer_id=\'{}\';'.format(str(id))
    cdb.execute(sql)
    res = cdb.fetchone()
    if res != None:
        author_count = res[0]

    voice_count = 0
    sql = 'SELECT COUNT(*) FROM release_reader WHERE reader_id=\'{}\';'.format(str(id))
    cdb.execute(sql)
    res = cdb.fetchone()
    if res != None:
        voice_count = res[0]

    return [author_count, voice_count]
    
@app.route('/alphabet/<c>/')
def alphabet(c):

    cdb = conn.cursor()

    first_name  = [] 
    last_name   = [] 
    middle_name = [] 
    nick_name   = [] 

    sql = 'SELECT id, first_name, middle_name, last_name, nick_name FROM piople'
    cdb.execute(sql)
    for w in cdb.fetchall():
        wstr = get_name(w)

        if (w[1] != None) and  (w[1][0].upper() == c):
            author_count, voice_count =  get_count_for_piople(w[0])
            first_name.append([w[0], wstr, author_count, voice_count])

        if (w[3] != None) and (w[3][0].upper() == c):
            author_count, voice_count =  get_count_for_piople(w[0])
            last_name.append([w[0], wstr, author_count, voice_count])

        if (w[4] != None) and (w[4][0].upper() == c):
            author_count, voice_count =  get_count_for_piople(w[0])
            nick_name.append([w[0], wstr, author_count, voice_count])


    first_name  = sorted( first_name,   key = lambda x: ( x[2] + x[3] ), reverse=True )
    last_name   = sorted( last_name,    key = lambda x: ( x[2] + x[3] ), reverse=True )
    nick_name   = sorted( nick_name,    key = lambda x: ( x[2] + x[3] ), reverse=True )


    return render_template("alphabet.html", alphabet_count=alphabet_count, 
                        first_name=first_name, last_name=last_name, nick_name=nick_name)



def tree_find(e, t):
    if e in t:
        return t
    for v in t.values():
        r = tree_find(e, v)
        if r:
            return r
    return None

def i():
    dict_ = {'A':['B', 'C'], 'B':['D','E'], 'C':['F', 'G', 'H'], 'E':['I', 'J']}
    tree = {}
    for k,v in dict_.items():
        n = tree_find(k, tree)
        (tree if not n else n)[k] = {e:{} for e in v}
    return render_template('index.html', **locals())

@app.route('/')
def index():

    i()

    pioples = []

    cdb = conn.cursor()
    sql = 'SELECT id, first_name, last_name, middle_name, nick_name FROM piople;'
    cdb.execute(sql)
    for w in cdb.fetchall():
        wstr = get_name(w)
        author_count, voice_count =  get_count_for_piople(w[0])
        pioples.append([w[0], wstr, author_count, voice_count])
    
    pioples = sorted( pioples, key = lambda x: ( x[2] + x[3] ), reverse=True )

    return render_template("index.html", pioples=pioples, alphabet_count=alphabet_count)

if __name__ == "__main__":
    conn = psycopg2.connect(database=DATABASE, user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
    make_alphabet_counts()
    app.run(port=port)
