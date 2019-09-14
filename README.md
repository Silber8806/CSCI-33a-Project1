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

## Some Notes:

#### CSS and JavaScript Notes
There are a few things I amended at the ending.  I ran everything through a formatter: python, css and html, 
re-positioned the JavaScripts from near the end of the \<body> to within the  \<head> tag and decided to
keep the CSS file instead of run it through SCSS, because the file length is small at the moment.  I think in the 
future I would refactor CSS to SCSS once the rules become more cumbersome. 

#### Use of Bash
I decided to quickly write up a quick procedure to source variables with bash.  Afterwards, I realized that might
have been a bit zealous and I could have probably just kept a single config file and sourced it.  I kept the 
file, because it is useful in this setting.  I think Python uses a .env file for the same purposes, but would 
have to research what best practices would be here. I decided to use that 
 file as a start to an automation directory where I could put infrastructure related code.

#### Postgres exist clause use
For database logic, I frequently use the postgres exists clause.  Exists works similar to a join, but doesn't produce
duplicate keys.  Instead it acts more like a filter.  I use this in production environments for ETL processes and 
it's very handy for this type of operation.  I think this is ok to use here and just interjecting some of my
experience from working with postgres for the last 4 years.

#### Design choice for import.py

For the import.py script, I followed ETL process called: Truncate and 
reload followed by a merge.  It might look a bit weird, but all it does is prevent duplicate loads from having any 
effect or partial loads.  This is a common pattern for small ETL jobs.  The design was based on my experience as 
a Data Warehouse Developer at Forrester Research.

#### Use of insert and lack of with in import.py

I based the insert statement on the class example, printed out rows and didn't use the with clause when opening a file.
I did this,because the class example used insert, printed rows and didn't have a with clause when opening files.
Typically, if I was going to write this at work, I'd add a with statement and I'd use the COPY Command, bulk loader or
 native driver to upload the data, because it's a bit faster.  I decided against the later due to the code being 
 structured that way in the lecture. It's also possible that my knowledge is outdated here. 

## sources
1. Placeholder Image: 
https://pkf-francisclarkcareers.co.uk/wp-content/uploads/2017/10/placeholder.png
2. Navbar: Boostrap main website
3. Login/registration forms: modified code on website similar to this: https://bootsnipp.com/snippets/GX4aP
