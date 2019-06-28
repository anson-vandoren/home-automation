import datetime

import pytz
from flask import abort, flash, jsonify, redirect, render_template, request, url_for

from app import app
from app.forms import LoginForm
from app.store import CSVStore, SettingsStore


@app.route("/")
@app.route("/index")
def index():
    """
    show the main page
    """
    office_sensor = CSVStore.get_last_reading("office")
    bedroom_sensor = CSVStore.get_last_reading("bedroom")
    sensors = [office_sensor, bedroom_sensor]
    for sensor in sensors:
        utc_timestamp = pytz.utc.localize(
            datetime.datetime.strptime(sensor["timestamp"], app.config["TIME_FORMAT"])
        ).isoformat()
        sensor["timestamp"] = utc_timestamp

    return render_template("index.html", sensors=sensors)


@app.route("/sensor/add_reading", methods=["POST"])
def update_from_sensor():
    # TODO: add authentication
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


@app.route("/current_temp")
def get_current_temp():
    sensor_name = request.args.get("sensorName", None)
    current_temp = CSVStore.get_last_reading(sensor_name)

    if current_temp is None:
        return (
            jsonify(
                {
                    "status": "failed",
                    "message": f"Could not find current temperature for sensor {sensor_name}",
                }
            ),
            400,
        )

    timestamp = current_temp["timestamp"]
    utc_timestamp = pytz.utc.localize(
        datetime.datetime.strptime(timestamp, app.config["TIME_FORMAT"])
    ).isoformat()

    return (
        jsonify(
            {
                "location": current_temp["location"],
                "timestamp": utc_timestamp,
                "temperature": current_temp["temperature"],
                "humidity": current_temp["humidity"],
            }
        ),
        200,
    )


@app.route("/temp_setpoint", methods=["GET", "POST"])
def temp_setpoint():
    if request.method == "GET":
        current_setpoint = SettingsStore.temp_setpoint()
        return jsonify({"setpoint": current_setpoint}), 200
    elif request.method == "POST":
        new_setpoint = request.json.get("newSetpoint", None)
        if new_setpoint is None:
            return (
                jsonify(
                    {"status": "failed", "message": "must include newSetpoint for POST"}
                ),
                400,
            )

        result = SettingsStore.temp_setpoint(new_setpoint)
        if result is None:
            return (
                jsonify(
                    {
                        "status": "failed",
                        "message": f"could not change setpoint to {new_setpoint}",
                    }
                ),
                400,
            )

        if result != int(new_setpoint):
            return (
                jsonify(
                    {
                        "status": "modified",
                        "message": f"requested setpoint ({new_setpoint}) out of bounds. used {result} as setpoint instead",
                        "setpoint": result,
                    }
                ),
                200,
            )

        return (
            jsonify(
                {
                    "status": "success",
                    "message": "successfully changed temperature setpoint",
                    "setpoint": result,
                }
            ),
            200,
        )
