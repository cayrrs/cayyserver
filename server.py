from flask import Flask, render_template, jsonify
import psutil
import time
import platform

app = Flask(__name__)
start_time = time.time()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/status")
def status():
    return jsonify({
        "cpu": psutil.cpu_percent(interval=0.5),
        "ram": psutil.virtual_memory().percent,
        "ram_mb": psutil.virtual_memory().used // 1024 // 1024,
        "uptime_sec": int(time.time() - start_time),
        "disk": psutil.disk_usage("/").percent,
        "hostname": platform.node(),
        "os": platform.system()
    })

if __name__ == "__main__":
    print("flask starting...")
    app.run(host="0.0.0.0", port=8000, debug=False)