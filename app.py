from flask import Flask,render_template,request
from database.db import add_item

app = Flask(__name__)

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
if __name__ == "__main__":
    app.run(debug=True)