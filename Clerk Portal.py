#!/usr/bin/venv python

from common import *


def signed_in():
    if "email" in session:
        email = session["email"]
        user_password = ClerkPortal.query.filter(ClerkPortal.email == email).first().clerk_password
        if user_password == session["clerk_password"]:
            return True
    else:
        return False


def logged_user():
    email = session["email"]
    user = Clerks.query.filter_by(email=email).first()
    sir_name = user.clerk_sname
    first_name = user.clerk_fname
    name = f"{sir_name} {first_name}"
    return name


@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        try:
            email = request.form["email"].lower()
            input_code = request.form["code"]
            user = Clerks.query.filter(Clerks.email == email).first()
            if len(input_code) == 0:
                password_string = ''
                for i in range(6):
                    password_string += str(random.randint(0, 9))
                code = int(password_string)
                msg = Message(f'Hello {user.clerk_sname}', sender=sending_email, recipients=[user.email])
                msg.body = f"Request for password reset.\nEnter the code below to reset your password for the MDFCS " \
                           f"Admin Account.\n{code}\nThe code is valid for 15 minutes."
                mail.send(msg)
                request_time = datetime.datetime.now()
                reset_details = ResetCodes(email, code, request_time)
                db.session.add(reset_details)
                db.session.commit()
                flash(f"Reset code sent to {email} and is valid for 15 minutes")
                return render_template('reset_password.html', title="Password Reset", code_hidden="false",
                                       button="Submit", email=email)
            else:
                try:
                    user_code = ResetCodes.query.filter(
                        and_(ResetCodes.user_email == email, ResetCodes.reset_code == input_code)).first()
                    code_sent_time = user_code.request_time
                    elapsed_time = (datetime.datetime.now() - code_sent_time).total_seconds() / 60
                    if elapsed_time > 15:
                        db.session.delete(user_code)
                        db.session.commit()
                        flash("Code timed out Please request another code")
                        return redirect(url_for('reset_password'))
                    else:
                        db.session.delete(user_code)
                        db.session.commit()
                        flash("Reset password")
                        return redirect(url_for('new_password', email=email))
                except AttributeError:
                    flash("Wrong code. Request a new one")
                    return redirect(url_for('reset_password'))

        except IntegrityError:
            flash("Code already sent")
            return render_template('reset_password.html', title="Password Reset", code_hidden="false", button="Submit")
        except AttributeError:
            flash("User not found")
            return redirect(url_for('reset_password'))
        except Exception:
            flash(f"Email not sent. Check your internet connection and try again")
            return redirect(url_for('reset_password'))
    else:
        return render_template("reset_password.html", title="Password Reset", button="Get Code", code_hidden="true")


@app.route("/new-password", methods=["POST", "GET"])
def new_password():
    if request.method == "POST":
        try:
            email = request.args.get('email')
            password = request.form['password']
            user = ClerkPortal.query.filter(ClerkPortal.email == email).first()
            name = Clerks.query.filter_by(email=email).first().clerk_sname
            hashed_password = sha256_crypt.hash(password)
            user.clerk_password = hashed_password
            db.session.commit()
            msg = Message(f'Hello {name}', sender=sending_email,
                          recipients=[user.email])
            msg.body = f"You have successfully reset your password"
            # mail.send(msg)
            flash("Password reset successfully")
            return redirect(url_for('clerk_signin'))
        except NameError:
            flash("User did not request reset code")
            return redirect(url_for('reset_password'))
    else:
        return render_template('newPassword.html', title="New Password")


@app.route("/home")
def home():
    if signed_in():
        email = session["email"]
        records = Clerks.query.filter_by(email=email).first()
        return render_template("webhome.html", records=records, title="Home", user=logged_user())
    else:
        return redirect(url_for("clerk_signin"))


