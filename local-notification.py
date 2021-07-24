from ddb import scan_all
import logging
import schedule
import time
import os

status_dict = {}


def local_notification(title, message):
    os.system("""osascript -e 'display notification "{}" with title "{}"'""".format(message, title))


def local_monitor():
    info = scan_all()
    logging.info(info)
    # if no info returned, just stop the function
    if not info:
        return

    for item in info:
        host_pid = "%s-%s" % (item["host"], item["pid"])
        if host_pid in status_dict and item['status'] != status_dict[host_pid]:
            message = "[%s %s] status changed from '%s' to '%s'" \
                      % (item['host'], item['pid'], status_dict[host_pid], item['status'])
            local_notification("Process updated", message)
        status_dict[host_pid] = item['status']


schedule.every(1).minutes.do(local_monitor)
while True:
    schedule.run_pending()
    time.sleep(1)
