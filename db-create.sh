#/bin/bash
sudo -u postgres psql -a -f ./sql/create_db.sql
sudo -u postgres psql -d daudiobookdb -a -f ./sql/create_tables.sql
sudo -u postgres psql -d daudiobookdb -a -f ./sql/insert_piople.sql
python3 create_db.py /media/duzeev/Archive/AudioBook/ /media/duzeev/Archive/AudioBook/
