import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from turtle import onclick, onscreenclick
# Python's built-in module for encoding and decoding JSON data
import json
# Python's built-in module for opening and reading URLs
import urllib.request
import textwrap

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    if session["user_id"] is None:
        return render_template("index.html")
    else: return render_template("dashboard.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("must provide password")

        # Confirmation missing or not matching password
        if not request.form.get("confirmation"):
            return apology("must provide password confirmation")

        # Confirmation and password don't match
        if not request.form.get("confirmation") == request.form.get("password"):
            return apology("Both passwords don't match")

        # Username already taken
        if db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username")):
            return apology("Sorry this username is already taken")

        # Add the user to the users table
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get("username"),
                   generate_password_hash(request.form.get("password")))

        # Log in the person
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        session["user_id"] = rows[0]["id"]

        # Redirect users to home page
        return redirect("/")

    else:
        return render_template("register.html")

@app.route("/mybooks", methods=["GET", "POST"])
@login_required
def addbook():
    if request.method == "POST":
        # Ensure book title was submitted
        if not request.form.get("book"):
            return apology("must provide book title")
        # Ensure book author was submitted
        if not request.form.get("author"):
            return apology("must provide book author")

        if request.form.get("author") and request.form.get("book"):
            # create getting started variables
            title = request.form.get("book").strip().replace(' ','+')
            author = request.form.get("author").strip().replace(' ','+')
            api = ("https://www.googleapis.com/books/v1/volumes?q={0}+inauthor:{1}".format(title, author))

            # send a request and get a JSON response
            response = urllib.request.urlopen(api)
            text = response.read()

            # parse JSON into Python as a dictionary
            book_data = json.loads(text)

            # if the book is not in the list
            if book_data["totalItems"] == 0:
                return apology("Sorry the book you are looking for is not in our database, please check spelling and try again")

            if len(book_data["items"]) == 1:
                # create additional variables for easy querying
                volume_info = book_data["items"][0]
                author = book_data["items"][0]["volumeInfo"]["authors"][0]
                isbn10 = volume_info["volumeInfo"]["industryIdentifiers"][0]["identifier"]
                # practice with conditional expressions!
                prettify_author = author if len(author) > 1 else author[0]

                # add the book to the table
                db.execute("INSERT INTO book (title, author, ISBN, pages, reader_id) VALUES (?, ?, ?, ?, ?)", volume_info["volumeInfo"]["title"],author, isbn10, volume_info["volumeInfo"]["pageCount"], session["user_id"])

                # add title, author, page count, publication date to website table
                newbook = db.execute("SELECT * FROM book WHERE reader_id = ?", session["user_id"])

                return render_template("mybooks.html", stocks=newbook)

            if len(book_data["items"]) > 1:
                db.execute("DELETE FROM listbook")
                for i in range(len(book_data["items"])):
                    volume_info = book_data["items"][i]
                    author = book_data["items"][i]["volumeInfo"]["authors"][0]
                    isbn10 = volume_info["volumeInfo"]["industryIdentifiers"][0]["identifier"]
                    date = volume_info["volumeInfo"]["publishedDate"]
                    if "subtitle" in volume_info["volumeInfo"]:
                        subtitle = volume_info["volumeInfo"]["subtitle"]
                    else: subtitle = " "
                    db.execute("INSERT INTO listbook (title, author, ISBN, pages, date, subtitle) VALUES (?, ?, ?, ?, ?, ?)", volume_info["volumeInfo"]["title"],author, isbn10, volume_info["volumeInfo"]["pageCount"], date, subtitle)
                newbook = db.execute("SELECT * FROM listbook")
                return render_template("listofbooks.html", stocks=newbook)

    if request.method == "GET":
        newbook = db.execute("SELECT * FROM book WHERE reader_id = ?", session["user_id"])
        return render_template("mybooks.html", stocks=newbook)

@app.route("/listofbooks", methods=["GET", "POST"])
def listofbooks():
    if request.method == "GET":
        newbook = db.execute("SELECT * FROM listbook")
        return render_template("listofbooks.html", stocks=newbook)

    if request.method == "POST":
        book = request.get_json()
        title = book[title]
        author = book[author]
        isbn = book[isbn]
        pages = book[pages]
        db.execute("INSERT INTO book (title, author, ISBN, pages, reader_id) VALUES (?, ?, ?, ?, ?)", title, author, isbn, pages, session["user_id"])
        newbook = db.execute("SELECT * FROM book WHERE reader_id = ?", session["user_id"])
        return render_template("mybooks.html", stocks=newbook)


@app.route("/myfavorites")
@login_required
def myfavorites():

    return render_template("myfavorites.html")

@app.route("/mystatistics")
@login_required
def mystatistics():
    return render_template("mystatistics.html")

