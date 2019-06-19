from app import app


@app.route("/")
@app.route("/index")
def index():
    return "Smart home stuff"
