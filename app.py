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
    {"number": 3001, "service_id": 1, "status": "done"},
    {"number": 1001, "service_id": 1, "status": "waiting"},
    {"number": 2001, "service_id": 2, "status": "in service"},
]


SERVICES = [
    {"service_id": 1, "name": "Regular service", "prefix": "R"},
    {"service_id": 2, "name": "Priority service", "prefix": "P"}
]



@app.route("/")
def index():
    # render_template looks inside the templates/ folder and passes
    # keyword arguments to the template as variables.
    return render_template("index.html", name="Sadcattooo", tickets=TICKETS)


@app.get("/queue/<int:ticket_id>")
def ticket(ticket_id):
    t = next((t for t in TICKETS if t["number"] == ticket_id), None)
    if t is None:
        abort(404)

    ahead = [x for x in TICKETS
             if x["service_id"] == t["service_id"]
             and x["status"] == "waiting"
             and x["number"] < t["number"]]

    service = next(s for s in SERVICES if s["service_id"] == t["service_id"])

    # Most recent ticket currently called for this service (for "Now serving")
    called = [x for x in TICKETS
              if x["service_id"] == t["service_id"] and x["status"] == "called"]
    now_serving = called[-1] if called else None

    return render_template("ticket.html", ticket=t, service=service,
                           ahead=len(ahead), now_serving=now_serving)


@app.post("/queue/<int:ticket_id>/leave")
def leave(ticket_id):
    t = next((t for t in TICKETS if t["number"] == ticket_id), None)
    if t is None:
        abort(404)
    if t["status"] in ("waiting", "called"):
        t["status"] = "no-show"
        flash("You left the queue.", "success")
    return redirect(url_for("index"))


@app.get("/join")
def join_form():
    return render_template("join.html", services=SERVICES, form={})


@app.post("/join")
def join():
    form = request.form
    service_id = form.get("service_id", type=int)

    errors = {}
    if service_id not in [s["service_id"] for s in SERVICES]:
        errors["service_id"] = "Choose a service."

    if errors:
        flash("Please fix the highlighted fields.", "danger")
        return render_template("join.html", services=SERVICES, form=form, errors=errors), 400

    number = TICKETS[-1]["number"] + 1 if TICKETS else 1
    TICKETS.append({"number": number, "service_id": service_id, "status": "waiting"})
    flash(f"You joined the queue. Your ticket is #{number}. Category: {next((s['name'] for s in SERVICES if s['service_id'] == service_id), 'Unknown')}", "success")
    return redirect(url_for("ticket", ticket_id=number))


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


