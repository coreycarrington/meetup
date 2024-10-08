from flask import render_template, request, redirect, abort, jsonify, url_for, session, Blueprint
from meetup.models import db, Member

from itsdangerous import TimedSerializer, BadTimeSignature
from passlib.hash import bcrypt_sha256
from flask import current_app as app
from meetup.config import SQLALCHEMY_DATABASE_URI
from sqlalchemy import create_engine
from sqlalchemy.sql import text

import logging, time, re, os, hashlib

auth = Blueprint('auth', __name__)

def sendmail(addr, text):
    return requests.post(
        "https://api.mailgun.net/v3/sandboxa934a03bddc04f4c921855c9c6fbc28e.mailgun.org/messages",
        auth=("api", "key-886baf72f7a96c51b9f14155716d86c1"),
        data={"from": "Meetup",
              "to": [addr],
              "subject": "Message from Meetup",
              "text": text})

@auth.route('/reset_password', methods=['POST', 'GET'])
@auth.route('/reset_password/<data>', methods=['POST', 'GET'])
def reset_password(data=None):
    if data is not None and request.method == "GET":
        return render_template('reset_password.html', mode='set')
    if data is not None and request.method == "POST":
        try:
            s = TimedSerializer(app.config['SECRET_KEY'])
            name = s.loads(data.decode('base64'), max_age=1800)
        except BadTimeSignature:
            return render_template('reset_password.html', errors=['Your link has expired'])
        member = Member.query.filter_by(name=name).first()
        member.password = bcrypt_sha256.encrypt(request.form['password'].strip())
        db.session.commit()
        db.session.close()
        return redirect('/login')

    if request.method == 'POST':
        email = request.form['email'].strip()
        member = Member.query.filter_by(email=email).first()
        if not member:
            return render_template('reset_password.html', errors=['Check your email'])
        s = TimedSerializer(app.config['SECRET_KEY'])
        token = s.dumps(member.username)
        text = """
Did you initiate a password reset?

{0}/reset_password/{1}

""".format(app.config['HOST'], token.encode('base64'))

        sendmail(email, text)

        return render_template('reset_password.html', errors=['Check your email'])
    return render_template('reset_password.html')


@auth.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        errors = []
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        zipcode = request.form['zipcode']
        valid_zip = True
        try:
            zipcode = int(zipcode, 10)
        except:
            valid_zip = False

        name_len = len(username) == 0
        usernames = [_ for _ in db.session.execute(
            text("SELECT COUNT(*) as user_count FROM member WHERE username = :Username"),
            {"Username": username}
            )]
        username_used = usernames[0]["user_count"]
        emails = [_ for _ in db.session.execute(
            text("SELECT COUNT(*) as email_count FROM member WHERE email = :Email"),
            {"Email": email}
            )]
        email_used = emails[0]["email_count"]

        pass_short = len(password) == 0
        pass_long = len(password) > 128
        valid_email = re.match("[^@]+@[^@]+\.[^@]+", request.form['email'])

        if not valid_email:
            errors.append("That email doesn't look right")
        if not valid_zip:
            errors.append("Invalid zip code given")
        if username_used:
            errors.append('That username is already taken')
        if email_used:
            errors.append('That email has already been used')
        if pass_short:
            errors.append('Pick a longer password')
        if pass_long:
            errors.append('Pick a shorter password')
        if name_len:
            errors.append('Pick a longer username')

        if len(errors) > 0:
            return render_template('register.html', errors=errors)
        else:
            with app.app_context():
                member = Member(username, password, firstname, lastname, email, zipcode)
                db.session.add(member)
                db.session.commit()
            '''
            if mailserver():
                sendmail(request.form['email'], "You've successfully registered for Meetup")
            '''

        db.session.close()

        return redirect('/login')
    return render_template('register.html')


@auth.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        errors = []
        username = request.form['username']
        password = request.form['password']
        member = [_ for _ in db.session.execute(
            text("SELECT password FROM member WHERE username = :Username"),
            {"Username": username}
            )]
        if len(member) == 1 and bcrypt_sha256.verify(password, member[0][0]):
            try:
                session.regenerate() # NO SESSION FIXATION FOR YOU
            except:
                pass
            session['username'] = username
            session['nonce'] = hashlib.sha512(os.urandom(10)).hexdigest()
            db.session.close()

            logger = logging.getLogger('logins')
            logger.warn("[{0}] {1} logged in".format(time.strftime("%m/%d/%Y %X"), session['username'].encode('utf-8')))

            return redirect('/home')
        else:
            errors.append("That account doesn't seem to exist")
            db.session.close()
            return render_template('login.html', errors=errors)
    else:
        db.session.close()
        return render_template('login.html')
