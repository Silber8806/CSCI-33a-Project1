CREATE TABLE ACCOUNTS
(
    user_id serial PRIMARY KEY,
    user_name VARCHAR Unique not null,
    password VARCHAR not null,
    created_on TIMESTAMP not null,
    last_login TIMESTAMP
);

