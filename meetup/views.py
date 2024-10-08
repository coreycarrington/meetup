from flask import render_template, Blueprint, request, session, redirect, url_for, flash
from meetup.config import SQLALCHEMY_DATABASE_URI
from meetup.models import db, Member
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from meetup import twitter

import datetime, json, requests
from time import gmtime, strftime

views = Blueprint('views', __name__)

eng = create_engine(SQLALCHEMY_DATABASE_URI)

def sendmail(addr, text):
    return requests.post(
        "https://api.mailgun.net/v3/sandboxa934a03bddc04f4c921855c9c6fbc28e.mailgun.org/messages",
        auth=("api", "key-886baf72f7a96c51b9f14155716d86c1"),
        data={"from": "Meetup",
              "to": [addr],
              "subject": "Message from Meetup",
              "text": text})

@views.route('/', methods=['GET', 'POST'])
def index():
    interest = ""
    start_time = str(datetime.datetime.now())
    end_time = str(datetime.datetime.now() + datetime.timedelta(days = 5))
    if request.method == 'POST':
        form_type = request.form.get('type')
        if form_type == "group":
            interest = request.form.get('interest')
        elif form_type == "event":
            start_time = request.form.get('starttime')
            end_time = request.form.get('endtime')

    interests = [_ for _ in db.session.execute(text("SELECT interest_name FROM about"))]

    groups = [_ for _ in db.session.execute(text("SELECT groups.* FROM groups LEFT JOIN about ON about.group_id = groups.group_id WHERE about.interest_name = :Interest"), {"Interest": interest})]

    events = [_ for _ in db.session.execute(
        text("SELECT events.event_id, events.title, events.description, events.start_time, events.end_time, events.group_id, location.*, groups.group_name \
            FROM events LEFT JOIN location ON (location.lname = events.lname AND location.zipcode = events.zipcode) \
            LEFT JOIN groups ON events.group_id = groups.group_id \
            WHERE (start_time >= :StartRange AND start_time <= :EndRange) OR \
            (end_time >= :StartRange AND end_time <= :EndRange)"),
        {"StartRange": start_time, "EndRange": end_time}
        )]
    return render_template('index.html', groups=groups, events=events, interests=interests, start_time=start_time, end_time=end_time)

@views.route('/dotweet', methods=['POST'])
def dotweet():
    """Calls the remote twitter API to create a new status update."""

    event = request.form.get("event")
    status = "I am going to %s. Come join me!" % event
    if not status:
        return redirect(url_for('index'))
    resp = twitter.post('statuses/update.json', data={
        'status':       status
    })
    if resp.status == 403:
        flash('Your tweet was too long.')
    elif resp.status == 401:
        flash('Authorization error with Twitter.')
    else:
        flash('Successfully tweeted your tweet (ID: #%s)' % resp.data['id'])
    return redirect(url_for('index'))

@views.route('/tweet', methods=['POST'])
def tweet():
    return twitter.authorize(callback=url_for('.dotweet'))

@views.route('/home', methods=['GET', 'POST'])
def home():
    msg = ""
    errors = []
    if "msg" in request.args:
        msg = request.args["msg"]
    if "errors" in request.args:
        errors = request.args["errors"]

    username = session["username"] if "username" in session else None 
    if username == None:
        return "NO SIR!"

    event_search = ""
    start_time = str(datetime.datetime.now())
    end_time = str(datetime.datetime.now() + datetime.timedelta(days = 5))
    if request.method == 'POST':
        event_search = request.form.get("search")
        start_time = request.form.get('starttime')
        end_time = request.form.get('endtime')

    events = [_ for _ in db.session.execute(
        text("SELECT events.event_id, events.title, events.description, events.start_time, events.end_time, events.group_id, location.*, groups.group_name, users_events.rsvp \
            FROM (SELECT * FROM attend WHERE attend.username = :Username) as users_events \
            LEFT JOIN events ON events.event_id = users_events.event_id \
            LEFT JOIN location ON (location.lname = events.lname AND location.zipcode = events.zipcode) \
            LEFT JOIN groups ON events.group_id = groups.group_id \
            WHERE (start_time >= :StartRange AND start_time <= :EndRange) OR \
            (end_time >= :StartRange AND end_time <= :EndRange) AND title LIKE \"%%%s%%\"" % event_search),
        {"StartRange": start_time, "EndRange": end_time, "EventTitle": event_search, "Username": username}
        )]

    groups = [_ for _ in db.session.execute(text("SELECT * FROM groups LEFT JOIN belongs_to ON groups.group_id = belongs_to.group_id \
        WHERE belongs_to.username = :Username"), {"Username": username})]

    group_members = []
    for group in groups:
        group_members.append([_ for _ in db.session.execute(text("SELECT username FROM belongs_to WHERE group_id = :GroupID"), {"GroupID": group[0]})])

    event_members = []
    for event in events:
        event_members.append([_ for _ in db.session.execute(text("SELECT username FROM attend WHERE event_id = :EventID"), {"EventID": event[0]})])

    interests = [_ for _ in db.session.execute(text("SELECT interest_name FROM interested_in WHERE username = :Username"),
        {"Username": username})]
    return render_template('home.html', events=events, groups=groups, interests=interests,
        event_search=event_search, start_time=start_time, end_time=end_time, msg=msg, group_members=group_members,
        event_members=event_members, errors=errors)

