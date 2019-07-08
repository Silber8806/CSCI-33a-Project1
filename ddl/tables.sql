CREATE TABLE ACCOUNTS
(
    acct_id serial PRIMARY KEY,
    acct_name VARCHAR not null,
    acct_email VARCHAR Unique not null,
    acct_password VARCHAR not null
);

CREATE TABLE BOOKS
(
    book_id serial PRIMARY KEY,
    book_isbn VARCHAR not null,
    book_name VARCHAR not null,
    book_author VARCHAR not null,
    book_year VARCHAR not null
);

CREATE TABLE BOOKS_STG
(
    book_isbn VARCHAR not null,
    book_name VARCHAR not null,
    book_author VARCHAR not null,
    book_year VARCHAR not null
);

CREATE TABLE REVIEWS
(
    review_id serial PRIMARY KEY,
    book_id_fk INTEGER not null references BOOKS(book_id),
    acct_id_fk INTEGER not null references ACCOUNTS(acct_id),
    review_name VARCHAR not null,
    review_text TEXT not null,
    unique (book_id_fk, acct_id_fk)
);



