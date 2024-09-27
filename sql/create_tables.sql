BEGIN;

CREATE TABLE cycle (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    year INT,
    num INT,
    parent_id INTEGER REFERENCES cycle(id)
);
GRANT ALL PRIVILEGES ON TABLE cycle TO daudiobookuser;
GRANT ALL PRIVILEGES ON SEQUENCE cycle_id_seq TO daudiobookuser;

CREATE TABLE piople (
    id SERIAL PRIMARY KEY,
    name_in_list VARCHAR NOT NULL,
    first_name VARCHAR,
    last_name VARCHAR,
    middle_name VARCHAR,
    nick_name VARCHAR
);
GRANT ALL PRIVILEGES ON TABLE piople TO daudiobookuser;
GRANT ALL PRIVILEGES ON SEQUENCE piople_id_seq TO daudiobookuser;

CREATE TABLE book (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    cycle_id INTEGER REFERENCES cycle(id),
    year INT not null,
    num INT not null
);
GRANT ALL PRIVILEGES ON TABLE book TO daudiobookuser;
GRANT ALL PRIVILEGES ON SEQUENCE book_id_seq TO daudiobookuser;

CREATE TABLE book_writer (
    book_id INTEGER NOT NULL REFERENCES book(id),
    writer_id INTEGER NOT NULL REFERENCES piople(id),
    PRIMARY KEY(book_id, writer_id)
);
GRANT ALL PRIVILEGES ON TABLE book_writer TO daudiobookuser;

CREATE TABLE book_release (
    id SERIAL PRIMARY KEY,
    book_id INTEGER NOT NULL REFERENCES book(id),
    zip VARCHAR,
    pic VARCHAR,
    new BOOLEAN not null,
    del BOOLEAN not null
);
ALTER TABLE book_release ALTER COLUMN new SET DEFAULT FALSE;
ALTER TABLE book_release ALTER COLUMN del SET DEFAULT TRUE;
GRANT ALL PRIVILEGES ON TABLE book_release TO daudiobookuser;
GRANT ALL PRIVILEGES ON SEQUENCE book_release_id_seq TO daudiobookuser;


CREATE TABLE release_reader (
    release_id INTEGER NOT NULL REFERENCES book_release(id),
    reader_id INTEGER NOT NULL REFERENCES piople(id)
);
GRANT ALL PRIVILEGES ON TABLE release_reader TO daudiobookuser;

COMMIT;