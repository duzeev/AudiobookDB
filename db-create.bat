"c:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -a -f ./sql/create_db.sql
"c:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -d daudiobookdb -a -f ./sql/create_tables.sql
"c:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -d daudiobookdb -a -f ./sql/insert_piople.sql
python3 create_db.py D:\AudioBook D:\AudioBook

