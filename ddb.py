from boto3.dynamodb.types import TypeSerializer, TypeDeserializer
import configparser
import logging
import boto3
import sys

log_format = "%(asctime)s [%(levelname)-5.5s]  %(message)s"
logging.basicConfig(level=logging.INFO, format=log_format, stream=sys.stdout)

config = configparser.ConfigParser()
config.read("settings.ini")
table_name = config["AWS"]["table_name"]

session = boto3.session.Session()
region_name = session.region_name or config["AWS"]["region_name"]

ddb = boto3.client("dynamodb", region_name=region_name)
# Primary key and sort key
KEYS = ["host", "pid"]

serializer = TypeSerializer()
deserializer = TypeDeserializer()


def validate_put_obj(obj: dict):
    if sum([1 for x in obj if x not in obj]):
        raise Exception("Either 'host' or 'pid' is missing in data: ", obj)


def create_monitor_table():
    try:
        response = ddb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'host',
                    'KeyType': 'HASH'
                }, {
                    'AttributeName': 'pid',
                    'KeyType': 'RANGE'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'host',
                    'AttributeType': 'S'
                }, {
                    'AttributeName': 'pid',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 1,
                'WriteCapacityUnits': 1
            }
        )
        logging.info(response)
    except Exception as e:
        logging.error(e, exc_info=True)


def deserialize_items(items: list):
    processes = []
    for item in items:
        processes.append({k: deserializer.deserialize(v) for k, v in item.items()})
    return processes


def scan_all():
    global ddb
    try:
        response = ddb.scan(TableName=table_name)
    except Exception as e:
        logging.error(e, exc_info=True)
        ddb = boto3.client("dynamodb", region_name=region_name)
        return None

    return deserialize_items(response["Items"])


def get_processes(host: str):
    global ddb
    try:
        response = ddb.query(KeyConditionExpression="host = :host",
                             ExpressionAttributeValues={
                                 ":host": serializer.serialize(host)
                             },
                             TableName=table_name)
    except Exception as e:
        logging.error(e, exc_info=True)
        ddb = boto3.client("dynamodb", region_name=region_name)
        return None

    return deserialize_items(response["Items"])


def get_pids(host: str):
    processes = get_processes(host)
    return [x['pid'] for x in processes] if processes else None


def batch_put_pid_info(objs: list):
    global ddb
    [validate_put_obj(obj) for obj in objs]
    request = {
        table_name: [{"PutRequest":
                          {"Item": {k: serializer.serialize(v) for k, v in
                                    item.items()}}} for item in objs]
    }
    try:
        resp = ddb.batch_write_item(RequestItems=request)
        logging.info(resp)
    except Exception as e:
        logging.error(e, exc_info=True)
        ddb = boto3.client("dynamodb", region_name=region_name)


def put_pid_info(obj: dict):
    validate_put_obj(obj)
    item = {k: serializer.serialize(v) for k, v in obj.items()}
    try:
        resp = ddb.put_item(Item=item, TableName=table_name)
        logging.info(resp)
    except Exception as e:
        logging.error(e, exc_info=True)


def put_basic_pid(host: str, pid: str):
    item = {"host": host, "pid": pid}
    put_pid_info(item)


def delete_pid(host: str, pid: str):
    item = {"host": host, "pid": pid}
    item = {k: serializer.serialize(v) for k, v in item.items()}
    try:
        resp = ddb.delete_item(Key=item, TableName=table_name)
        logging.info(resp)
    except Exception as e:
        logging.error(e, exc_info=True)
