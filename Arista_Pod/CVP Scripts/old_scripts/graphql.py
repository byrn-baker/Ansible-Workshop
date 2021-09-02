import requests
import json
import pprint

datacenter = "dc1-spine-01"

for item in device_name:
    if item.startswith('hostname'):
        hostname = item.strip('hostname')
        url = "https://192.168.130.153/api/graphql/"

        payload = json.dumps({
        "query": "query ($device: [String]) { devices(name__isw: $device){name _custom_field_data interfaces {name description enabled ip_addresses {address} connected_interface{device{name}name}}}}",
        "variables": {
            "device": hostname
        }
        })
        headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Token c7fdc6be609a244bb1e851c5e47b3ccd9d990b58',
        'Token': 'c7fdc6be609a244bb1e851c5e47b3ccd9d990b58'
        }

        response = requests.request("POST", url, headers=headers, data=payload, verify=False)

        data = response.content
        output = json.loads(data)

        print(json.dumps(output, indent=2))



# hostname = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_SYSTEM_LABELS)
# for item in hostname:
#     if item.startswith('hostname:'):
#         host = item.strip('hostname:')