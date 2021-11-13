from ddb import put_pid_info
from webhook import get_webhook_type
import random
import sys

if len(sys.argv) < 2:
    print("Please specify AWS SNS topic ARN")
    sys.exit(0)

arn = sys.argv[1]
random_pid = random.randint(0, 99999)

obj = {"host": "Config", "pid": str(random_pid), "topic-arn": arn}
put_pid_info(obj)
