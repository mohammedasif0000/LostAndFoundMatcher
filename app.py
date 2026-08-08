from flask import Flask,render_template,request

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
        print("ITEM:",item_name)
        print("CATEGORY:",category)
        print("DATE:",date)
        print("LOCATION:",location)
        print("DESCRIPTION:",description)
        print("CONTACT:",contact)
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
            print("ITEM:",item_name)
            print("CATEGORY:",category)
            print("DATE:",date)
            print("LOCATION:",location)
            print("DESCRIPTION:",description)
            print("CONTACT:",contact)
    return render_template("report_found.html")

if __name__ == "__main__":
    app.run(debug=True)