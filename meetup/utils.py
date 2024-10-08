from meetup.models import db

from urllib.parse import urllib.parse, urljoin
from functools import wraps
from flask import current_app as app, g, request, redirect, url_for, session

def init_utils(app):
    #app.jinja_env.globals.update()
    pass
