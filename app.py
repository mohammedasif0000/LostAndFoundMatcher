from flask import Flask, render_template, request, session, redirect, url_for, flash
from database.db import add_item, add_user, get_user_by_username, get_user_by_email, update_password, get_db_connection, get_user_by_id, get_items
from werkzeug.security import generate_password_hash
import re
import os
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from difflib import SequenceMatcher
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "lost_and_found_dev_key")
app.config["UPLOAD_FOLDER"] = "static/uploads"

@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/black")
def black_page():
    return render_template("black.html")

@app.route("/home")
def home():
    connection = get_db_connection()

    total_items = connection.execute(
        "SELECT COUNT(*) FROM Items"
    ).fetchone()[0]

    found_items = connection.execute(
        "SELECT COUNT(*) FROM Items WHERE type = 'found'"
    ).fetchone()[0]

    returned_items = connection.execute(
        "SELECT COUNT(*) FROM Items WHERE returned = 1"
    ).fetchone()[0]

    success_rate = (
        round((returned_items / total_items) * 100)
        if total_items > 0
        else 0
    )

    connection.close()

    return render_template(
        "index.html",
        total_items=total_items,
        found_items=found_items,
        returned_items=returned_items,
        success_rate=success_rate
    )

@app.route("/report_lost", methods=["GET", "POST"])
def report_lost():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        item_name = request.form.get("item_name")
        category = request.form.get("category")
        date = request.form.get("date")
        location = request.form.get("location")
        description = request.form.get("description")
        contact = request.form.get("contact")

        identifying_feature = request.form.get(
            "identifying_feature",
            "TEST"
        )

        secret_detail = request.form.get("secret_detail")

        photo = request.files.get("photos")
        image_filename = None

        if photo and photo.filename:

            filename = secure_filename(photo.filename)

            image_filename = filename

            photo.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

        item_id = add_item(
            session["user_id"],
            "lost",
            item_name,
            category,
            description,
            location,
            date,
            image_filename,
            contact,
            identifying_feature,
            secret_detail
        )

        print("New Lost Item ID:", item_id)
        print("LOST ITEM SAVED TO DATABASE")
        flash(
            "Your lost item has been reported successfully!",
            "success"
        )

        # Go to dashboard after successful submission
        return redirect(url_for("dashboard"))

    return render_template("report_lost.html")

@app.route("/report_found", methods=["GET", "POST"])
def report_found():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":

        item_name = request.form.get("item_name")
        category = request.form.get("category")
        date = request.form.get("date")
        location = request.form.get("location")
        description = request.form.get("description")
        contact = request.form.get("contact")

        identifying_feature = request.form.get(
            "identifying_feature"
        )

        secret_detail = request.form.get("secret_detail")

        photo = request.files.get("photos")
        image_filename = None

        if photo and photo.filename:

            filename = secure_filename(photo.filename)

            image_filename = filename

            photo.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    filename
                )
            )

        item_id = add_item(
            session["user_id"],
            "found",
            item_name,
            category,
            description,
            location,
            date,
            image_filename,
            contact,
            identifying_feature,
            secret_detail
        )

        print("New Found Item ID:", item_id)
        print("FOUND ITEM SAVED TO DATABASE")
        flash(
            "Your found item has been reported successfully!",
            "success"
        )

        # Go to dashboard after successful submission
        return redirect(url_for("dashboard"))

    return render_template("report_found.html")

# ============================================================
# MATCHING SYSTEM
# ============================================================

def text_similarity(text1, text2):
    """
    Compare two pieces of text and return a score from 0 to 100.
    """

    text1 = (text1 or "").strip().lower()
    text2 = (text2 or "").strip().lower()

    if not text1 or not text2:
        return 0

    return round(
        SequenceMatcher(None, text1, text2).ratio() * 100
    )

