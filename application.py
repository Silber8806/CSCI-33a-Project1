import os

from flask import Flask, session, render_template, request, flash, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import exc



app = Flask(__name__,static_url_path='/static')

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def update_credentials(acct_email, acct_id=None, acct_name=None):
    """ updates the credentials."""

    print("inside function")

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
            account = db.execute(acct_sql,{"acct_email":str(acct_email)})
            print(account)
            if (account.rowcount == 1):
                credential_account = account.fetchone()
                acct_id = credential_account["acct_id"]
                acct_name = credential_account["acct_name"]
                print("set")
            else:
                print("failed")
        except Exception as e:
            flash(e)
            return 1

    print("new session")
    session['id'] = acct_id
    session['name'] = acct_name
    session['email'] = acct_email

    return 0

@app.route("/")
def index():
    """ main page of website """
    return render_template('index.html')

@app.route("/login", methods = ['GET','POST'])
def login():
    """ Login page.."""
    if request.method == 'POST':
        email_address = request.form['email']
        email_password = request.form['password']
        acct_sql = """
                SELECT 
                    acct_id, 
                    acct_name,
                    acct_email,
                    acct_password
                from ACCOUNTS 
                where acct_email = :email_address 
                """
        account = db.execute(acct_sql,{"email_address":str(email_address)})
        if (account.rowcount == 1):
            active_account = account.fetchone()
            if (email_password == active_account["acct_password"]):
                session_info = [ \
                                active_account["acct_email"],\
                                 active_account["acct_id"], \
                                 active_account['acct_name'],\
                                ]
                update_credentials(*session_info)
                return render_template('index.html')
            else:
                error_message="bad password!"
                flash(error_message)
        elif (account.rowcount == 0):
            error_message = "Can't find account!"
            flash(error_message)
        else:
            flash(error_message)
    return render_template('login.html')

@app.route("/register", methods=['GET','POST'])
def register():
    """ Register page"""
    if request.method == 'POST':
        if (request.form['password'] == request.form['repeat-password']):
            acct_name, acct_email, acct_password = request.form['name'],request.form['email'], request.form['password']
            new_acct_sql = """
                INSERT into ACCOUNTS(acct_name,acct_email,acct_password) values 
                (:acct_name , :acct_email, :acct_password)
            """

            new_account_dict={"acct_name":acct_name,"acct_email": acct_email, "acct_password" : acct_password}
            try:
                db.execute(new_acct_sql,new_account_dict)
                flash("account created!")
                db.commit()
                update_credentials(acct_email=acct_email)
                render_template('index.html')
            except exc.IntegrityError:
                flash("Book Keeper Account already exists...")
            except Exception as e:
                flash("500 Internal Database Error")
        else:
            flash("Passwords don\'t match")
    return render_template('register.html')

@app.route("/account/")
def account():
    """ account settings page, not implemented... """
    return render_template('account.html')

@app.route("/logout")
def logout():
    """ logout route """
    session.clear()
    return render_template('index.html')