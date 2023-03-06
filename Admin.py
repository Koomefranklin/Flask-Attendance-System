from flask import Flask, request, redirect, url_for, flash, render_template, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import extract, or_
from passlib.hash import sha256_crypt
import datetime
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.secret_key = "MDFCS"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mdfcs.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = datetime.timedelta(minutes=5)

db = SQLAlchemy(app)


class Admins(db.Model):  # type: ignore
    adm_username = db.Column(db.String(10), primary_key=True)
    adm_name = db.Column(db.String(30))
    adm_email = db.Column(db.String(30))
    adm_password = db.Column(db.String(100))

    def __init__(self, adm_username, adm_name, adm_email, adm_password):
        self.adm_email = adm_email
        self.adm_username = adm_username
        self.adm_password = adm_password
        self.adm_name = adm_name


class Clerks(db.Model):
    clerk_id = db.Column(db.String(20), primary_key=True)
    clerk_fname = db.Column(db.String(20))
    clerk_sname = db.Column(db.String(20))
    clerk_email = db.Column(db.String(30), unique=True)
    clerk_address = db.Column(db.String(20))
    clerk_phone = db.Column(db.String(10), unique=True)

    def __init__(self, clerk_id, clerk_fname, clerk_sname, clerk_email, clerk_address, clerk_phone):
        self.clerk_id = clerk_id
        self.clerk_fname = clerk_fname
        self.clerk_sname = clerk_sname
        self.clerk_address = clerk_address
        self.clerk_email = clerk_email
        self.clerk_phone = clerk_phone


class ClerkPortal(db.Model):
    clerk_username = db.Column(db.String, primary_key=True)
    clerk_id = db.Column(db.String, db.ForeignKey('clerks.clerk_id'))
    clerk_password = db.Column(db.String)

    def __init__(self, clerk_username, clerk_id, clerk_password):
        self.clerk_username = clerk_username
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


class Attendance(db.Model):
    clerk_id_date = db.Column(db.String, primary_key=True)
    clerk_id = db.Column(db.String, db.ForeignKey('clerks.clerk_id'))
    date = db.Column(db.Date)
    time_in = db.Column(db.Time)
    time_out = db.Column(db.Time)
    total_time = db.Column(db.Float)

def logged_in():
    if "username" in session:
        name = session["username"]
        password = Admins.query.filter_by(adm_username=name).first().adm_password
        if password == session["password"]:
            status = logged_in
            return status
    else:
        return redirect(url_for("login"))

@app.route("/signup", methods=["POST", "GET"])
def adminregister():
    if request.method == "POST":
        name = request.form["name"].capitalize()
        username = request.form["username"].capitalize()
        mail = username.lower() + '@mdfcs.co'
        password = sha256_crypt.encrypt(request.form["password"])

        found_user = Admins.query.filter_by(adm_username=username).first()
        if found_user:
            flash("Username already taken")
            return render_template("adminsignup.html", title="Signup")
        else:
            usr = Admins(username, name, mail, password)
            db.session.add(usr)
            db.session.commit()

            flash("registration successful! login with credentials")
            flash(f'your email address is: {mail}')
            return redirect(url_for("login"))
    else:
        return render_template("adminsignup.html", title="Signup")


