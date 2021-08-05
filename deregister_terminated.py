from ddb import scan_all, delete_pid

info = scan_all()
for item in info:
    if item["host"] == "Config":
        continue
    if item["status"] == "Terminated":
        print(item)
        delete_pid(item["host"], item["pid"])
