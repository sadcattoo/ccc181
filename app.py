"""CCC181 Week 2: a "Hello, Flask" starter app.

Run it with:
    flask --app app run --debug
then open http://127.0.0.1:5000
"""
import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for
from flask_migrate import Migrate
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from models import Service, Ticket, User, db

load_dotenv()

app = Flask(__name__)
app.secret_key = "dev-only-change-me"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_ECHO"] = os.environ.get("SQLALCHEMY_ECHO") == "1"

db.init_app(app)
migrate = Migrate(app, db)


@app.cli.command("seed")
def seed():
    """Add the starting services if they are not there yet."""
    starting = [("Regular", 10), ("Priority", 10)]
    for name, minutes in starting:
        exists = db.session.scalar(db.select(Service).filter_by(name=name))
        if exists is None:
            db.session.add(Service(name=name, avg_minutes=minutes))
    db.session.commit()
    print("Services are ready.")


# SERVICES and TICKETS (the Week 3 lists) are gone. Every route that still
# mentions them below is replaced in Parts 8 and 9.

COUNTERS = [1, 2, 3]
CLERK = "DocG"


@app.route("/")
def index():
    # Part 8 replaces this with a database query.
    return render_template("index.html", name="Sadcattooo", tickets=TICKETS)


@app.get("/queue/<int:ticket_id>")
def ticket(ticket_id):
    t = db.get_or_404(Ticket, ticket_id)

    ahead = db.session.scalar(
        db.select(func.count()).select_from(Ticket)
        .where(Ticket.service_id == t.service_id,
               Ticket.status == "waiting",
               Ticket.id < t.id))

    now_serving = db.session.scalar(
        db.select(Ticket)
        .where(Ticket.service_id == t.service_id, Ticket.status == "called")
        .order_by(Ticket.id.desc()))

    return render_template("ticket.html", ticket=t, service=t.service, ahead=ahead, now_serving=now_serving)


@app.post("/queue/<int:ticket_id>/leave")
def leave(ticket_id):
    # Part 8 replaces this.
    t = next((t for t in TICKETS if t["number"] == ticket_id), None)
    if t is None:
        abort(404)
    if t["status"] in ("waiting", "called"):
        t["status"] = "no-show"
        flash("You left the queue.", "success")
    return redirect(url_for("index"))


@app.get("/queue/<int:ticket_id>/status.json")
def ticket_status(ticket_id):
    # Part 8 replaces this.
    t = find_ticket(ticket_id)
    if t is None:
        abort(404)

    ahead = sum(1 for x in TICKETS
                if x["service_id"] == t["service_id"]
                and x["status"] == "waiting" and x["number"] < t["number"])

    called = [x for x in TICKETS
              if x["service_id"] == t["service_id"] and x["status"] == "called"]
    now_serving = called[-1] if called else None

    return {
        "status": t["status"],
        "ahead": ahead,
        "counter": t.get("counter"),
        "now_serving": ticket_label(now_serving) if now_serving else None,
    }


def all_services():
    return db.session.scalars(db.select(Service).order_by(Service.name)).all()


@app.get("/join")
def join_form():
    return render_template("join.html", services=all_services(), form={}, errors={})


@app.post("/join")
def join():
    form = request.form
    service_id = form.get("service_id", type=int)
    service = db.session.get(Service, service_id) if service_id else None
    # "Make it yours": your own column from Part 2b (tickets.priority_level).
    priority_level = form.get("priority_level", "regular")

    errors = {}
    if service is None:
        errors["service_id"] = "Choose a service."
    if priority_level not in ("regular", "pwd"):
        errors["priority_level"] = "Choose regular or PWD."

    if errors:
        flash("Please fix the highlighted fields.", "danger")
        return render_template("join.html", services=all_services(),
                               form=form, errors=errors), 400

    # users has no name or email in this system, only a role. tickets.user_id
    # is NOT NULL, so every ticket needs a user row: make an anonymous customer.
    customer = User(role="customer")
    ticket = Ticket(user=customer, service=service, priority_level=priority_level)
    db.session.add(ticket)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("Something went wrong saving your ticket. Please try again.", "danger")
        return render_template("join.html", services=all_services(),
                               form=form, errors={}), 409

    flash(f"You joined the queue. Your ticket is #{ticket.id}.", "success")
    return redirect(url_for("ticket", ticket_id=ticket.id))


