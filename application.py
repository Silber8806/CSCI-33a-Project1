import os
import json
import requests

from flask import Flask, session, render_template, request, flash, redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import exc

app = Flask(__name__, static_url_path='/static')

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

goodreads_api_key = os.getenv("GOODREADS_API_KEY")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def standardize_email(email):
    return str(email).strip().lower()


def standardize_form_input(text_value):
    return str(text_value).strip()


def update_credentials(acct_email, acct_id=None, acct_name=None):
    """ updates the credentials."""

    if (acct_id is None or acct_name is None):
        acct_sql = """
                SELECT 
                    acct_id, 
                    acct_name,
                    acct_email
                from ACCOUNTS 
                where acct_email = :acct_email 
                """
        try:
            account = db.execute(acct_sql, {"acct_email": str(acct_email)})

            if (account.rowcount == 1):
                credential_account = account.fetchone()
                acct_id = credential_account["acct_id"]
                acct_name = credential_account["acct_name"]

        except Exception as e:
            flash(e)
            return 1

    session['id'] = acct_id
    session['name'] = acct_name
    session['email'] = acct_email

    return 0


def flash_err(message):
    flash(message, 'danger')
    return 0


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


@app.route("/")
def index():
    """ main page of website """
    return render_template('index.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    """ Login page.."""
    if request.method == 'POST':
        email_address = standardize_email(request.form['email'])
        email_password = standardize_form_input(request.form['password'])
        acct_sql = """
                SELECT 
                    acct_id, 
                    acct_name,
                    acct_email,
                    acct_password
                from ACCOUNTS 
                where acct_email = :email_address 
                """
        account = db.execute(acct_sql, {"email_address": str(email_address)})
        if (account.rowcount == 1):
            active_account = account.fetchone()
            if (email_password == active_account["acct_password"]):
                session_info = [ \
                    active_account["acct_email"], \
                    active_account["acct_id"], \
                    active_account['acct_name'], \
                    ]
                update_credentials(*session_info)
                return render_template('search.html')
            else:
                error_message = "bad password!"
                flash_err(error_message)
        elif (account.rowcount == 0):
            error_message = "Can't find account!"
            flash_err(error_message)
        else:
            flash_err(error_message)
    return render_template('login.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    """ Register page"""
    if request.method == 'POST':
        if (request.form['password'] == request.form['repeat-password']):
            acct_name, acct_email, acct_password = standardize_form_input(request.form['name']), \
                                                   standardize_email(request.form['email']), \
                                                   standardize_form_input(request.form['password'])
            new_acct_sql = """
                INSERT into ACCOUNTS(acct_name,acct_email,acct_password) values 
                (:acct_name , :acct_email, :acct_password)
            """

            new_account_dict = {"acct_name": acct_name, "acct_email": acct_email, "acct_password": acct_password}
            try:
                db.execute(new_acct_sql, new_account_dict)
                flash("account created!")
                db.commit()
                update_credentials(acct_email=acct_email)
                return render_template('search.html')
            except exc.IntegrityError:
                flash_err("Book Keeper Account already exists...")
            except Exception as e:
                flash_err("500 Internal Database Error")
        else:
            flash_err("Passwords don\'t match")
    return render_template('register.html')


@app.route("/search/", methods=['GET', 'POST'])
def search():
    """ search page with results """
    if request.method == 'POST':
        if len(request.form['book_search'].strip()) == 0:
            flash_err("blanks not allowed in search...")
            return render_template('search.html')

        search_term = str('%' + standardize_form_input(request.form['book_search']) + '%')

        search_sql = """
            SELECT 
                book_id,
                book_isbn,
                book_name,
                book_author,
                book_year
            from BOOKS 
            where book_isbn ilike :search_term or
                  book_name ilike :search_term or 
                  book_author ilike :search_term
            order by book_name,
                     book_author,
                     book_isbn
            """
        search_results = db.execute(search_sql, {"search_term": search_term})
        search_term = search_term[1:-1]
        return render_template('search.html', search_term=search_term, search_results=search_results)
    return render_template('search.html')


@app.route("/book/<int:book_id>")
def book(book_id):
    """ Get a specific book..."""

    if session.get('id') is None:
        flash_err("please login before viewing books...")
        return redirect(url_for('login'))

    book_sql = """
        SELECT 
            book_id,
            book_isbn,
            book_name,
            book_author,
            book_year
        from BOOKS 
        where book_id = :book_id
        """
    current_book = db.execute(book_sql, {"book_id": book_id})

    if (current_book.rowcount == 0):
        return render_template('404.html'), 404
    else:
        current_book = current_book.fetchone()

    res = requests.get("https://www.goodreads.com/book/review_counts.json",
                       params={"key": goodreads_api_key, "isbns": current_book.book_isbn})

    goodreads_data = res.json()['books'][0]
    user_id = session['id']

    review_sql = """
        SELECT 
            review_name,
            review_text,
            a.acct_name,
            r.acct_id_fk = :user_id as owner_review
        from REVIEWS r left outer join ACCOUNTS a 
            on (a.acct_id = r.acct_id_fk)
        where book_id_fk = :book_id
        """
    reviews = db.execute(review_sql, {"book_id": book_id, "user_id": user_id}).fetchall()
    write_review_active = len([review for review in reviews if review.owner_review]) == 0

    return render_template('book.html', \
                           book=current_book, \
                           goodreads=goodreads_data, \
                           reviews=reviews, \
                           review_active=write_review_active)


@app.route("/account/")
def account():
    """ account settings page, not implemented... """
    return render_template('account.html')


@app.route("/api/<isbn>")
def api(isbn):
    book_sql = """
        SELECT 
            book_id,
            book_isbn,
            book_name,
            book_author,
            book_year
        from BOOKS 
        where book_isbn = :book_isbn
        """
    current_book = db.execute(book_sql, {"book_isbn": isbn})

    review_cnt_sql = """
            SELECT 
                count(*) as review_count
            from REVIEWS r inner join BOOKS b
                on (r.book_id_fk = b.book_id)
                where b.book_isbn = :book_isbn
        """
    current_review_count_qry = db.execute(review_cnt_sql, {"book_isbn": isbn})

    if (current_book.rowcount == 0):
        send_json = {}
    else:
        current_book = current_book.fetchone()
        current_review_count = current_review_count_qry.fetchone()['review_count']
        send_json = {}
        send_json["title"] = current_book.book_name
        send_json["author"] = current_book.book_author
        send_json["year"] = current_book.book_year
        send_json["isbn"] = current_book.book_isbn
        send_json["review_count"] = current_review_count

    return jsonify(send_json)


@app.route("/post_review/<int:book_id>", methods=["POST"])
def post_review(book_id):
    user_id = session['id']
    review_name = standardize_form_input(request.form['review_title'])
    review_text = standardize_form_input(request.form['review_text'])

    create_review_sql = """
        INSERT into REVIEWS(book_id_fk,acct_id_fk,review_name,review_text) values
        (:book_id,:user_id,:review_name,:review_text)
    """

    new_review_info = {"book_id": book_id, "user_id": user_id, "review_name": review_name, "review_text": review_text}

    try:
        db.execute(create_review_sql, new_review_info)
        flash("book review created!")
        db.commit()
    except exc.IntegrityError:
        flash_err("Book review already exists...")
    except Exception as e:
        flash_err("500 Internal Database Error")

    return redirect(url_for('book', book_id=book_id))


@app.route("/logout")
def logout():
    """ logout route """
    session.clear()
    return render_template('index.html')
