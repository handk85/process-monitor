from ddb import delete_pid
import socket
import sys

if len(sys.argv) < 2:
    print("Please specify pid to monitor")
    sys.exit(0)

host = socket.gethostname()
pid = sys.argv[1]

delete_pid(host, pid)
