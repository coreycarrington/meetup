#!/bin/bash
sudo apt-get install py-bcrypt python-pip python-mysqldb mysql mysql-server 

sudo pip install flask-sqlalchemy flask-session passlib Flask-OAuth requests

mysql -u root -ptoor < setup.sql

