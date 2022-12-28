#/bin/bash
sudo -u postgres psql -a -f create_db.sql
sudo -u postgres psql -d daudiobookdb -a -f create_tables.sql
sudo -u postgres psql -d daudiobookdb -a -f insert_piople.sql
