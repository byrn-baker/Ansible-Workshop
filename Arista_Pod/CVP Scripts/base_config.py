import json
import requests
from netaddr import *
from cvplibrary import CVPGlobalVariables, GlobalVariableNames

# GraphQL query for Device data
def nautobot_device():
  device_name = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_SYSTEM_LABELS)
  for item in device_name:
    if item.startswith('hostname'):
        device = item.strip('hostname')
        url = "http://192.168.130.109:8000/api/graphql/"
        hostname = device.replace(":","")
        payload = json.dumps({
        "query": "query ($device: [String]) { devices(name__isw: $device){name config_context local_asn: cf_device_bgp viritual_router_mac: cf_virtual_router_mac tags {slug} site {vlans {name vid vxlan_rt: cf_vxlan_vlan_rt role {slug}}} interfaces {name role: cf_role virtual_router: cf_virtual_router_ipv4 vlan_vni: cf_vxlan_vlan_vni label description enabled mode lag {name} ip_addresses {address vrf {name rd}} connected_interface{device{name}name ip_addresses{address}}}}}",
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

        nautobot_device.device = output['data']['devices']
        # print(json.dumps(output, indent=2))
        # print (output)
nautobot_device()
device = nautobot_device.device


print("hostname %s" % (device[0]['name']))
print("!")
print("daemon TerminAttr")
print("  exec /usr/bin/TerminAttr -ingestgrpcurl=10.42.0.1:9910 -taillogs -ingestauth=key,arista -smashexcludes=ale,flexCounter,hardware,kni,pulse,strata -ingestexclude=/Sysdb/cell/1/agent,/Sysdb/cell/2/agent\n"
      "  no shutdown")
print("!")
try:
  if "leaf" in device[0]['name'] or "spine" in device[0]['name'] or "borderleaf" in device[0]['name']:
    print("service routing protocols model multi-agent")
    print("!")
except Exception:
  pass
print("alias mlag-reload bash /mnt/flash/shut_intfs && sudo shutdown now -r\n"
"alias conint sh interface | i connected\n"
"alias senz show interface counter error | nz\n"
"alias shmc show int | awk '/^[A-Z]/ { intf = $1 } /, address is/ { print intf, $6 }'\n"
"alias snz show interface counter | nz\n"
"alias spd show port-channel %1 detail all\n"
"alias sqnz show interface counter queue | nz\n"
"alias srnz show interface counter rate | nz\n"
"alias intdesc\n" 
   "!! Usage: intdesc interface-name description\n"
   "10 config\n" 
   "20 int %1\n" 
   "30 desc %2\n" 
   "40 exit")
print("!")
print("dns domain byrnbaker.local")
print("!")
print("ntp server 10.42.0.2 iburst source Management0")
print("!")
print("username arista privilege 15 role network-admin secret 0 arista123")
print("username admin privilege 15 role network-admin secret 0 admin")
print("username cvptemp privilege 15 secret sha512 $6$/BvFD0DvRg.qBMmr$pCseMBn6uStm2Lyoe5a4rOhaakqSOVtpshm4N4aNZBejVY/YGzWi39.8HkoYkUXikOsv7ytBLaq.86dfhRiiC0")
print("!")
print("management api http-commands\n"
   "  no shutdown")
for iface in device[0]['interfaces']:
    if "Management1" in iface['name']:
        print("interface %s" % (iface['name']))
        for ip in iface['ip_addresses']:  
            print(" ip address %s" % (ip['address']))
            print(" no shut")
        print("!")
print("ip routing")
print("ip route 0.0.0.0/0 10.42.0.2")