@views.route('/send/reminder', methods=['POST'])
def send_reminder():
    username = session["username"] if "username" in session else None 
    start_time = request.form.get('starttime')
    end_time = request.form.get('endtime')
    if username == None:
        return "NO SIR!"

    events = ["<p>Meetup: {0}, Description: {1}</p>".format(_[1], _[2]) for _ in db.session.execute(
        text("SELECT events.event_id, events.title, events.description, events.start_time, events.end_time, events.group_id, location.*, groups.group_name, users_events.rsvp \
            FROM (SELECT * FROM attend WHERE attend.username = :Username) as users_events \
            LEFT JOIN events ON events.event_id = users_events.event_id \
            LEFT JOIN location ON (location.lname = events.lname AND location.zipcode = events.zipcode) \
            LEFT JOIN groups ON events.group_id = groups.group_id \
            WHERE (start_time >= :StartRange AND start_time <= :EndRange) OR \
            (end_time >= :StartRange AND end_time <= :EndRange)"),
        {"StartRange": start_time, "EndRange": end_time, "Username": username}
        )]

    email = [_ for _ in db.session.execute(text("SELECT email FROM member WHERE username = :Username"), {
        "Username": username
        })][0]

    sendmail(email, "You have some events coming up, here they are: %s" % json.dumps(events))

    return redirect(url_for(".home", msg="Sent Reminders"))

@views.route('/search/event', methods=['POST', 'GET'])
def search_events():
    results = []
    search = ""
    if request.method == "POST":
        search = request.form.get("search")
        results = [_ for _ in db.session.execute(text("SELECT events.event_id, events.title, events.description, events.start_time, events.end_time, events.group_id, location.*, groups.group_name FROM event \
            LEFT JOIN location ON (location.lname = events.lname AND location.zipcode = events.zipcode) \
            LEFT JOIN groups ON events.group_id = groups.group_id WHERE title LIKE \"%%%s%%\"" % search),
            {"Search": search})]

    return render_template('search_event.html', results=results, search=search)

@views.route('/search/group', methods=['POST', 'GET'])
def search_groups():
    search = ''
    results = []
    if request.method == "POST":
        search  = request.form.get("search")
        results = [_ for _ in db.session.execute(text("SELECT * FROM groups WHERE group_name LIKE \"%%%s%%\"" % search))]

    return render_template('search_group.html', results=results, search=search)

@views.route('/join/event', methods=['POST'])
def join_event():
    errors = []
    username = session["username"] if "username" in session.keys() else None 
    event_id = request.form.get("eventid")
    if username == None:
        return "NO SIR!"

    user_in_group = len([_ for _ in db.session.execute(
        text("SELECT username FROM attend WHERE \
            event_id = :EventID AND username = :Username"),
        {"Username": username, "EventID": event_id})]) > 0

    if not user_in_group:
        db.session.execute(
            text("INSERT INTO attend (event_id, username, rsvp) \
                  VALUES (:EventID, :Username, :RSVP)"),
            {"EventID": event_id, "Username": username, "RSVP": 1})
    else:
        errors.append("Not in group")

    db.session.commit()

    return redirect(url_for(".home", msg="Joined Event", errors=errors))

@views.route('/join/group', methods=['POST'])
def join_group():
    errors = []
    username = session["username"] if "username" in session.keys() else None 
    group_id = request.form.get("groupid")
    if username == None:
        return "NO SIR!"

    user_in_group = len([_ for _ in db.session.execute(
        text("SELECT username FROM belongs_to WHERE \
            group_id = :GroupID AND username = :Username"),
        {"Username": username, "GroupID": group_id})]) > 0

    if not user_in_group:
        db.session.execute(
            text("INSERT INTO belongs_to (group_id, username, authorized) \
                  VALUES (:GroupID, :Username, :Authorized)"),
            {"GroupID": group_id, "Username": username, "Authorized": 0})

    db.session.commit()

    return redirect(url_for(".home", msg="Joined Group"))

@views.route('/create/group', methods=['GET', 'POST'])
def create_group():
    if request.method == "POST":
        errors = []
        name = request.form.get('name')
        username = session["username"] if "username" in session.keys() else None 
        description = request.form.get('description')
        category = request.form.get('category')
        if username == None:
            return "NO SIR!"

        db.session.execute(
            text("INSERT INTO groups (group_name, description, username, category) \
                  VALUES (:Name, :Description, :Username, :Category)"),
            {"Name": name, "Description": description, "Username": username, "Category": category})
        db.session.commit()
        group_id = [_ for _ in db.session.execute(
            text("SELECT group_id FROM groups WHERE group_name = :Name"),
            {"Name": name})][0][0]

        db.session.execute(
            text("INSERT INTO belongs_to (group_id, username, authorized) \
                  VALUES (:GroupID, :Username, :Authorized)"),
            {"GroupID": group_id, "Username": username, "Authorized": 1})
        db.session.commit()

        interest_exists = len([_ for _ in db.session.execute(
            text("SELECT interest_name FROM interest WHERE \
                interest_name = :Interest"), {"Interest": category})]) > 0

        if not interest_exists:
            db.session.execute(
                text("INSERT INTO interest (interest_name) VALUES (:Interest)"),
                {"Interest": category})
            db.session.commit()

        db.session.execute(
            text("INSERT INTO about (interest_name, group_id) \
                  VALUES (:Category, :GroupID)"),
            {"GroupID": group_id, "Category": category})
        db.session.commit()

        return redirect(url_for(".home", msg="Created Group"))
    return render_template('create_group.html')