@app.route("/signin", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        try:
            session.permanent = True
            uname = request.form["username"].capitalize()
            password = request.form["password"]
            session["username"] = uname

            found_user = Admins.query.filter_by(adm_username=uname).first()
            user_password = found_user.adm_password

            if found_user and sha256_crypt.verify(password, user_password):

                session["password"] = user_password
                flash("login successful!")
                return redirect(url_for("home"))
            else:
                flash("Incorrect username Password combination")
                return render_template("adminsignin.html",title = "Signin")
        except Exception as e:
            flash("User not found ")
            return render_template("adminsignin.html",title = "Signin")
    else:
        if logged_in() == logged_in:
            flash("Already logged in")
            return redirect(url_for("home"))
        return render_template("adminsignin.html",title = "Signin")


@app.route("/adminhome")
def home():
    if logged_in() == logged_in:
        return render_template("home.html",title = "Home")
    else:
        return redirect(url_for('login'))


@app.errorhandler(404)
def page_not_found(error):
    # Redirect user to the home page
    return redirect(url_for('home'))


@app.route("/register", methods=["POST", "GET"])
def clerkregistration():
    if logged_in() == logged_in:
        def assignid():
            search = Clerks.query.count()  # check if table has items
            if search:
                getlast = Clerks.query.order_by(Clerks.clerk_id.desc()).first()  # get the last id on the table
                last_id = getlast.clerk_id
                idnumber = ''.join((filter(str.isdigit, last_id)))
                newid = f'{int(idnumber) + 1:03d}'  # int with 3 digits
                print(newid)
                return ('C' + str(newid))
            else:
                newid = f'{1:03d}'  # create with 3 places
                new_id = 'C' + str(newid)
                return new_id

        if request.method == "POST":
            clerk_id = assignid()
            fname = request.form["f-name"].capitalize()
            sname = request.form["s-name"].capitalize()
            address = request.form["address"].upper()
            email = clerk_id.lower() + '@mdfcs.co'
            uname = email
            phone = request.form["phone"]
            password = sha256_crypt.encrypt(phone)
            found_clerk = Clerks.query.filter_by(clerk_id=clerk_id).first()
            if found_clerk:
                return render_template("clerkregistration.html",title = "Registration")
            else:
                usr = Clerks(clerk_id, fname, sname, email, address, phone)
                clrk = ClerkPortal(uname, clerk_id, password)
                db.session.add(usr)
                db.session.add(clrk)
                db.session.commit()

                flash("registration successful!")
                flash(f"clerk id is: {clerk_id} and email is: {email}")
                return redirect(url_for("viewclerks"))

        else:
            return render_template("clerkregistration.html",title = "Registration")
    else:
        flash("You need to login first")
        return redirect(url_for("login"))


@app.route('/viewclerks', methods=["POST", "GET"])
def viewclerks():
    if logged_in() == logged_in:

        if request.method == 'POST':
            c_id = request.form["id"].capitalize()
            search = f'%{c_id}%'
            result = Clerks.query.filter(Clerks.clerk_id.like(search)).all()
            if result:
                return render_template("viewclerks.html",title = "Registered clerks", result=result)
            else:
                flash("Search Item Not Found")
                return render_template("viewclerks.html",title = "Registered clerks")
        else:
            result = Clerks.query.all()  # get all table elements
            return render_template("viewclerks.html",title = "Registered clerks", result=result)
    else:
        flash(f"You need to login first")
        return redirect(url_for("login"))


@app.route('/viewattendance', methods=["POST", "GET"])
def viewattendance():
    if logged_in() == logged_in:
        if request.method == 'POST':
            c_id = request.form["id"].capitalize()
            view = db.session.query(Clerks, Attendance).join(Attendance, Clerks.clerk_id == Attendance.clerk_id).filter(
                Clerks.clerk_id.like(f'%{c_id}%')).all()
            return render_template("ClerksAttendanceSummary.html", title = "Attendance summary", result=view)
        else:
            view = db.session.query(Clerks, Attendance).join(Attendance, Clerks.clerk_id == Attendance.clerk_id).all()
            # get all table elements
            return render_template("ClerksAttendanceSummary.html", title = "Attendance summary", result=view)
    else:
        flash("You need to login first")
        return redirect(url_for("login"))


@app.route("/delete", methods=["POST", "GET"])
def deleterecords():
    if logged_in() == logged_in:
        if request.method == "POST":
            c_id = request.form["id"].capitalize()
            clerkfound = Clerks.query.filter_by(clerk_id=c_id).first()
            if clerkfound:
                db.session.delete(clerkfound)
                db.session.commit()
                flash(f"Clerk {c_id} deleted from database")
                return redirect(url_for("viewclerks"))
            else:
                flash("Requested id not found")
                return render_template("delete_clerk.html",title = "Delete")
        else:
            return render_template("delete_clerk.html",title = "Delete")
    else:
        return redirect(url_for("login"))


@app.route("/signout")
def adminsignout():
    if logged_in() == logged_in:
        session.pop("username", None)
        return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))


@app.route("/genarate", methods=["POST", "GET"])
def Generate_Payroll():
    if request.method == "POST":
        month = request.form["month"]
        year = request.form["year"]
        month_year = f"{month}-{year}"
        Payrate = int(request.form["pay-rate"])
        clerk_attendance = Attendance.query.with_entities(Attendance.total_time, Attendance.clerk_id,
                                                          extract('month', Attendance.date).label('month'), extract('year', Attendance.date).label('year')).filter(
            extract('month', Attendance.date) == month, extract('year', Attendance.date) == year).all()

        clerk_hours = {}
        for attendance in clerk_attendance:
            clerk_id = attendance.clerk_id
            total_hours = attendance.total_time

            # Update the total hours worked for this clerk
            if clerk_id not in clerk_hours:
                clerk_hours[clerk_id] = 0

            clerk_hours[clerk_id] += total_hours if total_hours is not None else 0
        for clerk_id, worked_hours in clerk_hours.items():
            worked_hours = float(format(worked_hours, '.2f'))
            total_pay = worked_hours * Payrate
            clerk_id_month_year = f"{clerk_id}_{month_year}"
            payroll = Payroll(clerk_id_month_year,clerk_id,month_year,worked_hours,Payrate,total_pay)
            db.session.add(payroll)
        try:
            db.session.commit()
            flash(f"Payroll for the peiod {month_year} has been generated")
        except IntegrityError:
            flash("Already Generated")
        return render_template("CreatePayroll.html")
    else:
        return render_template("CreatePayroll.html")


@app.route("/payroll", methods=["POST", "GET"])
def payroll():
    if logged_in() == logged_in:
        if request.method == "POST":
            query_month = request.form["month"]
            query_id = request.form["id"]
            records = db.session.query(Clerks, Payroll).join(Payroll, Clerks.clerk_id == Payroll.clerk_id)\
                .filter(or_((Payroll.month_year == query_month), (Payroll.clerk_id.like(f"%{query_id}%")))).all()
            return render_template("payroll.html", title="Payroll", pay_roll=records)
        else:
            pay_roll = db.session.query(Clerks, Payroll).join(Payroll, Clerks.clerk_id == Payroll.clerk_id).order_by(
                Payroll.month_year.asc()).all()
            return render_template("payroll.html", title="Payroll", pay_roll=pay_roll)
    else:
        return redirect(url_for("login"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
