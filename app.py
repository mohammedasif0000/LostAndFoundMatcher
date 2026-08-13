from flask import Flask, render_template, request, session, redirect, url_for
from database.db import add_item, add_user, get_user_by_username, get_user_by_email, update_password
from werkzeug.security import generate_password_hash
import re
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = "lost_and_found_dev_key"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/report_lost", methods=["GET", "POST"])
def report_lost():
    if request.method == "POST":
        item_name = request.form.get("item_name")
        category = request.form.get("category")
        date = request.form.get("date")
        location = request.form.get("location")
        description = request.form.get("description")
        contact = request.form.get("contact")

        add_item(
            "lost",
            item_name,
            category,
            description,
            location,
            date,
            None,
            contact
        )
        print("LOST ITEM SAVED TO DATABASE")
    return render_template("report_lost.html")

@app.route("/report_found", methods=["GET", "POST"])
def report_found():
    if request.method == "POST":
        item_name = request.form.get("item_name")
        category = request.form.get("category")
        date = request.form.get("date")
        location = request.form.get("location")
        description = request.form.get("description")
        contact = request.form.get("contact")

        add_item(
            "found",
            item_name,
            category,
            description,
            location,
            date,
            None,
            contact
        )
        print("FOUND ITEM SAVED TO DATABASE")
    return render_template("report_found.html")
            
@app.route("/match_result")
def match_result():
     match_score = 92
     lost_item = "Black Wallet"
     found_item = "Black Wallet"
     lost_category = "Electronics"
     found_category = "Electronics"
     lost_location = "College Campus"
     found_location = "College Campus"
     lost_date = "08 August 2026"
     found_date = "07 August 2026"
     lost_image = "images/test-lost.jpg"
     found_image = "images/test-found.jpg"
     return render_template("match_result.html",match_score=match_score,lost_item=lost_item,found_item=found_item,lost_category=lost_category,found_category=found_category,lost_location=lost_location,found_location=found_location,lost_date=lost_date,found_date=found_date,lost_image=lost_image,found_image=found_image)

@app.route("/verification")
def verification():
     return render_template("verification.html")

@app.route("/search")
def search():
     return render_template("search.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        if not re.fullmatch(r"[A-Za-z0-9_]{3,20}", username):
            return "Username must be 3-20 characters and contain only letters, numbers, or _"
        
        email = request.form.get("email", "").strip()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            return "Please enter a valid email address"

        password = request.form.get("password")
        if len(password) < 8:
            return "Password must be at least 8 characters long"

        if not re.search(r"[A-Z]", password):
            return "Password must contain an uppercase letter"

        if not re.search(r"[a-z]", password):
            return "Password must contain a lowercase letter"

        if not re.search(r"\d", password):
            return "Password must contain a number"

        if not re.search(r"[!@#$%^&*]", password):
            return "Password must contain a special character"
        
        confirm_password = request.form.get("confirm_password")
        if password != confirm_password:
            return "Passwords do not match"
        
        password_hash = generate_password_hash(password)

        if not add_user(username, email, password_hash):
            return "Username or email already exists"

        return "Account created successfully"
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password")
        user = get_user_by_username(username)

        if user in None:
            return "Invalid username or password"
        
        if not check_password_hash(user["password_hash"], password):
            return "Invalid username or password"
        session["user_id"] = user["id"]
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        user = get_user_by_email(email)
        if user is None:
            return "No account found with this email"
        if password != confirm_password:
            return "Passwords do not match"
        if len(password) < 8:
            return "Password must be at least 8 characters long"
        if not re.search(r"[A-Z]", password):
            return "Password must contain an uppercase letter"
        if not re.search(r"[a-z]", password):
            return "Password must contain a lowercase letter"
        if not re.search(r"\d", password):
            return "Password must contain a number"
        if not re.search(r"[!@#$%^&*]", password):
            return "Password must contain a special character"
        password_hash = generate_password_hash(password)
        update_password(email, password_hash)
        return redirect(url_for("login"))
    return render_template("forgot_password.html")

if __name__ == "__main__":
    app.run(debug=True)