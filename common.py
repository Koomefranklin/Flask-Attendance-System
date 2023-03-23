from flask import Flask, request, redirect, url_for, flash, render_template, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import extract, or_, and_
from passlib.hash import sha256_crypt
import datetime
from sqlalchemy.exc import IntegrityError
import logging
from flask_mail import Mail, Message
import random
import string

app = Flask(__name__)
app.secret_key = "MDFCS"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mdfcs.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = datetime.timedelta(minutes=5)
logging.basicConfig(filename='app.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s: %(message)s')


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'escapistcyber@gmail.com'
app.config['MAIL_PASSWORD'] = 'gdxbwxhbenvvkkux'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

db = SQLAlchemy(app)


class Clerks(db.Model):
    clerk_id = db.Column(db.String(20), primary_key=True)
    clerk_fname = db.Column(db.String(20))
    clerk_sname = db.Column(db.String(20))
    email = db.Column(db.String(50), nullable=False)
    clerk_address = db.Column(db.String(20))
    clerk_phone = db.Column(db.String(10), unique=True)
    working = db.Column(db.Boolean)

    def __init__(self, clerk_id, clerk_fname, clerk_sname, email, clerk_address, clerk_phone, working):
        self.clerk_id = clerk_id
        self.clerk_fname = clerk_fname
        self.clerk_sname = clerk_sname
        self.email = email
        self.clerk_address = clerk_address
        self.clerk_phone = clerk_phone
        self.working = working


class Attendance(db.Model):
    clerk_id_date = db.Column(db.String, primary_key=True)
    clerk_id = db.Column(db.String, db.ForeignKey('clerks.clerk_id'))
    date = db.Column(db.Date)
    time_in = db.Column(db.Time)
    time_out = db.Column(db.Time)
    total_time = db.Column(db.Float)

    def __init__(self, clerk_id_date, clerk_id, date, time_in, time_out, total_time):
        self.clerk_id_date = clerk_id_date
        self.clerk_id = clerk_id
        self.date = date
        self.time_in = time_in
        self.time_out = time_out
        self.total_time = total_time


class ClerkPortal(db.Model):
    email = db.Column(db.String, db.ForeignKey('clerks.email'), primary_key=True)
    clerk_id = db.Column(db.String, db.ForeignKey('clerks.clerk_id'))
    clerk_password = db.Column(db.String)

    def __init__(self, email, clerk_id, clerk_password):
        self.email = email
        self.clerk_id = clerk_id
        self.clerk_password = clerk_password


class Payroll(db.Model):
    clerk_id_month_year = db.Column(db.String, primary_key=True)
    clerk_id = db.Column(db.String, db.ForeignKey('clerks.clerk_id'))
    month_year = db.Column(db.String)
    total_hours = db.Column(db.Float)
    pay_rate = db.Column(db.Float)
    total_pay = db.Column(db.Float)

    def __init__(self, clerk_id_month_year, clerk_id, month_year, total_hours, pay_rate, total_pay):
        self.clerk_id_month_year = clerk_id_month_year
        self.clerk_id = clerk_id
        self.month_year = month_year
        self.total_hours = total_hours
        self.pay_rate = pay_rate
        self.total_pay = total_pay


class ResetCodes(db.Model):
    user_email = db.Column(db.String, primary_key=True)
    reset_code = db.Column(db.Integer)
    request_time = db.Column(db.DateTime)

    def __init__(self, user_email, reset_code, request_time):
        self.user_email = user_email
        self.reset_code = reset_code
        self.request_time = request_time