def calculate_match_score(lost_item, found_item):
    """
    Calculate a match score between a lost item and a found item.
    Maximum score = 100.
    """

    # Item name - 35 points
    name_similarity = text_similarity(
        lost_item["item_name"],
        found_item["item_name"]
    )

    name_score = name_similarity * 0.35


    # Description - 25 points
    description_similarity = text_similarity(
        lost_item["description"],
        found_item["description"]
    )

    description_score = description_similarity * 0.25


    # Category - 15 points
    lost_category = (
        lost_item["category"] or ""
    ).strip().lower()

    found_category = (
        found_item["category"] or ""
    ).strip().lower()

    if lost_category and found_category:

        if lost_category == found_category:
            category_score = 15
        else:
            category_score = (
                text_similarity(
                    lost_category,
                    found_category
                ) * 0.15
            )

    else:
        category_score = 0


    # Location - 15 points
    location_similarity = text_similarity(
        lost_item["location"],
        found_item["location"]
    )

    location_score = location_similarity * 0.15


    # Date - 10 points
    date_score = 0

    try:

        lost_date = datetime.strptime(
            lost_item["date"],
            "%Y-%m-%d"
        )

        found_date = datetime.strptime(
            found_item["date"],
            "%Y-%m-%d"
        )

        difference = abs(
            (lost_date - found_date).days
        )

        if difference == 0:
            date_score = 10

        elif difference <= 1:
            date_score = 9

        elif difference <= 3:
            date_score = 7

        elif difference <= 7:
            date_score = 5

        elif difference <= 14:
            date_score = 3

        else:
            date_score = 0

    except (ValueError, TypeError):

        date_score = 0


    # Final score
    total_score = (
        name_score
        + description_score
        + category_score
        + location_score
        + date_score
    )

    return round(min(total_score, 100))

def calculate_match_score(lost_item, found_item):
    """
    Calculate a simple matching score between a lost item
    and a found item.

    Maximum score: 100
    """

    score = 0

    # --------------------------------------------------------
    # CATEGORY MATCH - 30 POINTS
    # --------------------------------------------------------

    if (
        lost_item["category"]
        and found_item["category"]
        and lost_item["category"].strip().lower()
        == found_item["category"].strip().lower()
    ):
        score += 30


    # --------------------------------------------------------
    # ITEM NAME MATCH - 20 POINTS
    # --------------------------------------------------------

    lost_name = (lost_item["item_name"] or "").strip().lower()
    found_name = (found_item["item_name"] or "").strip().lower()

    if lost_name and found_name:

        if lost_name == found_name:
            score += 20

        elif (
            lost_name in found_name
            or found_name in lost_name
        ):
            score += 10


    # --------------------------------------------------------
    # LOCATION MATCH - 20 POINTS
    # --------------------------------------------------------

    lost_location = (lost_item["location"] or "").strip().lower()
    found_location = (found_item["location"] or "").strip().lower()

    if lost_location and found_location:

        if lost_location == found_location:
            score += 20

        elif (
            lost_location in found_location
            or found_location in lost_location
        ):
            score += 10


    # --------------------------------------------------------
    # DESCRIPTION SIMILARITY - 20 POINTS
    # --------------------------------------------------------

    lost_description = (
        lost_item["description"] or ""
    ).strip().lower()

    found_description = (
        found_item["description"] or ""
    ).strip().lower()

    if lost_description and found_description:

        lost_words = set(lost_description.split())
        found_words = set(found_description.split())

        common_words = lost_words.intersection(found_words)

        if common_words:

            similarity = (
                len(common_words)
                / max(len(lost_words), len(found_words))
            )

            if similarity >= 0.5:
                score += 20

            elif similarity >= 0.25:
                score += 10


    # --------------------------------------------------------
    # DATE MATCH - 10 POINTS
    # --------------------------------------------------------

    if (
        lost_item["date"]
        and found_item["date"]
        and lost_item["date"] == found_item["date"]
    ):
        score += 10


    return score

