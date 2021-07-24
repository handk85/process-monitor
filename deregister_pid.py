from ddb import delete_pid
import socket
import sys

if len(sys.argv) < 2:
    print("Please specify pid to monitor")
    sys.exit(0)

pid = sys.argv[1]
host = sys.argv[2] if len(sys.argv) > 2 else socket.gethostname()

delete_pid(host, pid)
