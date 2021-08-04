from ddb import get_pids, batch_put_pid_info
from datetime import datetime
import logging
import socket
import psutil
import schedule
import time


class ProcessInfo:
    def __init__(self, host: str, pid: str, status: bool, cmdline: str = "", started: str = ""):
        self.host = host
        self.pid = pid
        self.status = "Running" if status else "Terminated"
        self.updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cmdline = cmdline
        self.started = started

    def terminated(self):
        self.status = "Terminated"


def convert_create_time(create_time: float):
    d = datetime.fromtimestamp(create_time)
    return d.strftime("%Y-%m-%d %H:%M:%S")


def update_monitor_table(host: str, info: dict):
    pids = get_pids(host)
    # if no info returned, just stop the function
    if not pids or len(pids) < 1:
        logging.info("No process ids to check in the host: %s", host)
        return

    for pid in pids:
        if pid not in info and psutil.pid_exists(int(pid)):
            p = psutil.Process(int(pid))
            info[pid] = ProcessInfo(host, pid, True, " ".join(p.cmdline()),
                                    convert_create_time(p.create_time()))
        if pid in info and not psutil.pid_exists(int(pid)):
            info[pid].terminated()

    data = [v for k, v in info.items()]
    batch_put_pid_info(data)


hostname = socket.gethostname()
process_info = {}
schedule.every(10).seconds.do(update_monitor_table, hostname, process_info)
while True:
    schedule.run_pending()
    time.sleep(1)
