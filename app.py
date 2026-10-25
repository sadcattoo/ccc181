"""CCC181 Week 2: a "Hello, Flask" starter app.

Run it with:
    flask --app app run --debug
then open http://127.0.0.1:5000
"""
from flask import Flask, abort, flash, redirect, render_template, request, session, url_for

from datetime import datetime, timedelta


app = Flask(__name__)
app.secret_key = "dev-only-change-me" 

# Sample data for the demo. A real app would load this from a database later.
def ago(minutes):
    return datetime.now() - timedelta(minutes=minutes)


TICKETS = [
    {"number": 1001, "service_id": 1, "status": "served",  "issued_at": ago(40), "called_at": ago(32), "counter": 1},
    {"number": 2001, "service_id": 2, "status": "called",  "issued_at": ago(14), "called_at": ago(2),  "counter": 2},
    {"number": 3001, "service_id": 2, "status": "waiting", "issued_at": ago(12)},
    {"number": 1004, "service_id": 1, "status": "waiting", "issued_at": ago(7)},
    {"number": 1002, "service_id": 1, "status": "waiting", "issued_at": ago(3)},
    {"number": 1006, "service_id": 2, "status": "waiting", "issued_at": ago(1)},
]

SERVICES = [
    {"service_id": 1, "name": "Regular",  "prefix": "R", "rank": 1},
    {"service_id": 2, "name": "Priority", "prefix": "P", "rank": 0},
]

COUNTERS = [1, 2, 3]
CLERK = "DocG"




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
    TICKETS.append({"number": number, "service_id": service_id, "status": "waiting", "issued_at": datetime.now()})
    flash(f"You joined the queue. Your ticket is #{number}. Category: {next((s['name'] for s in SERVICES if s['service_id'] == service_id), 'Unknown')}", "success")
    return redirect(url_for("ticket", ticket_id=number))
    

def find_ticket(ticket_id):
    return next((t for t in TICKETS if t["number"] == ticket_id), None)


@app.template_global()
def ticket_service(t):
    return next(s for s in SERVICES if s["service_id"] == t["service_id"])


@app.template_global()
def ticket_label(t):
    return f'{ticket_service(t)["prefix"]}-{t["number"]}'


def current_counter():
    return session.get("counter", COUNTERS[0])


def back_to_dashboard():
    # keeps the service filter after an action (None is dropped by url_for)
    return redirect(url_for("staff_dashboard",
                            service_id=request.form.get("service_id", type=int)))


def call_ticket(t, counter):
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

    # priority lane first, then called before waiting, then by number
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
    # The plain-string version from the Routes slide.
    return "Hello, CCC181!"


if __name__ == "__main__":
    # Lets you also start the app with: python app.py
    app.run(debug=True)