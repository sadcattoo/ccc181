"""CCC181 Week 2: a "Hello, Flask" starter app.

Run it with:
    flask --app app run --debug
then open http://127.0.0.1:5000
"""
from flask import Flask, abort, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = "dev-only-change-me" 

# Sample data for the demo. A real app would load this from a database later.
TICKETS = [
    {"number": 1001, "service_id": 1, "status": "waiting"},
    {"number": 2001, "service_id": 2, "status": "in service"},
    {"number": 3001, "service_id": 3, "status": "done"},
    {"number": 1001, "service_id": 1, "status": "waiting"},
    {"number": 2001, "service_id": 2, "status": "in service"},
]


SERVICES = [
    {"service_id": 1, "name": "Buy a medicine"},
    {"service_id": 2, "name": "Buy with a prescription"},
    {"service_id": 3, "name": "Priority service"}
]



@app.route("/")
def index():
    # render_template looks inside the templates/ folder and passes
    # keyword arguments to the template as variables.
    return render_template("index.html", name="Sadcattooo", tickets=TICKETS)


@app.route("/queue/<int:ticket_id>")
def ticket(ticket_id):
    # <int:ticket_id> only matches numbers, so /queue/abc returns 404.
    return render_template("ticket.html", ticket_id=ticket_id)

@app.route("/join")
def join_form():
    return render_template("join.html")

@app.route("/staff")
def staff_dashboard():
    return "Staff dashboard coming soon"

@app.route("/hello")
def hello():
    # The plain-string version from the Routes slide.
    return "Hello, CCC181!"


if __name__ == "__main__":
    # Lets you also start the app with: python app.py
    app.run(debug=True)


