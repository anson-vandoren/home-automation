import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "superhandydandypassword"
    TIME_FORMAT = r"%Y-%m-%d %H:%M:%S"
