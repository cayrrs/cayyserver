from flask import Flask, render_template, jsonify
import psutil
import time
import platform
import subprocess
import threading

app = Flask(__name__)
start_time = time.time()


def start_bot():
    print("starting bot...")

    proc = subprocess.Popen(
        ["/home/deck/server/venv/bin/python", "dc bot/main.py"],
        cwd=".",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    for line in proc.stdout:
        print(f"[dcbot] {line}", end="")

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
    print("starting bot...")
    start_bot()
    print("bot started")
    print("flask starting...")
    app.run(host="0.0.0.0", port=8000, debug=False) # i hate that this is a BLOCKING FUCING THING MY GOD

    