@views.route('/create/event', methods=['GET', 'POST'])
def create_event():
    username = session["username"] if "username" in session.keys() else None 
    if username == None:
        return "NO SIR!"

    start_time = str(datetime.datetime.now())
    end_time = str(datetime.datetime.now() + datetime.timedelta(days = 1))

    groups = [_[0] for _ in db.session.execute(text("SELECT belongs_to.group_id, group_name FROM belongs_to \
        LEFT JOIN groups ON belongs_to.group_id = groups.group_id \
        WHERE belongs_to.username = :Username AND authorized = 1"), {"Username": username})]

    if request.method == "POST":
        errors = []
        title = request.form.get('title')
        description = request.form.get('description')
        start_time = request.form.get('starttime')
        end_time = request.form.get('endtime')
        group_id = request.form.get('groupid')

        if int(group_id) not in groups:
            return "NO SIR!"

        location_name = request.form.get('locationname')
        location_description = request.form.get('locationdescription')
        location_zip = request.form.get('locationzip')
        location_street = request.form.get('locationstreet')
        location_city = request.form.get('locationcity')
        location_lat = request.form.get('locationlat')
        location_long = request.form.get('locationlong')

        event_dict = {"Title": title, "GroupID": group_id, "Description": description,
            "StartTime": start_time, "EndTime": end_time, "LocationName": location_name,
            "LocationZip": location_zip}

        location_dict = {"LocationName": location_name,
            "LocationDescription": location_description, "LocationZip": location_zip,
            "LocationStreet": location_street, "LocationCity": location_city,
            "LocationLat": location_lat, "LocationLong": location_long}

        db.session.execute(
            text("INSERT INTO location (lname, zip, street, city, description, latitude, longitude) \
                  VALUES (:LocationName, :LocationZip, :LocationStreet, :LocationCity, :LocationDescription, :LocationLat, :LocationLong)"),
            location_dict)
        db.session.commit()

        db.session.execute(
            text("INSERT INTO events (title, description, start_time, end_time, group_id, lname, zip) \
                  VALUES (:Title, :Description, :StartTime, :EndTime, :GroupID, :LocationName, :LocationZip)"),
            event_dict)
        db.session.commit()

        event_id = [_ for _ in db.session.execute(
            text("SELECT event_id FROM events WHERE title = :Title"),
            {"Title": title})][0][0]

        db.session.execute(
            text("INSERT INTO attend (event_id, username, rsvp) \
                  VALUES (:EventID, :Username, :RSVP)"),
            {"EventID": event_id, "Username": username, "RSVP": 1})
        db.session.commit()
        return redirect(url_for(".home", msg="Created Event"))

    return render_template('create_event.html', groups=groups, start_time=start_time, end_time=end_time)

@views.route('/rate', methods=['POST'])
def rate():
    event_id = request.form.get("eventid")
    rating = request.form.get("rating")
    username = session["username"]

    try:
        rating = int(rating)
    except:
        errors = "Not a valid rating"
        return redirect(url_for(".home", msg="", errors=errors))

    if rating < 0 or rating > 10:
        errors = "Not a valid rating"
        return redirect(url_for(".home", msg="", errors=errors))

    db.session.execute(
        text("UPDATE attend SET rating = :Rating WHERE username = :Username AND event_id = :EventID"),
        {"Rating": rating, "Username": username, "EventID": event_id})
    db.session.commit()

    return redirect(url_for(".home", msg="Added Rating"))

@views.route('/create/interest', methods=['POST'])
def create_interest():
    interest = request.form.get("interest")
    username = session["username"]

    interest_exists = len([_ for _ in db.session.execute(
        text("SELECT interest_name FROM interest WHERE \
            interest_name = :Interest"), {"Interest": interest})]) > 0

    if not interest_exists:
        db.session.execute(
            text("INSERT INTO interest (interest_name) VALUES (:Interest)"),
            {"Interest": interest})
        db.session.commit()

    interested_in_exists = len([_ for _ in db.session.execute(
        text("SELECT interest_name FROM interested_in WHERE \
            interest_name = :Interest AND username = :Username"), {"Interest": interest, "Username": username})]) > 0

    if not interested_in_exists:
        db.session.execute(text("INSERT INTO interested_in (interest_name, username) \
            VALUES (:Interest, :Username)"),
            {"Interest": interest, "Username": username})
        db.session.commit()

    return redirect(url_for(".home", msg="Added Interest"))

@views.route('/logout')
def logout():
    session.clear()
    return render_template('logout.html')
