DROP DATABASE IF EXISTS daudiobookdb;
DROP USER IF EXISTS daudiobookuser;

CREATE DATABASE daudiobookdb;

CREATE USER daudiobookuser WITH ENCRYPTED PASSWORD '1234';
GRANT ALL PRIVILEGES ON DATABASE daudiobookdb TO daudiobookuser;

