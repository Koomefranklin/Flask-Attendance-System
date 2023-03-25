# Attendance System by Koome Franklin (Mburus)
# https://www.koomefranklin.github.io
from common import *


@app.route("/checkin", methods=["POST", "GET"])
def checkin():
    if request.method == "POST":
        c_id = request.form["id"].capitalize()
        date = datetime.date.today()
        id_date = c_id + "_" + str(date)
        time_in = datetime.datetime.now().time()

        verify_clerk = Clerks.query.filter(and_((Clerks.clerk_id == c_id), (Clerks.working == True))).first()
        if verify_clerk:
            clerk = Attendance(id_date, c_id, date, time_in, None, None)
            try:
                db.session.add(clerk)
                db.session.commit()
                flash(f"Check in at {time_in.strftime('%H:%M:%S')} successful")
                return redirect(url_for("checkin"))
            except IntegrityError:
                flash('Already checked in')
                return redirect(url_for("checkin"))
        else:
            flash("Clerk Id not found")
            return render_template("checkin.html", title="Checkin")
    else:
        return render_template("checkin.html", title="Checkin")


@app.route("/checkout", methods=["POST", "GET"])
def checkout():
    if request.method == "POST":
        c_id = request.form["id"].capitalize()
        date = datetime.date.today()
        id_date = c_id + "_" + str(date)
        clerk_details = Attendance.query.filter(Attendance.clerk_id_date == id_date).first()
        recorded_time_in = clerk_details.time_in
        time_out = datetime.datetime.now().time()
        converted_time_in = datetime.datetime.combine(datetime.datetime.today(), recorded_time_in)
        converted_time_out = datetime.datetime.combine(datetime.datetime.today(), time_out)
        total_time = float(format((converted_time_out - converted_time_in).total_seconds() / 3600, ".2f"))
        if clerk_details.time_out is None and clerk_details.total_time is None:
            clerk_details.time_out = time_out
            clerk_details.total_time = total_time
            db.session.commit()
            flash(f"Check out at {time_out.strftime('%H:%M:%S')} successful\nTotal time: {total_time}")
            return redirect(url_for("checkout"))
        else:
            flash(
                f"Clerk {clerk_details.clerk_id} already checked out at {clerk_details.time_out.strftime('%H:%M:%S')}")
            return render_template("checkout.html", title="Checkout")
    else:
        return render_template('checkout.html')


@app.errorhandler(404)
def page_not_found(error):
    # Redirect user to the page for filling attendance
    return redirect(url_for('checkin'))


with app.app_context():
    db.create_all()
if __name__ == "__main__":
    app.run(debug=True, port=5001)
