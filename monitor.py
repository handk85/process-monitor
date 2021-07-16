from ddb import get_pids, batch_put_pid_info
from datetime import datetime
import logging
import socket
import psutil
import schedule
import time


class ProcessInfo:
    def __init__(self, host: str, pid: str, status: bool):
        self.host = host
        self.pid = pid
        self.status = "Running" if status else "Terminated"
        self.updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S %z")


def update_monitor_table():
    host = socket.gethostname()
    pids = get_pids(host)
    if len(pids) < 1:
        logging.info("No process ids to check in the host:", host)
        return
    info = [ProcessInfo(host, pid, psutil.pid_exists(int(pid))).__dict__ for pid in pids]
    batch_put_pid_info(info)


schedule.every(1).minutes.do(update_monitor_table)
while True:
    schedule.run_pending()
    time.sleep(1)
