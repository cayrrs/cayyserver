import subprocess

print("launching server window..")

subprocess.Popen([
    "konsole",
    "-e",
    "bash",
    "-c",
    "python3 /home/deck/server/server.py; exec bash"
])
