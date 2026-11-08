"""CCC181 Week 2: a "Hello, Flask" starter app.

Run it with:
    flask --app app run --debug
then open http://127.0.0.1:5000
"""
import os
from datetime import datetime, timedelta, timezone

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

PH_TIME = timezone(timedelta(hours=8))  # Philippine time has no daylight saving


@app.template_filter("local")
def local_time(value):
    """Show a database time in Philippine time, e.g. Oct 26, 08:01 AM."""
    return value.astimezone(PH_TIME).strftime("%b %d, %I:%M %p") if value else ""


@app.template_filter("minutes_since")
def minutes_since(value):
    """Whole minutes between a database time and now."""
    if not value:
        return 0
    return int((datetime.now(timezone.utc) - value).total_seconds() // 60)


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


COUNTERS = [1, 2, 3]
CLERK = "DocG"


@app.route("/")
def index():
    tickets = db.session.scalars(
        db.select(Ticket)
        .where(Ticket.status.in_(["waiting", "called"]))
        .order_by(Ticket.created_at)).all()
    return render_template("index.html", name="Sadcattooo", tickets=tickets)


def people_ahead(t):
    """Count tickets still waiting for the same service that joined before t."""
    stmt = (db.select(func.count())
            .select_from(Ticket)
            .where(Ticket.service_id == t.service_id,
                   Ticket.status == "waiting",
                   Ticket.created_at < t.created_at))
    return db.session.scalar(stmt)


def latest_called(t):
    """The most recently called ticket for the same service as t (or None)."""
    return db.session.scalar(
        db.select(Ticket)
        .where(Ticket.service_id == t.service_id, Ticket.status == "called")
        .order_by(Ticket.id.desc())
        .limit(1))


@app.get("/queue/<int:ticket_id>")
def ticket(ticket_id):
    t = db.get_or_404(Ticket, ticket_id)
    return render_template("ticket.html", ticket=t, service=t.service,
                           ahead=people_ahead(t), now_serving=latest_called(t))


@app.post("/queue/<int:ticket_id>/leave")
def leave(ticket_id):
    t = db.get_or_404(Ticket, ticket_id)
    if t.status in ("waiting", "called"):
        t.status = "left"
        db.session.commit()
        flash("You left the queue.", "success")
    return redirect(url_for("ticket", ticket_id=t.id))


@app.get("/queue/<int:ticket_id>/status.json")
def ticket_status(ticket_id):
    t = db.get_or_404(Ticket, ticket_id)
    serving = latest_called(t)
    return {"status": t.status, "ahead": people_ahead(t),
            "now_serving": ticket_label(serving) if serving else None}


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
    return db.session.get(Ticket, ticket_id)


@app.template_global()
def ticket_service(t):
    return t.service


@app.template_global()
def ticket_label(t):
    
    return f"{t.service.name[:1].upper()}-{t.id}"


def current_counter():
    return session.get("counter", COUNTERS[0])


def serving_at(counter):
    """The ticket currently called at this counter (counters live in the session,
    because the tickets table has no counter column)."""
    ticket_id = session.get("serving", {}).get(str(counter))
    t = db.session.get(Ticket, ticket_id) if ticket_id else None
    return t if t is not None and t.status == "called" else None


def get_clerk():
    """The clerk user who verifies tickets; created the first time it is needed."""
    clerk = db.session.scalar(db.select(User).where(User.role == "clerk").limit(1))
    if clerk is None:
        clerk = User(role="clerk")
        db.session.add(clerk)
        db.session.flush()
    return clerk


def back_to_dashboard():

    return redirect(url_for("staff_dashboard",
                            service_id=request.form.get("service_id", type=int)))


def call_ticket(t, counter):
    
    busy = serving_at(counter)
    if busy is not None and busy.id != t.id:
        flash(f"Counter {counter} is still serving {ticket_label(busy)}. "
              "Complete or skip it first.", "warning")
        return
    t.status = "called"
    t.called_at = func.now()
    db.session.commit()
    session["serving"] = {**session.get("serving", {}), str(counter): t.id}
    flash(f"Calling {ticket_label(t)} to Counter {counter}.", "info")


@app.get("/staff")
def staff_dashboard():
    service_id = request.args.get("service_id", type=int)
    stmt = (db.select(Ticket)
            .where(Ticket.status.in_(["waiting", "called"]))
            .order_by(Ticket.created_at))
    if service_id:
        stmt = stmt.where(Ticket.service_id == service_id)
    queue = db.session.scalars(stmt).all()

    services = all_services()
    counts = {s.id: 0 for s in services}
    waiting = {s.id: 0 for s in services}
    rows = db.session.execute(
        db.select(Ticket.service_id, Ticket.status, func.count())
        .where(Ticket.status.in_(["waiting", "called"]))
        .group_by(Ticket.service_id, Ticket.status)).all()
    for sid, status, n in rows:
        counts[sid] = counts.get(sid, 0) + n
        if status == "waiting":
            waiting[sid] = waiting.get(sid, 0) + n

    today = datetime.now(PH_TIME).replace(hour=0, minute=0, second=0, microsecond=0)
    served_count = db.session.scalar(
        db.select(func.count()).select_from(Ticket)
        .where(Ticket.status.in_(["served", "completed"]),
               Ticket.created_at >= today))
    avg_seconds = db.session.scalar(
        db.select(func.avg(func.extract("epoch", Ticket.called_at - Ticket.created_at)))
        .where(Ticket.called_at.is_not(None)))

    counter = current_counter()
    return render_template(
        "staff.html", queue=queue, services=services, selected=service_id,
        counts=counts, waiting=waiting, total=sum(counts.values()),
        now_serving=serving_at(counter), counter=counter, counters=COUNTERS,
        clerk=CLERK, served_count=served_count,
        avg_wait=round(avg_seconds / 60) if avg_seconds is not None else None)


@app.post("/staff/counter")
def set_counter():
    counter = request.form.get("counter", type=int)
    if counter in COUNTERS:
        session["counter"] = counter
    return back_to_dashboard()


@app.post("/staff/call-next/<int:service_id>")
def call_next(service_id):
    service = db.get_or_404(Service, service_id)
    next_ticket = db.session.scalar(
        db.select(Ticket)
        .where(Ticket.service_id == service_id, Ticket.status == "waiting")
        .order_by(Ticket.created_at, Ticket.id)
        .limit(1))
    if next_ticket is not None:
        call_ticket(next_ticket, current_counter())
    else:
        flash(f"No one is waiting for {service.name}.", "warning")
    return back_to_dashboard()


@app.post("/staff/tickets/<int:ticket_id>/<action>")
def staff_action(ticket_id, action):
    t = find_ticket(ticket_id)
    if t is None or action not in ("call", "serve", "skipped", "verify"):
        abort(404)

    if action == "verify":
        t.verified_by = get_clerk().id
        t.verified_at = func.now()
        db.session.commit()
        flash(f"{ticket_label(t)} verified.", "success")
    elif t.status not in ("waiting", "called"):
        flash(f"{ticket_label(t)} is already {t.status}.", "warning")
    elif action == "call":
        call_ticket(t, current_counter())
    else:
        t.status = "served" if action == "serve" else "skipped"
        db.session.commit()
        flash(f"{ticket_label(t)} marked {t.status}.", "info")
    return back_to_dashboard()


@app.route("/hello")
def hello():

    return "Hello, CCC181!"


if __name__ == "__main__":

    app.run(debug=True)