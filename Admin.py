#!/usr/bin/venv python
# Attendance System by Koome Franklin (Mburus)
# https://www.koomefranklin.github.io
# Get the common configuration like app setup and database tables
from common import *


# Table used only by the admin site
class Admins(db.Model):  # type: ignore
    adm_username = db.Column(db.String(10), primary_key=True)
    adm_name = db.Column(db.String(30))
    adm_password = db.Column(db.String(100))
    email = db.Column(db.String(50), nullable=False)

    def __init__(self, adm_username, adm_name, adm_password, email):
        self.adm_username = adm_username
        self.adm_password = adm_password
        self.adm_name = adm_name
        self.email = email


# Function to check if  there is a logged in user
# Get the username and password from the session and verify from the database
# if the session is empty then no logged in usser
# If the username and password in the session are different then return false
def logged_in():
    if "username" in session:
        name = session["username"]
        password = Admins.query.filter_by(adm_username=name).first().adm_password
        if password == session["password"]:
            return True
    else:
        return False


# Function to get the name of the current user
def logged_user():
    username = session["username"]
    name = Admins.query.filter(Admins.adm_username == username).first().adm_name
    return name

@app.route("/reset-password", methods=["GET","POST"])
def reset_password():
    # reset forgoten password
    if request.method == "POST":
        try:
            # Using the try except blocks to catch errors at runtime
            # Get the inputs and verify the excistence from db
            email = request.form["email"].lower()
            input_code = request.form["code"]
            user = Admins.query.filter(Admins.email == email).first()
            if len(input_code) == 0:
                password_string = ''
                for i in range(6):
                    password_string += str(random.randint(0,9))
                code = int(password_string) # Randomly generated code for password reset
                msg = Message(f'Hello {user.adm_name}', sender=sending_email, recipients=[user.email])
                msg.body = f"Request for password reset.\nEnter the code below to reset your password for the MDFCS Admin Account.\n{code}\nThe code is valid for 15 minutes."
                mail.send(msg) # Send code via email
                request_time = datetime.datetime.now()
                reset_details = ResetCodes(email, code, request_time) # Add the code, email and time to a database table
                db.session.add(reset_details)
                db.session.commit()
                flash(f"Reset code sent to {user.email} and is valid for 15 minutes")
                return render_template('reset_password.html', title="Password Reset", code_hidden="false", button="Submit", email=email)
            else:
                try:
                    # Verify that the user and code match
                    user_code = ResetCodes.query.filter(
                        and_(ResetCodes.user_email == email, ResetCodes.reset_code == input_code)).first()
                    code_sent_time = user_code.request_time
                    elapsed_time = (datetime.datetime.now() - code_sent_time).total_seconds() / 60
                    if elapsed_time > 15: # Verify that the code is not timed out (15 minutes)
                        db.session.delete(user_code) # Remove the code from db
                        db.session.commit()
                        flash("Code timed out Please request another code")
                        return redirect(url_for('reset_password'))
                    else:
                        db.session.delete(user_code)
                        db.session.commit()
                        flash("Reset password")
                        return redirect(url_for('new_password', email=email))
                except AttributeError: # Code is incorect
                    flash("Wrong code. Request a new one")
                    return redirect(url_for('reset_password'))
        except IntegrityError: # Trying to request code twice
            flash("Code already sent")
            return render_template('reset_password.html', title="Password Reset", code_hidden="false", button="Submit", email=email)
        except AttributeError: # unregistered email
            flash("User not found")
            return redirect(url_for('reset_password'))
        except Exception: # any other error mostly a connection tiemout in sending the mail
            flash(f"Email not sent. Check your internet connection and try again")
            return redirect(url_for('reset_password'))
    else:
        return render_template("reset_password.html", title="Password Reset", button="Get Code", code_hidden="true")


@app.route("/new-password", methods=["POST", "GET"])
def new_password():
    # Set a new password after entering correct password
    if request.method == "POST":
        try:
            email = request.args.get('email')
            password = request.form['password']
            user = Admins.query.filter(Admins.email == email).first()
            hashed_password = sha256_crypt.hash(password)
            user.adm_password = hashed_password
            db.session.commit()
            msg = Message(f'Hello {user.adm_name}', sender=sending_email,
                          recipients=[user.email])
            msg.body = f"You have successfully reset your password"
            mail.send(msg)
            flash("Password reset successfully")
            return redirect(url_for('login'))
        except Exception:
            flash("User did not request reset code")
            return redirect(url_for('reset_password'))
    else:
        return render_template('newPassword.html', title="New Password")


