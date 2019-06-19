import csv
import datetime
import os

CSV_FILE = "./readings.csv"


class CSVStore:
    filename = CSV_FILE

    @classmethod
    def add_sensor_reading(cls, sensor_name, temperature, humidity):
        with open(cls.filename, "a") as csv_file:
            writer = csv.writer(csv_file, delimiter=",")
            timestamp = datetime.datetime.utcnow().strftime(r"%Y-%m-%d %H:%M:%S")
            writer.writerow([timestamp, sensor_name, temperature, humidity])

    @classmethod
    def get_last_reading(cls, desired_sensor_name):
        if not os.path.exists(cls.filename):
            return None
        with open(cls.filename, "r") as csv_file:
            for row in csv_file.readlines()[-2:]:
                timestamp, sensor_name, temperature, humidity = row.split(",")
                if sensor_name == desired_sensor_name:
                    return {
                        "location": sensor_name,
                        "timestamp": timestamp,
                        "temperature": temperature,
                        "humidity": humidity,
                    }
            else:
                return None
