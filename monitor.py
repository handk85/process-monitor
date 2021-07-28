from ddb import get_pids, batch_put_pid_info
from datetime import datetime
from collections import defaultdict
import logging
import socket
import psutil
import schedule
import time


class ProcessInfo:
    def __init__(self, host: str, pid: str, status: bool, cmdline: str = ""):
        self.host = host
        self.pid = pid
        self.status = "Running" if status else "Terminated"
        self.updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cmdline = cmdline


pid_cmdlines = defaultdict(str)


def update_monitor_table():
    global pid_cmdlines
    host = socket.gethostname()
    pids = get_pids(host)

    # if no info returned, just stop the function
    if not pids:
        return

    if len(pids) < 1:
        logging.info("No process ids to check in the host: %s", host)
        return
    info = []
    for pid in pids:
        if pid not in pid_cmdlines and psutil.pid_exists(int(pid)):
            p = psutil.Process(int(pid))
            pid_cmdlines[pid] = " ".join(p.cmdline())

        info.append(ProcessInfo(host, pid, psutil.pid_exists(int(pid)), pid_cmdlines[pid]).__dict__)

    batch_put_pid_info(info)


schedule.every(1).minutes.do(update_monitor_table)
while True:
    schedule.run_pending()
    time.sleep(1)
