from flask_sqlalchemy import SQLAlchemy

from passlib.hash import bcrypt_sha256

import datetime
import hashlib

def sha512(string):
    return hashlib.sha512(string).hexdigest()

db = SQLAlchemy()

class Member(db.Model):
    username = db.Column(db.String(20), unique=True, primary_key=True)
    password = db.Column(db.String(256))
    firstname = db.Column(db.String(20))
    lastname = db.Column(db.String(20))
    email = db.Column(db.String(20), index=True, unique=True)
    zipcode = db.Column(db.Integer)

    def __init__(self, username, password, firstname, lastname, email, zip):
        self.username = username
        self.password = bcrypt_sha256.encrypt(password)
        self.firstname = firstname
        self.lastname = lastname
        self.zip = zip

    def __repr__(self):
        return '<Member %r>' % self.username

class Groups(db.Model):
    group_id = db.Column(db.Integer, primary_key=True)
    group_name = db.Column(db.String(20))
    description = db.Column(db.Text)
    username = db.Column(db.String(20), db.ForeignKey('member.username'))
    category = db.Column(db.String(80))

    def __init__(self, group_name, description, username, category):
        self.group_name = group_name
        self.description = description
        self.username = username
        self.category = category

    def __repr__(self):
        return '<Group %r>' % self.group_name

class Interest(db.Model):
    interest_name = db.Column(db.String(20), default="", primary_key=True)

    def __init__(self, interest_name=""):
        self.interest_name = interest_name

    def __repr__(self):
        return '<Interest %r>' % self.interest_name

class GroupInterest(db.Model):
    __tablename__ = "about"
    interest_name = db.Column(
            db.String(20), db.ForeignKey('interest.interest_name'), default=""
        )
    group_id = db.Column(
            db.Integer, db.ForeignKey('groups.group_id')
        )
    i = db.Column(db.Integer, primary_key=True)

    def __init__(self, group_id, interest_name=""):
        self.interest_name = interest_name
        self.group_id = group_id

    def __repr__(self):
        return '<GroupInterest %r>' % self.group_id

class MemberInterest(db.Model):
    __tablename__ = "interested_in"
    interest_name = db.Column(
            db.String(20), db.ForeignKey('interest.interest_name'), default=""
        )
    username = db.Column(
            db.String(20), db.ForeignKey('member.username')
        )
    i = db.Column(db.Integer, primary_key=True)

    def __init__(self, interest_name, username):
        self.interest_name = interest_name
        self.username = username

    def __repr__(self):
        return '<MemberInterest %r>' % self.username

class GroupUser(db.Model):
    __tablename__ = "belongs_to"
    group_id = db.Column(
            db.Integer, db.ForeignKey('groups.group_id')
        )
    username = db.Column(
            db.String(20), db.ForeignKey('member.username')
        )
    authorized = db.Column(db.Boolean)
    i = db.Column(db.Integer, primary_key=True)

    def __init__(self, group_id, username, authorized):
        self.group_id = group_id
        self.username = username
        self.authorized = authorized

    def __repr__(self):
        return '<GroupUser %r>' % self.group_id

class Location(db.Model):
    lname = db.Column(db.String(20), default="", primary_key=True)
    zipcode = db.Column(db.Integer, index=True, unique=True)
    street = db.Column(db.String(20), default="")
    city = db.Column(db.String(20), default="")
    description = db.Column(db.Text)
    latitude = db.Column(db.Integer)
    longitude = db.Column(db.Integer)

    def __init__(self, zip, description, latitude, longitude, lname="", street="", city=""):
        self.zip = zip
        self.description = description
        self.latitude = latitude
        self.longitude = longitude
        self.lname = lname
        self.street = street
        self.city = city

    def __repr__(self):
        return '<Location %r>' % self.lname

class Events(db.Model):
    event_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    start_time = db.Column(db.DateTime(timezone=True))
    end_time = db.Column(db.DateTime(timezone=True))
    group_id = db.Column(db.Integer, db.ForeignKey('groups.group_id'))
    lname = db.Column(db.String(20), db.ForeignKey('location.lname'))
    zipcode = db.Column(db.Integer, db.ForeignKey('location.zipcode'))

    def __init__(self, event_id, title, description, start_time, end_time, group_id, lname, zip):
        self.event_id = event_id
        self.title = title
        self.description = description
        self.start_time = start_time
        self.end_time = end_time
        self.group_id = group_id
        self.lname = lname
        self.zip = zip

    def __repr__(self):
        return '<Event %r>' % self.lname

class EventUser(db.Model):
    __tablename__ = "attend"
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'))
    username = db.Column(db.String(20), db.ForeignKey('member.username'), default="")
    rsvp = db.Column(db.Boolean)
    rating = db.Column(db.Integer)
    i = db.Column(db.Integer, primary_key=True)

    def __init__(self, event_id, rsvp, rating, username=""):
        self.event_id = event_id
        self.rsvp = rsvp
        self.rating = rating
        self.username = username

    def __repr__(self):
        return '<EventUser %r>' % self.username
