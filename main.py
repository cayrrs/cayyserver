<<<<<<< HEAD
import subprocess

print("launching server window...")

subprocess.Popen([
    "konsole",
    "-e",
    "bash",
    "-c",
    "python3 /home/deck/server/server.py; exec bash"
=======
import subprocess

# opens a visible terminal window
subprocess.Popen([
    "konsole",
    "-e",
    "bash",
    "-c",
    "echo server alive; exec bash"
>>>>>>> ed7b735949a3d46b4c08f5d752a93cdd9912a199
])