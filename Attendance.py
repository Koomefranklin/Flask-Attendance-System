from flask import Flask, request, redirect, url_for, flash, render_template
from flask_sqlalchemy import SQLAlchemy
import datetime
import time
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.secret_key = "MDFCS"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mdfcs.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = datetime.timedelta(minutes=5)

db = SQLAlchemy(app)


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


class Clerks(db.Model):
    clerk_id = db.Column(db.String(20), primary_key=True)
    clerk_fname = db.Column(db.String(20))
    clerk_sname = db.Column(db.String(20))
    clerk_email = db.Column(db.String(30), unique=True)
    clerk_address = db.Column(db.String(20))
    clerk_phone = db.Column(db.String(10), unique=True)


@app.route("/checkin", methods=["POST", "GET"])
def checkin():
    if request.method == "POST":
        c_id = request.form["id"].capitalize()
        date = datetime.date.today()
        id_date = c_id + "_" + str(date)
        time_in = datetime.datetime.now().time()

        verifyclerk = Clerks.query.filter_by(clerk_id=c_id).first()
        if verifyclerk:
            clerk = Attendance(id_date, c_id, date, time_in, None, None)
            db.session.add(clerk)
            try:
                db.session.commit()
                flash(f"Check in at {time_in.strftime('%H:%M:S')} successful")
                return redirect(url_for("checkin"))
            except IntegrityError:
                flash("Already checked in")
                return render_template("Attendance.html", title="Check In")
        else:
            flash("Clerk Id not found")
            return render_template("Attendance.html", title="Check In")
    else:
        return render_template("Attendance.html", title="Check In")


@app.route("/checkout", methods=["POST", "GET"])
def checkout():
    if request.method == "POST":
        c_id = request.form["id"].capitalize()
        date = datetime.date.today()
        id_date = c_id + "_" + str(date)
        try:
            verifyclerk = Attendance.query.filter_by(clerk_id_date=id_date).first()
            time_in = verifyclerk.time_in
        except AttributeError:
            flash("User did not check in")
            return render_template("Attendance.html", title="Check Out")
        time_out = datetime.datetime.now().time()
        convertedtimein = datetime.datetime.combine(datetime.datetime.today(), time_in)
        convertedtimeout = datetime.datetime.combine(datetime.datetime.today(), time_out)
        total_time = float(format((convertedtimeout - convertedtimein).total_seconds() / 3600, ".2f"))
        if verifyclerk.time_out is None and verifyclerk.total_time is None:
            verifyclerk.time_out = time_out
            verifyclerk.total_time = total_time
            db.session.commit()
            flash(f"Check out at {time_out.strftime('%H:%M:S')} successfull\nTotal time: {total_time}")
            return redirect(url_for("checkin"))
        else:
            flash(f"Clerk {verifyclerk.clerk_id} already checked out at {verifyclerk.time_out}")
            return render_template("Attendance.html", title="Check Out")
    else:
        return render_template("Attendance.html", title="Check Out")


@app.errorhandler(404)
def page_not_found(error):
    # Redirect user to the checkin page
    return redirect(url_for('checkin'))


with app.app_context():
    db.create_all()
if __name__ == "__main__":
    app.run(debug=True, port=5001)
