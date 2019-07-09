# Project 1

Web Programming with Python and JavaScript

## Set-up

1. Create a heroku postgres database and goodreads services
2. go to the secrets directory and fill out the below params:

    ```
    FLASK_APP="application.py"
    FLASK_DEBUG=1
    DATABASE_URL=""
    DATABASE_HOST=""
    DATABASE=""
    DATABASE_USER=""
    DATABASE_PASSWORD=""
    GOODREAD_API_KEY=""
    ```

    Blank fields should be set with corresponding values.

3. Go to ddl table and grab the tables.sql.  Create those tables in a database.
4. Run: ``` source ./automation/env.sh [environment]``` where environment is the basename without extension of the config file.
5. Go to the data directory and run: ```python import.py```  wait a while for the data to upload.
6. Run: ```flask run``` and the web server should begin.

I covered all the requirements and focused on trying to iron out the smaller edge cases.

## Website Layout

The index of the website has: login and register.  Register first and it will bring you to a search page.
Notice that the navbar menus change from register/login to search/about.  The main book keeper button brings 
you back to the login/register page.  On the search page, you can search for books and it should give you a
listing.  Pressing on the book title or more info button gets you to the books page.  You can go to the bottom
and write a review.  Once a review is written, you can no longer write a review for that specific book.  Other
books are however open for reviews.  /api/[isbn] route provides JSON data as specified.  Feel free to create
a few accounts and try it out.

## Tables

```sql
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
```
I use a common ETL pattern: truncate-reload-merge and that's where the BOOKS_STG comes from (STG -> stage).

## Files
The below will show you the output of the directory as a tree structure.  I've added comments about files below:

Command:

```$ cmd //c tree //```

Output:
```
C:.
▒   application.py # application with all routes etc...
▒   README.md # this file that you are reading.
▒   requirements.txt # requirements file
▒
▒▒▒▒automation # folder for automation
▒       env.sh # bash to set up the environment
▒
▒▒▒▒data # data directory
▒       books.csv # Data as CSV file
▒       import.py # python import.py in this folder to load data.
▒
▒▒▒▒ddl # folder for ddl -> data definition language
▒       tables.sql # actual DDL file.
▒
▒▒▒▒flask_session # directory with sessions
▒
▒▒▒▒secrets # secrets directory...should make this hidden... (to do)
▒       dev.config # not present in repo, this is the config I used.
▒       example.config # example config file...
▒       secrets.md # just a file saying this dir is for secrets.
▒
▒▒▒▒static # static content
▒   ▒▒▒▒css # css static content
▒   ▒       styles.css # actual CSS used in project (didn't use SCSS sorry)
▒   ▒
▒   ▒▒▒▒images # images for project
▒   ▒       placeholder.jpg # placeholder image
▒   ▒
▒   ▒▒▒▒js # where JS files should have gone.
▒▒▒▒templates # A TON of templates!  TON!
▒       404.html # 404 page
▒       account.html # this is not implemented yet
▒       book.html # book page
▒       error.html # generic error page
▒       index.html # main page
▒       layout.html # generic layout, should be in it's own dir (to do list)
▒       login.html # login page
▒       register.html # register page
▒       search.html # search page
▒
```

Note I trimmed the output of the command to not include temporary files.

## Summary

Honestly think there is a lot of room for improvement.  This is more of a quick prototype.

## sources
1. Placeholder Image: 
https://pkf-francisclarkcareers.co.uk/wp-content/uploads/2017/10/placeholder.png
2. Navbar: Boostrap main website
3. Login/registration forms: modified code on website similar to this: https://bootsnipp.com/snippets/GX4aP
