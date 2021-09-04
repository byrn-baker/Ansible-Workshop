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
    # print (device)

# Query for Spine BGP
def spine_devices():
  device_name = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_SYSTEM_LABELS)
  for item in device_name:
    if item.startswith('hostname'):
        device = item.strip('hostname')
        url = "http://192.168.130.109:8000/api/graphql/"
        query = device.replace(":","")
        ltr1 = query[-3]
        ltr2 = query[-2]
        ltr3 = query[-1]
        dc = []
        dc = str.join('', ltr1) + str.join('', ltr2) + str.join('', ltr3)
        hostname = "spine1" + "-" + dc
        payload = json.dumps({
        "query": "query ($device: [String]) { devices(name__isw: $device) { name local_asn: cf_device_bgp }}",
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

        spine_devices.device = output['data']['devices']
        # print(json.dumps(output, indent=2))
        # print (device)

# Query for DCI BGP
def dci_devices():
  device_name = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_SYSTEM_LABELS)
  for item in device_name:
    if item.startswith('hostname'):
        device = item.strip('hostname')
        url = "http://192.168.130.109:8000/api/graphql/"
        hostname = device.replace(":","")
        payload = json.dumps({
         "query": "query ($device: [String]) { devices(name__isw: $device) { name local_asn: cf_device_bgp }}",
        "variables": {
        "device": "dci"
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

        dci_devices.device = output['data']['devices']
        # print(json.dumps(output, indent=2))
        # print (output)

nautobot_device()
device = nautobot_device.device
spine_devices()
spine_device = spine_devices.device
dci_devices()
dci_device = dci_devices.device

# Interfaces
if "leaf1" in device[0]['name'] or "leaf3" in device[0]['name'] or "borderleaf1" in device[0]['name']:
    print("spanning-tree mode mstp\n"
          "!\n"
          "no spanning-tree vlan-id 4094\n"
          "!\n"
          "vlan 4094\n"
          "  trunk group MLAGPEER")
    print("!")
    
elif "leaf2" in device[0]['name'] or "leaf4" in device[0]['name'] or "borderleaf2" in device[0]['name']:
    print("spanning-tree mode mstp\n"
          "!\n"
          "no spanning-tree vlan-id 4094\n"
          "!\n"
          "vlan 4094\n"
          "  trunk group MLAGPEER")
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
        if iface['label'] == 'mlag':
            print("interface %s" % (iface['name']))
            print(" switchport mode trunk\n"
            "  switchport trunk group MLAGPEER")
            print("!")
        if iface['label'] == 'trunk':
            print("interface %s" % (iface['name']))
            print(" switchport mode trunk")
            print("!")
        if iface['label'] == 'Layer3':
            print("interface %s" % (iface['name']))
            print(" no switchport")
            for ip in iface['ip_addresses']:  
                print(" ip address %s" % (ip['address']))
            print("!")
    if "Vlan4094" in iface['name'] and iface['label'] != "Layer3":
        print("interface %s" % (iface['name']))
        for ip in iface['ip_addresses']:
            print("  description MLAG PEER LINK")  
            print(" ip address %s" % (ip['address']))
            print("!")

#MLAG Config
if "leaf1" in device[0]['name'] or "leaf3" in device[0]['name'] or "borderleaf1" in device[0]['name']:
    print("mlag configuration\n"
          "  domain-id MLAG\n"
          "  local-interface Vlan4094\n"
          "  peer-address 192.168.255.2\n"
          "  peer-link Port-Channel10")
    print("!")      
    
elif "leaf2" in device[0]['name'] or "leaf4" in device[0]['name'] or "borderleaf2" in device[0]['name']:
    print("mlag configuration\n"
          "  domain-id MLAG\n"
          "  local-interface Vlan4094\n"
          "  peer-address 192.168.255.1\n"
          "  peer-link Port-Channel10")
    print("!")      

#Prefix List
for prefix in device[0]['config_context']['prefix_list']:
    print("ip prefix-list LOOPBACK permit %s" % (prefix))
    print("!")
if 'spine' in device[0]['name'] or 'dci' in device[0]['name']:    
    print ("route-map LOOPBACK permit 10\n"
            "  match ip address prefix-list LOOPBACK\n"
            "  peer-filter LEAF-AS-RANGE\n"
            "  10 match as-range 65000-65535 result accept")
    print("!")        
if 'leaf' in device[0]['name']:
    print ("route-map LOOPBACK permit 10\n"
        " match ip address prefix-list LOOPBACK")
    print("!")    
print("router bgp %s" % (device[0]["local_asn"]))
for iface in device[0]['interfaces']:
    if 'Loopback0' in iface['name']:
        for rid in iface['ip_addresses']:
            ip = IPNetwork(rid['address'])
            print("   router-id %s" % (ip.ip))
print("   no bgp default ipv4-unicast\n"
    "   maximum-paths 3\n"
    "   distance bgp 20 200 200")
if 'spine' in device[0]['name']:
    print("   bgp listen range 10.0.0.0/16 peer-group LEAF_UNDERLAY peer-filter LEAF-AS-RANGE\n"
        "   neighbor LEAF_UNDERLAY peer group\n"
        "   neighbor LEAF_UNDERLAY send-community extended\n"
        "   neighbor LEAF_UNDERLAY maximum-routes 12000")
if 'dci' in device[0]['name']:
    print("   bgp listen range 10.0.0.0/16 peer-group BORDERLEAF_UNDERLAY peer-filter LEAF-AS-RANGE\n"
        "   neighbor BORDERLEAF_UNDERLAY peer group\n"
        "   neighbor BORDERLEAF_UNDERLAY send-community extended\n"
        "   neighbor BORDERLEAF_UNDERLAY maximum-routes 12000")
if 'leaf' in device[0]['name']:
    print("   neighbor SPINE_UNDERLAY peer group")
    print("   neighbor SPINE_UNDERLAY remote-as %s" % (spine_device[0]['local_asn']))
    print("   neighbor SPINE_UNDERLAY send-community extended\n"
        "   neighbor SPINE_UNDERLAY maximum-routes 12000")
    print("   neighbor LEAF_Peer peer group")
    print("   neighbor LEAF_Peer remote-as %s" % (device[0]["local_asn"]))
    print("   neighbor LEAF_Peer next-hop-self\n"
            "   neighbor LEAF_Peer send-community extended\n"
            "   neighbor LEAF_Peer maximum-routes 12000")
try:
    if 'borderleaf' in device[0]['name']:
        print("   neighbor DCI_UNDERLAY peer group")
        print("   neighbor DCI_UNDERLAY remote-as %s" % dci_device[0]['local_asn'])
        print("   neighbor DCI_UNDERLAY send-community extended\n"
            "   neighbor DCI_UNDERLAY maximum-routes 12000")
except Exception:
    pass
for iface in device[0]['interfaces']:
    if iface['role'] == 'spine':
        for ip in iface['connected_interface']['ip_addresses']:
            ip = IPNetwork(ip['address'])
            peer = (ip.ip)
            print("   neighbor %s peer group SPINE_UNDERLAY" % (peer))
if "leaf1" in device[0]['name'] or "leaf3" in device[0]['name'] or "borderleaf1" in device[0]['name']:
    print("   neighbor 192.168.255.2 peer group LEAF_Peer")
elif "leaf2" in device[0]['name'] or "leaf4" in device[0]['name'] or "borderleaf2" in device[0]['name']:
    print("   neighbor 192.168.255.1 peer group LEAF_Peer")
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
if "leaf1" in device[0]['name'] or "leaf2" in device[0]['name'] or "leaf3" in device[0]['name'] or "leaf4" in device[0]['name']:
    print("     neighbor SPINE_UNDERLAY activate")
    print("     neighbor LEAF_Peer activate")
if "borderleaf1" in device[0]['name'] or "borderleaf2" in device[0]['name']:
  print("     neighbor DCI_UNDERLAY activate")
if 'dci' in device[0]['name']:
    print("     neighbor BORDERLEAF_UNDERLAY activate")
print("     redistribute connected route-map LOOPBACK")