@app.route("/signup", methods=["POST", "GET"])
def adminregister():
    if request.method == "POST":
        name = request.form["name"].capitalize()
        username = request.form["username"].capitalize()
        password = sha256_crypt.hash(request.form["password"])
        email = request.form["email"].lower()

        found_user = Admins.query.filter_by(adm_username=username).first()
        if found_user:
            flash("Username already taken")
            return render_template("adminsignup.html", title="Signup")
        else:
            usr = Admins(username, name, password, email)
            db.session.add(usr)
            db.session.commit()

            flash("registration successful! login with credentials")
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
            flash(f"User not found {e}")
            return render_template("adminsignin.html",title = "Signin")
    else:
        if logged_in():
            flash("Already logged in")
            return redirect(url_for("home"))
        return render_template("adminsignin.html",title = "Signin")


@app.route("/adminhome")
def home():
    if logged_in():
        return render_template("home.html",title="Home",username=logged_user())
    else:
        return redirect(url_for('login'))


@app.errorhandler(404)
def page_not_found(error):
    # Redirect user to the home page
    return redirect(url_for('home'))


@app.route("/register", methods=["POST", "GET"])
def clerkregistration():
    if logged_in():
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
            clerk_email = request.form["email"].lower()
            uname = clerk_email
            phone = request.form["phone"]
            password = sha256_crypt.hash(phone)
            found_clerk = Clerks.query.filter_by(clerk_id=clerk_id).first()
            if found_clerk:
                return render_template("clerkregistration.html",title = "Registration", username=logged_user())
            else:
                usr = Clerks(clerk_id, fname, sname, clerk_email, address, phone, True)
                clrk = ClerkPortal(uname, clerk_id, password)
                db.session.add(usr)
                db.session.add(clrk)
                db.session.commit()
                try:
                    msg = Message(f'Hello {sname}', sender=sending_email, recipients=[clerk_email])
                    msg.body = f"Registration as a Mdfcs clerk successful.\nYour ID is {clerk_id} and will be used generally everywhere.\nFor the web portal, use tour email {clerk_email} and your password which is your phone number\nOnce you enter the details you will be prompted to change your password.\n\nWelcome."
                    mail.send(msg)
                finally:
                    flash(f"Registration of {clerk_id} successful!")
                    return redirect(url_for("viewclerks"))

        else:
            return render_template("clerkregistration.html",title = "Registration", username=logged_user())
    else:
        flash("You need to login first")
        return redirect(url_for("login"))


@app.route('/viewclerks', methods=["POST", "GET"])
def viewclerks():
    if logged_in():

        if request.method == 'POST':
            c_id = request.form["id"].capitalize()
            search = f'%{c_id}%'
            result = Clerks.query.filter(and_((Clerks.clerk_id.like(search)), (Clerks.working == True))).all()
            if result:
                return render_template("viewclerks.html",title = "Registered clerks", result=result, username=logged_user())
            else:
                flash("Search Item Not Found")
                return render_template("viewclerks.html",title = "Registered clerks", username=logged_user())
        else:
            result = Clerks.query.filter(Clerks.working == True).all()  # get all table elements
            return render_template("viewclerks.html",title = "Registered clerks", result=result, username=logged_user())
    else:
        flash(f"You need to login first")
        return redirect(url_for("login"))


@app.route('/viewattendance', methods=["POST", "GET"])
def viewattendance():
    if logged_in():
        if request.method == 'POST':
            c_id = request.form["id"].capitalize()
            view = db.session.query(Clerks, Attendance).join(Attendance, Clerks.clerk_id == Attendance.clerk_id).filter(
                and_((Clerks.clerk_id.like(f'%{c_id}%')), (Clerks.working == True))).all()
            return render_template("ClerksAttendanceSummary.html", title = "Attendance summary", result=view, username=logged_user())
        else:
            view = db.session.query(Clerks, Attendance).join(Attendance, Clerks.clerk_id == Attendance.clerk_id).filter(Clerks.working == True).all()
            # get all table elements
            return render_template("ClerksAttendanceSummary.html", title = "Attendance summary", result=view, username=logged_user())
    else:
        flash("You need to login first")
        return redirect(url_for("login"))


