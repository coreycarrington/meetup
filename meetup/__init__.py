from flask import Flask, render_template, request, redirect, abort, session, jsonify, json as json_mod, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
import logging, os, sqlalchemy, jinja2
from flask_oauth import OAuth

oauth = OAuth()          
twitter = oauth.remote_app('twitter',
base_url='https://api.twitter.com/1/',
request_token_url='https://api.twitter.com/oauth/request_token',
access_token_url='https://api.twitter.com/oauth/access_token',
authorize_url='https://api.twitter.com/oauth/authenticate',
consumer_key='7uazYUVD2EPYubYIg3oaD5kDh',
consumer_secret='BHefATbQuwCR76UXDO1fdxSn8CxOOcvARk2lWps4tR0QhzBIRm'
)

def format_datetime(date):
    return date.strftime("%Y-%m-%d %H:%M")

def create_app(username="", password=""):
    app = Flask("meetup", static_folder="../static", template_folder="../templates")
    app.jinja_env.filters['datetime'] = format_datetime
    with app.app_context():
        app.config.from_object('meetup.config')

        from meetup.models import db
        db.init_app(app)
        db.create_all()

        app.db = db

        Session(app)

        from meetup.views import views
        from meetup.auth import auth

        from meetup.errors import init_errors
        init_errors(app)

        app.register_blueprint(views)
        app.register_blueprint(auth)

        return app

