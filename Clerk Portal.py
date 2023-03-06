from flask import Flask, request, redirect, url_for, flash, render_template, session
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
import datetime
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


class ClerkPortal(db.Model):
    clerk_username = db.Column(db.String, primary_key=True)
    clerk_id = db.Column(db.String, db.ForeignKey('clerks.clerk_id'))
    clerk_password = db.Column(db.String)


class Clerks(db.Model):
    clerk_id = db.Column(db.String(20), primary_key=True)
    clerk_fname = db.Column(db.String(20))
    clerk_sname = db.Column(db.String(20))
    clerk_email = db.Column(db.String(30), unique=True)
    clerk_address = db.Column(db.String(20))
    clerk_phone = db.Column(db.String(10), unique=True)


class Payroll(db.Model):
    clerk_id_month_year = db.Column(db.String, primary_key=True)
    clerk_id = db.Column(db.String, db.ForeignKey('clerks.clerk_id'))
    month_year = db.Column(db.String)
    total_hours = db.Column(db.Float)
    pay_rate = db.Column(db.Float)
    total_pay = db.Column(db.Float)


@app.route("/home")
def home():
    if "clerkusername" in session:
        clerkusername = session["clerkusername"]
        c_id = ClerkPortal.query.filter_by(clerk_username=clerkusername).first().clerk_id
        records = Clerks.query.filter_by(clerk_id=c_id).first()
        return render_template("webhome.html", records=records, title="Home")
    else:
        return redirect(url_for("clerk_signin"))


@app.route("/clerksignin", methods=["POST", "GET"])
def clerk_signin():
    if request.method == "POST":
        try:
            session.permanent = True
            clerkusername = request.form["clerk-username"].lower()
            password = request.form["password"]

            found_user = ClerkPortal.query.filter_by(clerk_username=clerkusername).first()

            clerk_password = found_user.clerk_password
            if found_user and sha256_crypt.verify(password, clerk_password):
                if password == Clerks.query.filter_by(clerk_id=found_user.clerk_id).first().clerk_phone:
                    flash("Proceed to change password")
                    return redirect(url_for("changePassword"))
                else:
                    session["clerkusername"] = clerkusername
                    session["password"] = password
                    flash("login successful!")
                    return redirect(url_for("home"))
            else:
                flash("Incorrect Username Password combination")
                return render_template("clerk_signin.html", title="Sign In")
        except:
            flash(f"User not found")
            return render_template("clerk_signin.html", title="Sign In")
    else:
        if "clerkusername" in session:
            flash("Already logged in")
            return redirect(url_for("home"))
        else:
            return render_template("clerk_signin.html")


@app.route("/attendancesummary")
def attendancesummary():
    if "clerkusername" in session:
        clerkusername = session["clerkusername"]
        c_id = ClerkPortal.query.filter_by(clerk_username=clerkusername).first().clerk_id
        summary = Attendance.query.filter_by(clerk_id=c_id).all()
        return render_template("summary.html", summary=summary, id=c_id)
    else:
        return redirect(url_for("clerk_signin"))


@app.route("/payment")
def payinfo():
    if "clerkusername" in session:
        c_id = ClerkPortal.query.filter_by(clerk_username=session["clerkusername"]).first().clerk_id
        result = Payroll.query.filter_by(clerk_id=c_id).all()
        return render_template("payment.html", result=result, id=c_id)
    else:
        return redirect(url_for("clerk_signin"))


@app.route("/changePassword", methods=["POST", "GET"])
def changePassword():
    if "clerkusername" in session:
        clerkusername = session["clerkusername"]
        if request.method == "POST":
            old_password = request.form["old-password"]
            new_password = request.form["new-password"]
            confirm = request.form["confirm-password"]
            try:
                check_user = ClerkPortal.query.filter_by(clerk_username=clerkusername).first()
                verify_password = sha256_crypt.verify(old_password, check_user.clerk_password)
                if verify_password:
                    if new_password == confirm:
                        check_user.clerk_password = sha256_crypt.encrypt(new_password)
                        db.session.commit()
                        flash("Password Changed Successfully Proceed to login")
                        return redirect(url_for("signout"))
                    else:
                        flash("New Passwords don't match")
                        return rendfit-contenter_template("ChangePassword.html", username=clerkusername)
                else:
                    flash("Incorect old password")
                    return render_template("ChangePassword.html", username=clerkusername)
            except:
                flash("Password Unchanged")
                return render_template("ChangePassword.html")
        else:
            return render_template("ChangePassword.html", title="Change Password", username=clerkusername)
    else:
       return redirect(url_for("clerk_signin"))


@app.errorhandler(404)
def page_not_found(error):
    # Redirect user to the home page
    return redirect(url_for('home'))


@app.route("/signout")
def signout():
    if "clerkusername" in session:
        session.pop("clerkusername", None)
        return redirect(url_for("clerk_signin"))
    else:
        return redirect(url_for("clerk_signin"))


with app.app_context():
    db.create_all()
if __name__ == "__main__":
    app.run(debug=True, port=5002)
