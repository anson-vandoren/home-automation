import csv
import datetime
import json
import os

from app import app

CSV_FILE = "./readings.csv"
SETTINGS_FILE = "./settings.json"


class SettingsStore:
    filename = SETTINGS_FILE
    DEFAULT_STORE = {"setpoint": 72}

    @classmethod
    def temp_setpoint(cls, new_setpoint=None):
        if not os.path.exists(cls.filename):
            cls.create_default_store()

        with open(cls.filename, "r") as json_file:
            settings = json.load(json_file)

        if new_setpoint is None:
            # return current setpoint
            return settings.get("setpoint", cls.DEFAULT_STORE["setpoint"])
        else:
            try:
                new_setpoint = int(new_setpoint)
            except ValueError:
                return None

            # validate/clamp setpoint
            new_setpoint = max(
                app.config["SETPOINT_MIN"],
                min(app.config["SETPOINT_MAX"], new_setpoint),
            )

            settings["setpoint"] = new_setpoint
            with open(cls.filename, "w") as json_file:
                json.dump(settings, json_file)

            return new_setpoint

    @classmethod
    def create_default_store(cls):
        with open(cls.filename, "w") as json_file:
            json.dump(cls.DEFAULT_STORE, json_file)


class CSVStore:
    filename = CSV_FILE

    @classmethod
    def add_sensor_reading(cls, sensor_name, temperature, humidity):
        with open(cls.filename, "a") as csv_file:
            writer = csv.writer(csv_file, delimiter=",")
            timestamp = datetime.datetime.utcnow().strftime(app.config["TIME_FORMAT"])
            writer.writerow([timestamp, sensor_name, temperature, humidity])

    @classmethod
    def get_last_reading(cls, desired_sensor_name):
        if not os.path.exists(cls.filename):
            return None
        with open(cls.filename, "r") as csv_file:
            for row in reversed(csv_file.readlines()):
                timestamp, sensor_name, temperature, humidity = [
                    tag.strip() for tag in row.split(",")
                ]
                if sensor_name == desired_sensor_name or desired_sensor_name is None:
                    return {
                        "location": sensor_name,
                        "timestamp": timestamp,
                        "temperature": temperature,
                        "humidity": humidity,
                    }
            else:
                return None

    @classmethod
    def get_all(cls):
        if not os.path.exists(cls.filename):
            return None
        with open(cls.filename, "r") as csv_file:
            ret_data = []
            for row in csv_file.readlines():
                timestamp, sensor_name, temperature, humidity = row.split(",")
                ret_data.append(
                    {
                        "timestamp": timestamp,
                        "sensor_name": sensor_name,
                        "temperature": temperature,
                        "humidity": humidity,
                    }
                )

            return ret_data