def find_ticket(ticket_id):
    # Part 8/9 replaces this.
    return next((t for t in TICKETS if t["number"] == ticket_id), None)


@app.template_global()
def ticket_service(t):
    return t.service


@app.template_global()
def ticket_label(t):
    # services has no prefix column, so use the first letter of the name:
    # Regular -> R-12, Priority -> P-13
    return f"{t.service.name[:1].upper()}-{t.id}"


def current_counter():
    return session.get("counter", COUNTERS[0])


def back_to_dashboard():

    return redirect(url_for("staff_dashboard",
                            service_id=request.form.get("service_id", type=int)))


def call_ticket(t, counter):
    # Part 9 replaces everything from here down to /hello.
    busy = next((x for x in TICKETS
                 if x["status"] == "called" and x.get("counter") == counter and x is not t), None)
    if busy:
        flash(f"Counter {counter} is still serving {ticket_label(busy)}. "
              "Complete or skip it first.", "warning")
        return
    t["status"] = "called"
    t["counter"] = counter
    t["called_at"] = datetime.now()
    flash(f"Calling {ticket_label(t)} to Counter {counter}.", "info")


@app.get("/staff")
def staff_dashboard():
    service_id = request.args.get("service_id", type=int)
    counter = current_counter()
    services = sorted(SERVICES, key=lambda s: s["rank"])
    rank = {s["service_id"]: s["rank"] for s in SERVICES}

    active = [t for t in TICKETS if t["status"] in ("waiting", "called")]
    active.sort(key=lambda t: (rank[t["service_id"]], t["status"] != "called", t["number"]))

    counts = {s["service_id"]: sum(t["service_id"] == s["service_id"] for t in active) for s in SERVICES}
    waiting = {s["service_id"]: sum(t["service_id"] == s["service_id"] and t["status"] == "waiting"
                                    for t in active) for s in SERVICES}

    queue = [t for t in active if t["service_id"] == service_id] if service_id else active
    rows = [{**t, "waited": int((datetime.now() - t["issued_at"]).total_seconds() // 60)}
            for t in queue]

    now_serving = next((t for t in active
                        if t["status"] == "called" and t.get("counter") == counter), None)

    waits = [(t["called_at"] - t["issued_at"]).total_seconds() / 60
             for t in TICKETS if t.get("called_at")]

    return render_template(
        "staff.html", queue=rows, services=services, counts=counts, waiting=waiting,
        total=len(active), selected=service_id, now_serving=now_serving,
        counter=counter, counters=COUNTERS, clerk=CLERK,
        served_count=sum(t["status"] == "served" for t in TICKETS),
        avg_wait=round(sum(waits) / len(waits)) if waits else None)


@app.post("/staff/counter")
def set_counter():
    counter = request.form.get("counter", type=int)
    if counter in COUNTERS:
        session["counter"] = counter
    return back_to_dashboard()


@app.post("/staff/call-next/<int:service_id>")
def call_next(service_id):
    service = next((s for s in SERVICES if s["service_id"] == service_id), None)
    if service is None:
        abort(404)
    waiting = sorted((t for t in TICKETS
                      if t["service_id"] == service_id and t["status"] == "waiting"),
                     key=lambda t: t["number"])
    if waiting:
        call_ticket(waiting[0], current_counter())
    else:
        flash(f"No one is waiting for {service['name']}.", "warning")
    return back_to_dashboard()


@app.post("/staff/tickets/<int:ticket_id>/<action>")
def staff_action(ticket_id, action):
    t = find_ticket(ticket_id)
    if t is None or action not in ("call", "serve", "no-show", "verify"):
        abort(404)

    if action == "verify":
        t["verified"] = True
        flash(f"{ticket_label(t)} verified.", "success")
    elif t["status"] not in ("waiting", "called"):
        flash(f"{ticket_label(t)} is already {t['status']}.", "warning")
    elif action == "call":
        call_ticket(t, current_counter())
    else:
        t["status"] = "served" if action == "serve" else "no-show"
        flash(f"{ticket_label(t)} marked {t['status']}.", "info")
    return back_to_dashboard()


@app.route("/hello")
def hello():

    return "Hello, CCC181!"


if __name__ == "__main__":

    app.run(debug=True)