@app.route("/match_result")
def match_result():

    # --------------------------------------------------------
    # LOGIN PROTECTION
    # --------------------------------------------------------

    user_id = session.get("user_id")

    if user_id is None:
        return redirect(url_for("login"))


    # --------------------------------------------------------
    # GET LOST ITEM ID
    # --------------------------------------------------------

    lost_id = request.args.get("lost_id", type=int)

    if lost_id is None:
        return "Lost item ID is required.", 400


    # --------------------------------------------------------
    # GET ITEMS FROM DATABASE
    # --------------------------------------------------------

    connection = get_db_connection()

    lost_item = connection.execute(
        "SELECT * FROM items WHERE id = ? AND type = 'lost'",
        (lost_id,)
    ).fetchone()

    found_items = connection.execute(
        "SELECT * FROM items WHERE type = 'found'"
    ).fetchall()

    connection.close()


    # --------------------------------------------------------
    # LOST ITEM NOT FOUND
    # --------------------------------------------------------

    if lost_item is None:
        return "Lost item not found.", 404


    # --------------------------------------------------------
    # CALCULATE MATCHES
    # --------------------------------------------------------

    matches = []

    for found_item in found_items:

        score = calculate_match_score(
            lost_item,
            found_item
        )

        matches.append({
            "item": found_item,
            "score": score
        })


    # --------------------------------------------------------
    # SORT HIGHEST SCORE FIRST
    # --------------------------------------------------------

    matches.sort(
        key=lambda match: match["score"],
        reverse=True
    )


    # --------------------------------------------------------
    # ONLY SHOW MEANINGFUL MATCHES
    # --------------------------------------------------------

    matches = [
        match
        for match in matches
        if match["score"] >= 30
    ]

    return render_template("match_result.html", lost_item=lost_item, matches=matches)

