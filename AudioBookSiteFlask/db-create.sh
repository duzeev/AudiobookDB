#/bin/bash

source ../conf-linux.sh

source ../AudioBookSiteDjango/.venv/bin/activate

sudo -u postgres psql -a -f ./sql/create_db.sql
sudo -u postgres psql -d daudiobookdb -a -f ./sql/create_tables.sql
sudo -u postgres psql -d daudiobookdb -a -f ./sql/insert_piople.sql
python3 db-update.py $DIR_ZIP $DIR_PIC

