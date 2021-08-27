from ddb import get_processes, batch_put_pid_info, get_config
from webhook import send_webhook, webhook_type_map, WebhookTypes
from datetime import datetime
import logging
import socket
import psutil
import schedule
import time
import boto3


class ProcessInfo:
    def __init__(self, host: str, pid: str, status: bool, cmdline: str = "", started: str = ""):
        self.host = host
        self.pid = pid
        self.status = "Running" if status else "Terminated"
        self.cmdline = cmdline
        self.started = started
        self.updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def terminated(self):
        self.status = "Terminated"

    def update(self):
        self.updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def pretty_str(self):
        return '''
Host: %s
PID: %s
Status: %s
Command: %s
Started: %s
Updated: %s
        ''' % (self.host, self.pid, self.status, self.cmdline, self.started, self.updated)


def convert_create_time(create_time: float):
    d = datetime.fromtimestamp(create_time)
    return d.strftime("%Y-%m-%d %H:%M:%S")


def notification(p_info: ProcessInfo):
    config = get_config()
    if not config or len(config) < 1:
        return
    for item in config:
        if "webhook_url" in item:
            webhook_type = WebhookTypes(item["webhook_type"])
            webhook_class = webhook_type_map[webhook_type]
            message = webhook_class(item["webhook_url"], "The process is terminated",
                                    "The process is terminated", p_info.__dict__)
            logging.info("Send %s webhook via %s", webhook_type.value, item["webhook_url"])
            send_webhook(message)
        if "topic-arn" in item:
            client = boto3.client("sns")
            logging.info("Publish AWS SNS message to %s" % item["topic-arn"])
            client.publish(TopicArn=item["topic-arn"],
                           Subject="The process on %s is terminated" % p_info.host,
                           Message=p_info.pretty_str())


def update_monitor_table(host: str, info: dict):
    processes = get_processes(host)
    # if no info returned, just stop the function
    if not processes or len(processes) < 1:
        logging.info("No process ids to check in the host: %s", host)
        return

    logging.info("Process IDs: %s", list(info.keys()))
    for item in processes:
        pid = item['pid']
        if pid not in info and psutil.pid_exists(int(pid)):
            p = psutil.Process(int(pid))
            info[pid] = ProcessInfo(host, pid, True, " ".join(p.cmdline()),
                                    convert_create_time(p.create_time()))
        if pid in info:
            if info[pid].status == "Terminated":
                del info[pid]
                continue
            if not psutil.pid_exists(int(pid)):
                info[pid].terminated()
                notification(info[pid])

    data = [v for k, v in info.items()]
    [p.update() for p in data]
    if len(data) > 0:
        batch_put_pid_info(data)


hostname = socket.gethostname()
process_info = {}
schedule.every(1).minutes.do(update_monitor_table, hostname, process_info)
while True:
    schedule.run_pending()
    time.sleep(1)
