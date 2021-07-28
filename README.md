# Remote Process Monitor
A simple remote process monitor using a DynamoDB table

![Overview](https://github.com/handk85/process-monitor/blob/master/figures/overview.png?raw=true)

## Dependencies
* boto3
* schedule
* psutil

```python
pip3 install boto3 schedule psutil
```

## Configure on a remote machine 
* [Configure boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration)
* Execute `create_table.py` for creating a DynamoDB table. By default, it will create a table with the name, `monitor`
```
> python3 create_table.py
```
* Start a `screen` session
```
> screen -S monitor
```
* In the screen session, run `monitor.py`. The `monitor.py` keeps checking the registered processes every minutes.
```
> python3 monitor.py
```
* Detach the screen session by pressing `Ctrl+a d`
* Get the process id (i.e., PID) of interest on a remote machine. For example:
```
> ps -ef | grep python
```
* Run `register_pid.py` to register the process for monitoring:
```
> python3 register_pid.py [PID]
```
* If you run `register_pid.py` on the remote machine, you don't need to specify the hostname.
If not, you can specify the hostname at the end of the script.
```
> python3 register_pid.py [PID] [HOSTNAME]
```
* Then, the process information will be updated in the DynamoDB table every minutes


## Check the current process information
You can check the monitoring information in [DynamoDB console](https://console.aws.amazon.com/dynamodb/home#tables:).
Please double-check the region if you cannot find `monitor` table

Alternatively, you can scan the DynamoDB table via AWS CLI for checking the latest process status
```
> aws dynamodb scan --table-name monitor
```
The expected result is as below:
```
{
    "Items": [
        {
            "pid": {
                "S": "3753234"
            },
            "updated": {
                "S": "2021-07-28 14:20:56"
            },
            "cmdline": {
                "S": "python3 long_task.py"
            },
            "host": {
                "S": "HOST1"
            },
            "status": {
                "S": "Running"
            }
        },
        {
            "pid": {
                "S": "929665"
            },
            "updated": {
                "S": "2021-07-28 14:20:56"
            },
            "cmdline": {
                "S": "python3 another_long_task.py"
            },
            "host": {
                "S": "HOST1"
            },
            "status": {
                "S": "Terminated"
            }
        },
        {
            "pid": {
                "S": "987243"
            },
            "updated": {
                "S": "2021-07-28 14:20:56"
            },
            "cmdline": {
                "S": "python3 super_long_task.py"
            },
            "host": {
                "S": "HOST2"
            },
            "status": {
                "S": "Running"
            }
        }
    ],
    "Count": 3,
    "ScannedCount": 3,
    "ConsumedCapacity": null
}
```

## Local notification config (MacOS only)
First of all, you need to allow notifications for Script Editor.
Go to `System Preferences > Notifications` Then, locate `Script Editor` and turn on `Allow Notifications`

Then, you need to execute `local-notification.py` script for monitoring any process status changes every minutes.
```
> python3 local-notification.py
```
You may want to run the script in a screen session.

If there is any status change, it will trigger a notification on your Mac.
