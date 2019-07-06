CREATE TABLE ACCOUNTS
(
    acct_id serial PRIMARY KEY,
    acct_name VARCHAR not null,
    acct_email VARCHAR Unique not null,
    acct_password VARCHAR not null
);