@app.route("/verification", methods=["GET", "POST"])
def verification():

    # --------------------------------------------------------
    # LOGIN PROTECTION
    # --------------------------------------------------------

    if "user_id" not in session:
        return redirect(url_for("login"))


    # --------------------------------------------------------
    # GET ITEM ID
    # --------------------------------------------------------

    # First try the URL:
    # /verification?item_id=13
    #
    # If this is a POST, also allow the form to provide
    # the item_id.

    item_id = request.args.get("item_id", type=int)

    if item_id is None and request.method == "POST":
        item_id = request.form.get("item_id", type=int)


    # --------------------------------------------------------
    # ITEM ID REQUIRED
    # --------------------------------------------------------

    if item_id is None:
        return "Verification item ID is required.", 400


    # --------------------------------------------------------
    # GET THE SELECTED FOUND ITEM
    # --------------------------------------------------------

    connection = get_db_connection()

    item = connection.execute(
        "SELECT * FROM items WHERE id = ?",
        (item_id,)
    ).fetchone()

    connection.close()


    # --------------------------------------------------------
    # ITEM NOT FOUND
    # --------------------------------------------------------

    if item is None:
        return "Item not found.", 404


    # --------------------------------------------------------
    # GET REQUEST
    # --------------------------------------------------------

    if request.method == "GET":

        return render_template(
            "verification.html",
            item=item
        )


    # --------------------------------------------------------
    # POST REQUEST
    # --------------------------------------------------------

    identifying_feature = request.form.get(
        "identifying_feature",
        ""
    ).strip()

    secret_detail = request.form.get(
        "secret_detail",
        ""
    ).strip()

    location = request.form.get(
        "location",
        ""
    ).strip()

    date = request.form.get(
        "date",
        ""
    ).strip()

    description = request.form.get(
        "description",
        ""
    ).strip()


    # --------------------------------------------------------
    # SCORE SYSTEM
    # --------------------------------------------------------

    score = 0


    if (
        identifying_feature.lower()
        == item["identifying_feature"].lower().strip()
    ):
        score += 30


    if (
        secret_detail.lower()
        == item["secret_detail"].lower().strip()
    ):
        score += 25


    if (
        location.lower()
        == item["location"].lower().strip()
    ):
        score += 20


    if date == item["date"]:
        score += 15


    if (
        description.lower()
        == item["description"].lower().strip()
    ):
        score += 10


    # --------------------------------------------------------
    # VERIFICATION RESULT
    # --------------------------------------------------------

    if score >= 80:

        status = "Verified"

    elif score >= 60:

        status = "Needs review"

    else:

        status = "Failed"


    print("Verification Item ID:", item_id)
    print("Verification Score:", score)
    print("Verification Status:", status)


    # --------------------------------------------------------
    # SAVE VERIFICATION
    # --------------------------------------------------------

    connection = get_db_connection()

    connection.execute(
        """
        INSERT INTO Verification (
            item_id,
            claimant_id,
            identifying_feature,
            secret_detail,
            location,
            date,
            description,
            score,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            item_id,
            session["user_id"],
            identifying_feature,
            secret_detail,
            location,
            date,
            description,
            score,
            status
        )
    )

    connection.commit()
    connection.close()


    # --------------------------------------------------------
    # SHOW RESULT
    # --------------------------------------------------------

    return render_template(
        "verification.html",
        item=item,
        verification_submitted=True,
        score=score,
        status=status
    )

@app.route("/mark_returned/<int:item_id>", methods=["POST"])
def mark_returned(item_id):

    # Login protection
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    # Check that the item exists
    item = connection.execute(
        "SELECT * FROM Items WHERE id = ?",
        (item_id,)
    ).fetchone()

    if item is None:
        connection.close()
        return "Item not found.", 404

    # Mark item as returned
    connection.execute(
        "UPDATE Items SET returned = 1 WHERE id = ?",
        (item_id,)
    )

    connection.commit()
    connection.close()

    # Go back to the item's details page
    return redirect(url_for("item_details", item_id=item_id))

@app.route("/items")
def items():
    user_id = session.get("user_id")

    if user_id is None:
        return redirect(url_for("login"))

    all_items = get_items()

    return render_template(
        "items.html",
        items=all_items
    )

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":

        name = request.form.get("name", "").strip()
        if not name:
            flash("Please enter your full name.", "error")
            return redirect(url_for("signup"))

        username = request.form.get("username", "").strip()
        if not re.fullmatch(r"[A-Za-z0-9_]{3,20}", username):
            flash(
                "Username must be 3–20 characters and contain only letters, numbers, or _.",
                "error"
            )
            return redirect(url_for("signup"))

        email = request.form.get("email", "").strip()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            flash("Please enter a valid email address.", "error")
            return redirect(url_for("signup"))

        password = request.form.get("password", "")

        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "error")
            return redirect(url_for("signup"))

        if not re.search(r"[A-Z]", password):
            flash("Password must contain an uppercase letter.", "error")
            return redirect(url_for("signup"))

        if not re.search(r"[a-z]", password):
            flash("Password must contain a lowercase letter.", "error")
            return redirect(url_for("signup"))

        if not re.search(r"\d", password):
            flash("Password must contain a number.", "error")
            return redirect(url_for("signup"))

        if not re.search(r"[!@#$%^&*]", password):
            flash("Password must contain a special character.", "error")
            return redirect(url_for("signup"))

        confirm_password = request.form.get("confirm_password", "")

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("signup"))

        password_hash = generate_password_hash(password)

        if not add_user(name, username, email, password_hash):
            flash("Username or email already exists.", "error")
            return redirect(url_for("signup"))

        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = get_user_by_username(username)

        if user is None:
            flash("Invalid username or password.", "error")
            return redirect(url_for("login"))

        if not check_password_hash(user["password_hash"], password):
            flash("Invalid username or password.", "error")
            return redirect(url_for("login"))

        session["user_id"] = user["id"]

        flash("Login successful!", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/change_password", methods=["GET", "POST"])
def change_password():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = get_user_by_id(session["user_id"])

    if request.method == "POST":

        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not check_password_hash(
            user["password_hash"],
            current_password
        ):
            flash("Current password is incorrect.", "error")
            return redirect(url_for("change_password"))

        if new_password != confirm_password:
            flash("New passwords do not match.", "error")
            return redirect(url_for("change_password"))

        if len(new_password) < 8:
            flash("Password must be at least 8 characters long.", "error")
            return redirect(url_for("change_password"))

        if not re.search(r"[A-Z]", new_password):
            flash("Password must contain an uppercase letter.", "error")
            return redirect(url_for("change_password"))

        if not re.search(r"[a-z]", new_password):
            flash("Password must contain a lowercase letter.", "error")
            return redirect(url_for("change_password"))

        if not re.search(r"\d", new_password):
            flash("Password must contain a number.", "error")
            return redirect(url_for("change_password"))

        if not re.search(r"[!@#$%^&*]", new_password):
            flash("Password must contain a special character.", "error")
            return redirect(url_for("change_password"))

        new_password_hash = generate_password_hash(new_password)

        connection = get_db_connection()

        connection.execute(
            """
            UPDATE users
            SET password_hash = ?
            WHERE id = ?
            """,
            (new_password_hash, session["user_id"])
        )

        connection.commit()
        connection.close()

        flash("Password changed successfully!", "success")
        return redirect(url_for("dashboard"))

    return render_template(
        "change_password.html",
        user=user
    )

@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        user = get_user_by_email(email)

        if user is None:
            flash("No account found with this email.", "error")
            return redirect(url_for("forgot_password"))

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("forgot_password"))

        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "error")
            return redirect(url_for("forgot_password"))

        if not re.search(r"[A-Z]", password):
            flash("Password must contain an uppercase letter.", "error")
            return redirect(url_for("forgot_password"))

        if not re.search(r"[a-z]", password):
            flash("Password must contain a lowercase letter.", "error")
            return redirect(url_for("forgot_password"))

        if not re.search(r"\d", password):
            flash("Password must contain a number.", "error")
            return redirect(url_for("forgot_password"))

        if not re.search(r"[!@#$%^&*]", password):
            flash("Password must contain a special character.", "error")
            return redirect(url_for("forgot_password"))

        password_hash = generate_password_hash(password)

        update_password(email, password_hash)

        flash("Password reset successfully! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("forgot_password.html")

@app.route("/item/<int:item_id>")
def item_details(item_id):
    user_id = session.get("user_id")

    if user_id is None:
       return redirect(url_for("login"))
    
    connection = get_db_connection()
    item = connection.execute(
        "SELECT * FROM items WHERE id = ?",
        (item_id,)
    ).fetchone()
    connection.close()

    if item is None:
        return "Item not found", 404

    #REMEMBER WHERE THE USER CAME FROM
    source = request.args.get("from", "dashboard")
    if source not in ["dashboard", "items"]:
        source = "dashboard"

    return render_template("item_details.html", item=item, source=source)

@app.route("/dashboard")
def dashboard():

    user_id = session.get("user_id")
    print("DASHBOARD USER ID:", user_id)

    if user_id is None:
        return redirect(url_for("login"))

    user = get_user_by_id(user_id)

    connection = get_db_connection()

    # =========================================================
    # COMMUNITY / GLOBAL STATISTICS
    # =========================================================

    total_items = connection.execute(
        "SELECT COUNT(*) FROM items"
    ).fetchone()[0]

    lost_items = connection.execute(
        "SELECT COUNT(*) FROM items WHERE type = 'lost'"
    ).fetchone()[0]

    found_items = connection.execute(
        "SELECT COUNT(*) FROM items WHERE type = 'found'"
    ).fetchone()[0]

    returned_items = connection.execute(
        "SELECT COUNT(*) FROM items WHERE returned = 1"
    ).fetchone()[0]


    # =========================================================
    # MY REPORTS
    # Only reports belonging to the logged-in user
    # =========================================================

    my_items = connection.execute(
        """
        SELECT *
        FROM items
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,)
    ).fetchall()


    # =========================================================
    # MY STATISTICS
    # =========================================================

    my_total_items = len(my_items)

    my_lost_items = sum(
        1 for item in my_items
        if item["type"] == "lost"
    )

    my_found_items = sum(
        1 for item in my_items
        if item["type"] == "found"
    )

    my_returned_items = sum(
        1 for item in my_items
        if item["returned"] == 1
    )


    connection.close()


    return render_template(
        "dashboard.html",

        user=user,

        # Community statistics
        total_items=total_items,
        lost_items=lost_items,
        found_items=found_items,
        returned_items=returned_items,

        # User-specific data
        my_items=my_items,
        my_total_items=my_total_items,
        my_lost_items=my_lost_items,
        my_found_items=my_found_items,
        my_returned_items=my_returned_items
    )

if __name__ == "__main__":
    app.run(debug=True)