from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "im working"

if __name__ == "__main__":
    print("flask starting...")
    app.run(host="0.0.0.0", port=8000, debug=True)