@app.route("/delete", methods=["POST", "GET"])
def deleterecords():
    if logged_in():
        all_clerks = Clerks.query.filter(Clerks.working == True).all()
        if request.method == "POST":
            c_id = request.form["id"].capitalize()
            clerkfound = Clerks.query.filter(and_(Clerks.clerk_id.like(f'%{c_id}%' )), (Clerks.working == True)).all()
            if clerkfound:
                return render_template("delete_clerk.html", title = "Delete", result=clerkfound, username=logged_user())
            else:
                flash("Requested id not found")
                return render_template("delete_clerk.html", title = "Delete", result=all_clerks, username=logged_user())
        else:
            return render_template("delete_clerk.html", title = "Delete", result=all_clerks, username=logged_user())
    else:
        return redirect(url_for("login"))


@app.route("/deactivate", methods=["POST"])
def deactivaterecords():
    if logged_in():
        data = request.get_json()
        c_id = data['value']
        clerk = Clerks.query.filter_by(clerk_id=c_id).first()
        if clerk.working is True:
            clerk.working = False
            action = "Deactivated"
        else:
            clerk.working = True
            action = "Reactivated"
        db.session.commit()
        msg = Message(f'Hello {clerk.clerk_sname}', sender=sending_email, recipients=[clerk.email])
        msg.body = f"You have been {action}"
        mail.send(msg)
        return f"Clerk {clerk.clerk_id} {action}"
    else:
        return "Timed Out Login First!"


@app.route("/deactivated", methods=["POST", "GET"])
def deactivated():
    if logged_in():
        all_clerks = Clerks.query.filter(Clerks.working == False).all()
        if request.method == "POST":
            c_id = request.form["id"].capitalize()
            clerkfound = Clerks.query.filter(and_(Clerks.clerk_id.like(f'%{c_id}%')), (Clerks.working == False)).all()
            if clerkfound:
                return render_template("deactivated.html", title="Inactive", result=clerkfound, username=logged_user())
            else:
                flash("Requested id not found")
                return render_template("deactivated.html", title="Inactive", result=all_clerks, username=logged_user())
        else:
            return render_template("deactivated.html", title="Inactive", result=all_clerks, username=logged_user())
    else:
        return redirect(url_for("login"))


@app.route("/payroll", methods=["POST", "GET"])
def payroll():
    if logged_in():
        if request.method == "POST":
            query_month = request.form["month"]
            query_id = request.form["id"]
            records = db.session.query(Clerks, Payroll).join(Payroll, Clerks.clerk_id == Payroll.clerk_id)\
                .filter(or_((Payroll.month_year.like(f"{query_month}%")), (Payroll.clerk_id.like(f"%{query_id}%")))).all()
            return render_template("payroll.html", title="Payroll", pay_roll=records, username=logged_user())
        else:
            pay_roll = db.session.query(Clerks, Payroll).join(Payroll, Clerks.clerk_id == Payroll.clerk_id).order_by(
                Payroll.month_year.asc()).all()
            return render_template("payroll.html", title="Payroll", pay_roll=pay_roll, username=logged_user())
    else:
        return redirect(url_for("login"))


@app.route("/genarate", methods=["POST", "GET"])
def Generate_Payroll():
    if logged_in():
        if request.method == "POST":
            month = request.form["month"]
            year = request.form["year"]
            month_year = f"{month}-{year}"
            Payrate = int(request.form["pay-rate"])
            try:
                clerk_attendance = Attendance.query.filter(extract('month', Attendance.date) == month, extract('year', Attendance.date) == year).all()
                if len(clerk_attendance) > 0:
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
                        total_pay = float(format(worked_hours * Payrate, '.2f'))
                        clerk_id_month_year = f"{clerk_id}_{month_year}"
                        payroll = Payroll(clerk_id_month_year,clerk_id,month_year,worked_hours,Payrate,total_pay)

                        db.session.add(payroll)
                    emails = []
                    records = Clerks.query.all()
                    for record in records:
                        emails.append(record.email)
                    msg = Message(f'Hello, ', sender=sending_email, recipients=emails)
                    msg.body = f"Payroll for the period {month_year} has been generated.\ncheck your portal for details."
                    mail.send(msg)
                    db.session.commit()
                    flash(f"Payroll for the peiod {month_year} has been generated")
                else:
                    flash(f"No records found for the period {month_year}")
            except IntegrityError:
                flash("Already Generated")
            return render_template("CreatePayroll.html")
        else:
            return render_template("CreatePayroll.html")
    else:
        return redirect(url_for('login'))


@app.route("/signout")
def signout():
    if logged_in():
        session.pop("username", None)
        session.pop("password", None)
        return redirect(url_for("login"))
    else:
        return redirect(url_for("login"))



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
