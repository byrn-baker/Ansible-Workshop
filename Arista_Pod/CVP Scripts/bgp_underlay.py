import json
import requests
from netaddr import *
# from cvplibrary import CVPGlobalVariables, GlobalVariableNames

# GraphQL query for Device data
def nautobot_device():
#   device_name = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_SYSTEM_LABELS)
#   for item in device_name:
#     if item.startswith('hostname'):
#       device = item.strip('hostname:')
    url = "http://192.168.130.2:8000/api/graphql/"
    # hostname = device.replace(":","")
    payload = json.dumps({
    "query": "query ($device: [String]) { devices(name__isw: $device){name config_context local_asn: cf_device_bgp viritual_router_mac: cf_virtual_router_mac tags {slug} site {vlans {name vid vxlan_rt: cf_vxlan_vlan_rt role {slug}}} interfaces {name role: cf_role virtual_router: cf_virtual_router_ipv4 vlan_vni: cf_vxlan_vlan_vni label description enabled mode lag {name} ip_addresses {address vrf {name rd}} connected_interface{device{name}name ip_addresses{address}}}}}",
    "variables": {
    "device": 'leaf1-dc1'
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
    # print (device)

# Query for Spine BGP
def spine_devices():
#   device_name = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_SYSTEM_LABELS)
#   for item in device_name:
#     if item.startswith('hostname'):
        # device = item.strip('hostname')
        url = "http://192.168.130.74:8000/api/graphql/"
        # hostname = device.replace(":","")
        payload = json.dumps({
        "query": "query ($device: [String]) { devices(name__isw: $device){name config_context local_asn: cf_device_bgp viritual_router_mac: cf_virtual_router_mac tags {slug} site {vlans {name vid vxlan_rt: cf_vxlan_vlan_rt role {slug}}} interfaces {name role: cf_role virtual_router: cf_virtual_router_ipv4 vlan_vni: cf_vxlan_vlan_vni label description enabled mode lag {name} ip_addresses {address vrf {name rd}} connected_interface{device{name}name ip_addresses{address}}}}}",
        "variables": {
        "device": "spine1"
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

        spine_devices.device = output['data']['devices']
        # print(json.dumps(output, indent=2))
        # print (device)

nautobot_device()
device = nautobot_device.device
spine_devices()
spine_bgp = spine_devices.device

# Interfaces
print("service routing protocols model multi-agent")
print("!")
for iface in device[0]['interfaces']:
    if "Ethernet" in iface['name']:
        if iface['label'] == 'Layer3':
            print("interface %s" % (iface['name']))
            print(" no switchport\n"
                " mtu 9214")
            for ip in iface['ip_addresses']:  
                print(" ip address %s" % (ip['address']))
            print("!")
        if iface['label'] == 'trunk':
            print("interface %s" % (iface['name']))
            print(" switchport mode trunk")
            po = iface['lag']['name']
            print(" channel-group %s mode active" % (po.replace("Port-Channel","")))
            print("!")
    if "Loopback" in iface['name']:
        print("interface %s" % (iface['name']))
        for ip in iface['ip_addresses']:  
            print(" ip address %s" % (ip['address']))
            print("!")
    if "Port-Channel" in iface['name']:
        print("interface %s" % (iface['name']))
        print(" switchport mode trunk")
        print("!")
    if "Vlan" in iface['name']:
        print("interface %s" % (iface['name']))
        for ip in iface['ip_addresses']:  
            print(" ip address %s" % (ip['address']))
            print("!")

#Prefix List
for prefix in device[0]['config_context']['prefix_list']:
    print("ip prefix-list LOOPBACK permit %s" % (prefix))
if 'spine' in device[0]['name'] or 'dci' in device[0]['name']:    
    print ("route-map LOOPBACK permit 10\n"
            "  match ip address prefix-list LOOPBACK\n"
            "  peer-filter LEAF-AS-RANGE\n"
            "  10 match as-range 65000-65535 result accept")
if 'leaf' in device[0]['name']:
    print (" route-map LOOPBACK permit 10\n"
        " match ip address prefix-list LOOPBACK")
print(" router bgp %s" % (device[0]["local_asn"]))
for iface in device[0]['interfaces']:
    if 'Loopback0' in iface['name']:
        for rid in iface['ip_addresses']:
            ip = IPNetwork(rid['address'])
            print("   router-id %s" % (ip.ip))
print("   no bgp default ipv4-unicast\n"
    "   maximum-paths 3\n"
    "   distance bgp 20 200 200")
if 'spine' in device[0]['name']:
    print("   bgp listen range 192.168.0.0/16 peer-group LEAF_UNDERLAY peer-filter LEAF-AS-RANGE\n"
        "   neighbor LEAF_UNDERLAY peer group\n"
        "   neighbor LEAF_UNDERLAY send-community\n"
        "   neighbor LEAF_UNDERLAY maximum-routes 12000")
if 'dci' in device[0]['name']:
    print("   bgp listen range 192.168.0.0/16 peer-group BORDERLEAF_UNDERLAY peer-filter LEAF-AS-RANGE\n"
        "   neighbor BORDERLEAF_UNDERLAY peer group\n"
        "   neighbor BORDERLEAF_UNDERLAY send-community\n"
        "   neighbor BORDERLEAF_UNDERLAY maximum-routes 12000")
if 'leaf' in device[0]['name']:
    print("   neighbor SPINE_UNDERLAY peer group")
    print("   neighbor SPINE_UNDERLAY remote-as %s" % (device[0]['config_context']['bgp']['spine_asn']))
    print("   neighbor SPINE_UNDERLAY send-community\n"
        "   neighbor SPINE_UNDERLAY maximum-routes 12000")
    print("   neighbor LEAF_Peer peer group")
    print("   neighbor LEAF_Peer remote-as %s" % (device[0]["local_asn"]))
    print("   neighbor LEAF_Peer next-hop-self\n"
            "   neighbor LEAF_Peer send-community\n"
            "   neighbor LEAF_Peer maximum-routes 12000")
try:
    if device[0]['config_context']['bgp']['dci_asn']:
        print("   neighbor DCI_UNDERLAY peer group")
        print("   neighbor DCI_UNDERLAY remote-as %s" % device[0]['config_context']['bgp']['dci_asn'])
        print("   neighbor DCI_UNDERLAY send-community\n"
            "   neighbor DCI_UNDERLAY maximum-routes 12000")
except Exception:
    pass
for iface in device[0]['interfaces']:
    if iface['role'] == 'spine':
        for ip in iface['connected_interface']['ip_addresses']:
            ip = IPNetwork(ip['address'])
            peer = (ip.ip)
            print("   neighbor %s peer group SPINE_UNDERLAY" % (peer))
try:
    print("   neighbor %s peer group LEAF_Peer" % (device[0]['config_context']['bgp']['leaf_peer']))
except Exception:
    pass
for iface in device[0]['interfaces']:
    if iface['role'] == 'dci':
        for ip in iface['connected_interface']['ip_addresses']:
            ip = IPNetwork(ip['address'])
            peer = (ip.ip)
            print("   neighbor %s peer group DCI_UNDERLAY" % (peer))
# print("   redistribute connected route-map LOOPBACK")
print("   address-family ipv4")
if 'spine' in device[0]['name']:
    print("     neighbor LEAF_UNDERLAY activate")
    print("     redistribute connected route-map LOOPBACK")
if 'leaf' in device[0]['name']:
    print("     neighbor SPINE_UNDERLAY activate")
    print("     neighbor LEAF_Peer activate")
    try:
        if device[0]['config_context']['bgp']['dci_asn']:
            print("     neighbor DCI_UNDERLAY activate")
    except Exception:
        pass
    print("     redistribute connected route-map LOOPBACK")
if 'dci' in device[0]['name']:
    print("     neighbor BORDERLEAF_UNDERLAY activate\n"
        "     redistribute connected route-map LOOPBACK")