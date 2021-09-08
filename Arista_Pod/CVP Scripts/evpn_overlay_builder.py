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

def spine_devices():
  # device_name = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_SYSTEM_LABELS)
  # for item in device_name:
  #   if item.startswith('hostname'):
  #     device = item.strip('hostname')
    url = "http://192.168.130.109:8000/api/graphql/"
    # query = device.replace(":","")
    query = nautobot_device.device[0]['name']
    ltr1 = query[-3]
    ltr2 = query[-2]
    ltr3 = query[-1]
    dc = []
    dc = str.join('', ltr1) + str.join('', ltr2) + str.join('', ltr3)
    
    nautobot_query = "query ($device: [String], $dc: [String]) { devices(name__isw: $device, name__ic: $dc) {name config_context local_asn: cf_device_bgp viritual_router_mac: cf_virtual_router_mac tags {slug} site {vlans {name vid vxlan_rt: cf_vxlan_vlan_rt role {slug}}} interfaces {name role: cf_role virtual_router: cf_virtual_router_ipv4 vlan_vni: cf_vxlan_vlan_vni label description enabled mode lag {name} ip_addresses {address vrf {name rd}} connected_interface{device{name}name ip_addresses{address}}}}}"

    payload = json.dumps({
    "query":  nautobot_query,
    "variables": {
    "device": "spine",
    "dc": dc
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
    spine_devices.dc = dc
    # print(json.dumps(output, indent=2))
    # print (device)

def leaf_devices():
  # device_name = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_SYSTEM_LABELS)
  # for item in device_name:
  #   if item.startswith('hostname'):
  #     device = item.strip('hostname')
    url = "http://192.168.130.109:8000/api/graphql/"
    # query = device.replace(":","")
    query = nautobot_device.device[0]['name']
    ltr1 = query[-3]
    ltr2 = query[-2]
    ltr3 = query[-1]
    dc = []
    dc = str.join('', ltr1) + str.join('', ltr2) + str.join('', ltr3)
    
    nautobot_query = "query ($device: [String], $dc: [String]) { devices(name__isw: $device, name__ic: $dc) {name config_context local_asn: cf_device_bgp viritual_router_mac: cf_virtual_router_mac tags {slug} site {vlans {name vid vxlan_rt: cf_vxlan_vlan_rt role {slug}}} interfaces {name role: cf_role virtual_router: cf_virtual_router_ipv4 vlan_vni: cf_vxlan_vlan_vni label description enabled mode lag {name} ip_addresses {address vrf {name rd}} connected_interface{device{name}name ip_addresses{address}}}}}"

    payload = json.dumps({
    "query":  nautobot_query,
    "variables": {
    "device": "leaf",
    "dc": dc
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

    leaf_devices.device = output['data']['devices']
    
    # print(json.dumps(output, indent=2))
    # print (device)

def borderleaf_devices():
  # device_name = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_SYSTEM_LABELS)
  # for item in device_name:
  #   if item.startswith('hostname'):
  #     device = item.strip('hostname')
    url = "http://192.168.130.109:8000/api/graphql/"
    # query = device.replace(":","")
    query = nautobot_device.device[0]['name']
    ltr1 = query[-3]
    ltr2 = query[-2]
    ltr3 = query[-1]
    dc = []
    dc = str.join('', ltr1) + str.join('', ltr2) + str.join('', ltr3)
    
    nautobot_query = "query ($device: [String], $dc: [String]) { devices(name__isw: $device, name__ic: $dc) {name config_context local_asn: cf_device_bgp viritual_router_mac: cf_virtual_router_mac tags {slug} site {vlans {name vid vxlan_rt: cf_vxlan_vlan_rt role {slug}}} interfaces {name role: cf_role virtual_router: cf_virtual_router_ipv4 vlan_vni: cf_vxlan_vlan_vni label description enabled mode lag {name} ip_addresses {address vrf {name rd}} connected_interface{device{name}name ip_addresses{address}}}}}"

    payload = json.dumps({
    "query":  nautobot_query,
    "variables": {
    "device": "borderleaf",
    "dc": dc
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

    borderleaf_devices.device = output['data']['devices']

    # print(json.dumps(output, indent=2))
    # print (device)

# GraphQL query for DCI device
def dci_devices():
  # device_name = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_SYSTEM_LABELS)
  # for item in device_name:
  #   if item.startswith('hostname'):
  #       device = item.strip('hostname')
        url = "http://192.168.130.109:8000/api/graphql/"
        # hostname = device.replace(":","")
        payload = json.dumps({
         "query": "query ($device: [String]) { devices(name__isw: $device) { name local_asn: cf_device_bgp interfaces {name role: cf_role virtual_router: cf_virtual_router_ipv4 vlan_vni: cf_vxlan_vlan_vni label description enabled mode lag {name} ip_addresses {address vrf {name rd}} connected_interface{device{name}name ip_addresses{address}}}}}",
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
        
# GraphQL query for VRF data
def conf_vrf():
  url = "http://192.168.130.109:8000/api/graphql/"
  payload = json.dumps({
  "query": "query {vrfs {name rd vni: cf_vrf_vni import_targets {name} export_targets {name}}}"
  })
  headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Token c7fdc6be609a244bb1e851c5e47b3ccd9d990b58',
  'Token': 'c7fdc6be609a244bb1e851c5e47b3ccd9d990b58'
  }

  response = requests.request("POST", url, headers=headers, data=payload, verify=False)

  vrf_data = response.content
  vrf_output = json.loads(vrf_data)
  
  conf_vrf.vrfs = vrf_output['data']['vrfs']
  # print(json.dumps(vrf_output, indent=2))
  # print (vrfs)

def dci_borderleaf_devices():
  # device_name = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_SYSTEM_LABELS)
  # for item in device_name:
  #   if item.startswith('hostname'):
  #     device = item.strip('hostname')
    url = "http://192.168.130.109:8000/api/graphql/"
    # query = device.replace(":","")
    query = nautobot_device.device[0]['name']
    ltr1 = query[-3]
    ltr2 = query[-2]
    ltr3 = query[-1]
    dc = []
    dc = str.join('', ltr1) + str.join('', ltr2) + str.join('', ltr3)
    
    nautobot_query = "query ($device: [String]) { devices(name__isw: $device) {name config_context local_asn: cf_device_bgp viritual_router_mac: cf_virtual_router_mac tags {slug} site {vlans {name vid vxlan_rt: cf_vxlan_vlan_rt role {slug}}} interfaces {name role: cf_role virtual_router: cf_virtual_router_ipv4 vlan_vni: cf_vxlan_vlan_vni label description enabled mode lag {name} ip_addresses {address vrf {name rd}} connected_interface{device{name}name ip_addresses{address}}}}}"

    payload = json.dumps({
    "query":  nautobot_query,
    "variables": {
    "device": "borderleaf"
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

    dci_borderleaf_devices.device = output['data']['devices']

    # print(json.dumps(output, indent=2))
    # print (device)

nautobot_device()
spine_devices()
conf_vrf()
dci_devices()
leaf_devices()
borderleaf_devices()
dci_borderleaf_devices()
device = nautobot_device.device
spine_device = spine_devices.device
dci_device = dci_devices.device
leaf_device = leaf_devices.device
borderleaf_device = borderleaf_devices.device
dci_borderleaf_device = dci_borderleaf_devices.device
dc = spine_devices.dc

leaf1 = 'leaf1-' + dc
leaf2 = 'leaf2-' + dc
leaf3 = 'leaf3-' + dc
leaf4 = 'leaf4-' + dc
borderleaf1 = 'borderleaf1-' + dc
borderleaf2 = 'borderleaf2-' + dc

# BGP Peer Group config
if 'spine' in device[0]['name']:
  print("router bgp %s" % (device[0]['local_asn']))
  print(" neighbor EVPN-OVERLAY-PEERS peer group\n"
        " neighbor EVPN-OVERLAY-PEERS next-hop-unchanged\n"
        " neighbor EVPN-OVERLAY-PEERS update-source Loopback0\n"
        " neighbor EVPN-OVERLAY-PEERS bfd\n"
        " neighbor EVPN-OVERLAY-PEERS ebgp-multihop 3\n"
        " neighbor EVPN-OVERLAY-PEERS send-community extended\n"
        " neighbor EVPN-OVERLAY-PEERS maximum-routes 0"
        )
  for leaf in leaf_device:
    for iface in leaf['interfaces']:
      if 'Loopback0' in iface['name']:
        for ip in iface['ip_addresses']:
          ip = IPNetwork(ip['address'])
          peer = (ip.ip)
          print(" neighbor %s peer group EVPN-OVERLAY-PEERS" % (peer))
          print(" neighbor %s remote-as %s" % (peer, leaf['local_asn']))
  for leaf in borderleaf_device:
    for iface in leaf['interfaces']:
      if 'Loopback0' in iface['name']:
        for ip in iface['ip_addresses']:
          ip = IPNetwork(ip['address'])
          peer = (ip.ip)
          print(" neighbor %s peer group EVPN-OVERLAY-PEERS" % (peer))
          print(" neighbor %s remote-as %s" % (peer, leaf['local_asn']))
  print(" address-family evpn\n"
        "  neighbor EVPN-OVERLAY-PEERS activate")

if 'dci' in device[0]['name']:
  print("router bgp %s" % (device[0]['local_asn']))
  print(" neighbor EVPN-OVERLAY-PEERS peer group\n"
        " neighbor EVPN-OVERLAY-PEERS next-hop-unchanged\n"
        " neighbor EVPN-OVERLAY-PEERS update-source Loopback0\n"
        " neighbor EVPN-OVERLAY-PEERS bfd\n"
        " neighbor EVPN-OVERLAY-PEERS ebgp-multihop 3\n"
        " neighbor EVPN-OVERLAY-PEERS send-community extended\n"
        " neighbor EVPN-OVERLAY-PEERS maximum-routes 0"
        )
  for leaf in dci_borderleaf_device:
    for iface in leaf['interfaces']:
      if 'Loopback0' in iface['name']:
        for ip in iface['ip_addresses']:
          ip = IPNetwork(ip['address'])
          peer = (ip.ip)
          print(" neighbor %s peer group EVPN-OVERLAY-PEERS" % (peer))
          print(" neighbor %s remote-as %s" % (peer, leaf['local_asn']))
  print(" address-family evpn\n"
        "  neighbor EVPN-OVERLAY-PEERS activate")

if device[0]['name'] == leaf1 or device[0]['name'] == leaf2 or device[0]['name'] == leaf3 or device[0]['name'] == leaf4:
  print("router bgp %s" % (device[0]['local_asn']))
  print(" neighbor EVPN-OVERLAY-PEERS peer group")
  print(" neighbor EVPN-OVERLAY-PEERS remote-as %s" % (spine_device[0]['local_asn']))
  print(" neighbor EVPN-OVERLAY-PEERS update-source Loopback0\n"
        " neighbor EVPN-OVERLAY-PEERS bfd\n"
        " neighbor EVPN-OVERLAY-PEERS ebgp-multihop 3\n"
        " neighbor EVPN-OVERLAY-PEERS send-community extended\n"
        " neighbor EVPN-OVERLAY-PEERS maximum-routes 0"
        )
  for spine in spine_device:
    for iface in spine['interfaces']:
      if 'Loopback0' in iface['name']:
        for ip in iface['ip_addresses']:
          ip = IPNetwork(ip['address'])
          peer = (ip.ip)
          print(" neighbor %s peer group EVPN-OVERLAY-PEERS" % (peer))
  print(" address-family evpn\n"
        "  neighbor EVPN-OVERLAY-PEERS activate")

if device[0]['name'] == borderleaf1 or device[0]['name'] == borderleaf2:
  print("router bgp %s" % (device[0]['local_asn']))
  print(" neighbor EVPN-OVERLAY-PEERS peer group")
  print(" neighbor EVPN-OVERLAY-PEERS update-source Loopback0\n"
        " neighbor EVPN-OVERLAY-PEERS bfd\n"
        " neighbor EVPN-OVERLAY-PEERS ebgp-multihop 3\n"
        " neighbor EVPN-OVERLAY-PEERS send-community extended\n"
        " neighbor EVPN-OVERLAY-PEERS maximum-routes 0"
        )
  for dci in dci_device:
    for iface in dci['interfaces']:
      if 'Loopback0' in iface['name']:
        for ip in iface['ip_addresses']:
          ip = IPNetwork(ip['address'])
          peer = (ip.ip)
          print(" neighbor %s peer group EVPN-OVERLAY-PEERS" % (peer))
          print(" neighbor %s remote-as %s" % (peer, dci['local_asn']))
  for spine in spine_device:
    for iface in spine['interfaces']:
      if 'Loopback0' in iface['name']:
        for ip in iface['ip_addresses']:
          ip = IPNetwork(ip['address'])
          peer = (ip.ip)
          print(" neighbor %s peer group EVPN-OVERLAY-PEERS" % (peer))
          print(" neighbor %s remote-as %s" % (peer, spine['local_asn']))
  print(" address-family evpn\n"
        "  neighbor EVPN-OVERLAY-PEERS activate")
