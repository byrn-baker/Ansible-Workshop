import json
import requests
from netaddr import *
from operator import itemgetter
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
        "query": "query ($device: [String]) { devices(name__isw: $device){name config_context local_asn: cf_device_bgp viritual_router_mac: cf_virtual_router_mac tags {slug} site {vlans {name vid vxlan_rt: cf_vxlan_vlan_rt role {slug}}} interfaces {name role: cf_role virtual_router: cf_virtual_router_ipv4 vlan_vni: cf_vxlan_vlan_vni label description enabled mode tagged_vlans{vid} lag {name} ip_addresses {address vrf {name rd}} connected_interface{device{name}name ip_addresses{address}}}}}",
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

if 'host' in device[0]['name']:
    for vlan in device[0]['site']['vlans']:
        try:
            if vlan['role']['slug'] == 'vxlan':
                print("vlan %s" % (vlan['vid']))
                print("  name %s" % (vlan['name']))
                print("!")
        except Exception:
            pass
    for iface in device[0]['interfaces']:
        # Ethernet Interface Configuration
        if 'Ethernet' in iface['name']:
            if iface['label'] == 'trunk':
                print("interface %s" % (iface['name']))
                print(" description **%s** %s-%s" % (iface['lag']['name'] ,iface['connected_interface']['device']['name'], iface['connected_interface']['name']))
                print(" switchport mode trunk")
                try:
                    vlan_list = list(map(itemgetter('vid'), iface['tagged_vlans']))
                    separator = ","
                    print(" switchport trunk allowed vlan %s" % (separator.join(map(str, vlan_list))))
                except Exception:
                    pass
            
                try:
                    po = iface['lag']['name']
                    print(" channel-group %s mode active" % (po.replace("Port-Channel","")))
                except Exception:
                    pass
                print("!")
        # Port-Channel interface configuration
        if 'Port-Channel' in iface['name']:
            if iface['label'] == 'trunk':
                print("interface %s" % (iface['name']))
                print(" description %s" % (iface['description']))
                print(" switchport mode trunk")
                try:
                    vlan_list = list(map(itemgetter('vid'), iface['tagged_vlans']))
                    separator = ","
                    print(" switchport trunk allowed vlan %s" % (separator.join(map(str, vlan_list))))
                except Exception:
                    pass
                print("!")
        # SVI Interfaces configuration
        if 'Vlan' in iface['name']:
            if iface['label'] == 'Layer3' and iface['role'] == 'vxlan':
              print("interface %s" % (iface['name']))
              print("  description %s" % (iface['description']))
              for ip in iface['ip_addresses']:  
                print(" ip address %s" % (ip['address']))

if 'leaf' in device[0]['name']:
    for vlan in device[0]['site']['vlans']:
        try:
            if vlan['role']['slug'] == 'vxlan':
                print("vlan %s" % (vlan['vid']))
                print("  name %s" % (vlan['name']))
                print("!")
        except Exception:
            pass
    for iface in device[0]['interfaces']:
        # Ethernet Interface Configuration
        if 'Ethernet' in iface['name']:
            if iface['label'] == 'trunk':
                if iface['role'] == 'host_connection':
                    print("interface %s" % (iface['name']))
                    print(" description **%s** %s-%s" % (iface['lag']['name'] ,iface['connected_interface']['device']['name'], iface['connected_interface']['name']))
                    print(" switchport mode trunk")
                    try:
                        vlan_list = list(map(itemgetter('vid'), iface['tagged_vlans']))
                        separator = ","
                        print(" switchport trunk allowed vlan %s" % (separator.join(map(str, vlan_list))))
                    except Exception:
                        pass
                
                    try:
                        po = iface['lag']['name']
                        print(" channel-group %s mode active" % (po.replace("Port-Channel","")))
                    except Exception:
                        pass
                    print("!")
        # Port-Channel interface configuration
        if 'Port-Channel' in iface['name']:
            if iface['label'] == 'trunk':
                if iface['role'] == 'host_connection':
                    print("interface %s" % (iface['name']))
                    print(" description %s" % (iface['description']))
                    print(" switchport mode trunk")
                    try:
                        vlan_list = list(map(itemgetter('vid'), iface['tagged_vlans']))
                        separator = ","
                        print(" switchport trunk allowed vlan %s" % (separator.join(map(str, vlan_list))))
                    except Exception:
                        pass
                    print("!")

        if 'Vlan' in iface['name']:
            if iface['name'] != 'Vlan4094':
                if iface['label'] == 'Layer3':
                    if iface['role'] == 'vxlan':
                        print("interface %s" % (iface['name']))
                        for ip in iface['ip_addresses']:  
                            print(" ip address %s" % (ip['address']))