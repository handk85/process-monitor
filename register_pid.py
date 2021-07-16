from ddb import put_basic_pid
import socket
import sys

if len(sys.argv) < 2:
    print("Please specify pid to monitor")
    sys.exit(0)

host = socket.gethostname()
pid = sys.argv[1]

put_basic_pid(host, pid)
