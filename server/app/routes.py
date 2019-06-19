from flask import abort, flash, jsonify, redirect, render_template, request, url_for
from app import app
from app.forms import LoginForm
from app.store import CSVStore


@app.route("/")
@app.route("/index")
def index():
    """
    show the main page
    """
    office_sensor = CSVStore.get_last_reading("office")
    return render_template("index.html", sensors=[office_sensor])


@app.route("/sensor/add_reading", methods=["POST"])
def update_from_sensor():
    if (
        not request.json
        or "sensor_name" not in request.json
        or "sensor_id" not in request.json
    ):
        abort(400)

    sensor_name = request.json["sensor_name"]
    sensor_id = request.json["sensor_id"]
    temp = request.json.get("temperature", None)
    humidity = request.json.get("humidity", None)

    CSVStore.add_sensor_reading(sensor_name, temp, humidity)

    sensor_name = request.json["sensor_name"]
    return jsonify({"status": "success"}), 200


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash(
            f"Login requested for user {form.username.data}, remember_me={form.remember_me.data}"
        )
        return redirect(url_for("index"))
    return render_template("login.html", title="Sign In", form=form)


@app.route("/raw_readings")
def raw_readings():
    all_readings = CSVStore.get_all()
    return render_template("raw_data.html", title="Raw Readings", rows=all_readings)
