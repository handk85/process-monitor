from ddb import put_pid_info
from webhook import get_webhook_type
import random
import sys

if len(sys.argv) < 2:
    print("Please specify webhook url")
    sys.exit(0)

webhook_url = sys.argv[1]
random_pid = random.randint(0, 99999)

webhook_type = get_webhook_type(webhook_url)

obj = {"host": "Config", "pid": str(random_pid), "webhook_url": webhook_url,
       "webhook_type": webhook_type.value}
put_pid_info(obj)
