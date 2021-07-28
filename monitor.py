from ddb import get_pids, batch_put_pid_info
from datetime import datetime
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


def update_monitor_table():
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
        if psutil.pid_exists(int(pid)):
            p = psutil.Process(int(pid))
            info.append(ProcessInfo(host, pid, True, " ".join(p.cmdline())).__dict__)
        else:
            info.append(ProcessInfo(host, pid, False).__dict__)
    batch_put_pid_info(info)


schedule.every(1).minutes.do(update_monitor_table)
while True:
    schedule.run_pending()
    time.sleep(1)
