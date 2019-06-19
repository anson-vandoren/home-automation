from flask import abort, jsonify, render_template, request
from app import app
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
    return jsonify({"sensor_name": sensor_name}), 200
