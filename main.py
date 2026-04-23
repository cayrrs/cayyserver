import subprocess

# opens a visible terminal window
subprocess.Popen([
    "konsole",
    "-e",
    "bash",
    "-c",
    "echo server alive; exec bash"
])