@app.route("/clerksignin", methods=["POST", "GET"])
def clerk_signin():
    if signed_in():
        return redirect(url_for("home"))
    else:
        if request.method == "POST":
            try:
                session.permanent = True
                email = request.form["email"].lower()
                password = request.form["password"]
                found_user = ClerkPortal.query.filter_by(email=email).first()
                active_clerk = Clerks.query.filter(Clerks.clerk_id == found_user.clerk_id).first()
                try:
                    if active_clerk.working is True:
                        session["email"] = email
                        clerk_password = found_user.clerk_password
                        session["clerk_password"] = clerk_password
                        if found_user and sha256_crypt.verify(password, clerk_password):
                            if password == Clerks.query.filter_by(clerk_id=found_user.clerk_id).first().clerk_phone:
                                flash("Proceed to change password")
                                return redirect(url_for("change_password"))
                            else:
                                flash("login successful!")
                                return redirect(url_for("home"))
                        else:
                            flash("Incorrect Username Password combination")
                            return render_template("clerk_signin.html", title="Sign In")
                    else:
                        flash("Clerk was Deactivated!")
                        return render_template("clerk_signin.html", title="Sign In")
                except AttributeError:
                    flash("User Not Found!")
                    return render_template("clerk_signin.html", title="Sign In")
            except (ValueError, AttributeError):
                flash(f"User not found")
                return render_template("clerk_signin.html", title="Sign In")
        else:
            return render_template("clerk_signin.html", title="Sign In")


@app.route("/attendancesummary")
def attendancesummary():
    if signed_in():
        email = session["email"]
        c_id = ClerkPortal.query.filter_by(email=email).first().clerk_id
        summary = Attendance.query.filter_by(clerk_id=c_id).all()
        return render_template("summary.html", summary=summary, id=c_id, user=logged_user())
    else:
        return redirect(url_for("clerk_signin"))


@app.route("/payment")
def payinfo():
    if signed_in():
        c_id = ClerkPortal.query.filter_by(email=session["email"]).first().clerk_id
        result = Payroll.query.filter_by(clerk_id=c_id).all()
        return render_template("payment.html", result=result, id=c_id, user=logged_user())
    else:
        return redirect(url_for("clerk_signin"))


@app.route("/changePassword", methods=["POST", "GET"])
def change_password():
    if signed_in():
        email = session["email"]
        if request.method == "POST":
            old_password = request.form["old-password"]
            password = request.form["password"]
            confirm = request.form["confirm-password"]
            try:
                check_user = ClerkPortal.query.filter_by(email=email).first()
                verify_password = sha256_crypt.verify(old_password, check_user.clerk_password)
                if verify_password:
                    if password == confirm:
                        check_user.clerk_password = sha256_crypt.hash(password)
                        db.session.commit()
                        name = Clerks.query.filter_by(email=email).first().clerk_sname
                        msg = Message(f'Hello {name}.', sender=sending_email, recipients=[email])
                        msg.body = f"Password change successful\nProceed to login using your new password to access " \
                                   f"the portal\n\nWelcome"
                        mail.send(msg)
                        flash("Password Changed Successfully")
                        return redirect(url_for("signout"))
                    else:
                        flash("New Passwords don't match")
                        return render_template("ChangePassword.html", username=email, user=logged_user())
                else:
                    flash("Incorect old password")
                    return render_template("ChangePassword.html", username=email, user=logged_user())
            except Exception:
                flash("Password Unchanged")
                return render_template("ChangePassword.html", title="Change Password", user=logged_user())
        else:
            return render_template("ChangePassword.html", title="Change Password", username=email,
                                   user=logged_user())
    else:
        return redirect(url_for("clerk_signin"))


@app.errorhandler(404)
def page_not_found(error):
    # Redirect user to the home page
    return redirect(url_for('home'))


@app.route("/signout")
def signout():
    if signed_in():
        session.pop("email", None)
        session.pop("clerk_password", None)
        return redirect(url_for("clerk_signin"))
    else:
        return redirect(url_for("clerk_signin"))


with app.app_context():
    db.create_all()
if __name__ == "__main__":
    app.run(debug=True, port=5002)
