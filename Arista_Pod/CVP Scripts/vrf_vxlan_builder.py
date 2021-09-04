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
  url = "http://192.168.130.50:8000/api/graphql/"
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

# GraphQL query for VRF data
def conf_vrf():
  url = "http://192.168.130.50:8000/api/graphql/"
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


nautobot_device()
conf_vrf()
device = nautobot_device.device

# VRF Configuration
if 'leaf' in device[0]['name']:
  for vrf in conf_vrf.vrfs:
    print("vrf instance %s" % (vrf['name']))
    print("!")
    print("ip routing vrf %s" % (vrf['name']))
    print("!")

   # VLAN Configuration
  for vlan in device[0]['site']['vlans']:
    try:
      if vlan['role']['slug'] == 'vxlan':
        print("vlan %s" % (vlan['vid']))
        print("  name %s" % (vlan['name']))
        print("!")
    except Exception:
      pass

  # SVI Configuration
  for iface in device[0]['interfaces']:
    if 'Vlan' in iface['name']:
      if iface['role'] == 'vxlan':
        print('interface %s' % (iface['name']))
        for ip in iface['ip_addresses']:
          print("  description %s" % iface['description'])
          print("  vrf %s" % (ip['vrf']['name']))
          print("  ip address virtual %s" % (ip['address']))
          print("!")

  #VXLAN INTERFACE
  if conf_vrf.vrfs:
    print("interface vxlan1\n"
          "  vxlan source-interface Loopback1\n"
          "  vxlan udp-port 4789")
    for vrf in conf_vrf.vrfs:
      print("  vxlan vrf %s vni %s" % (vrf['name'], vrf['rd']))
    for iface in device[0]['interfaces']:
      if 'Vlan' in iface['name']:
        if iface['role'] == 'vxlan':
          vlan = iface['name']
          vln = vlan.replace('Vlan',"")
          print("  vxlan vlan %s vni %s" % (vln, iface['vlan_vni']))

   # BGP Configuration vrf
    print("router bgp %s" % (device[0]['local_asn']))
    if conf_vrf.vrfs:
      for vrf in conf_vrf.vrfs:
          print("  vrf %s" % (vrf['name']))
          for iface in device[0]['interfaces']:
            if iface['name'] == 'Loopback1':
              for ip in iface['ip_addresses']:
                lo1 = IPNetwork(ip['address'])
                print("    rd %s:%s" % (lo1.ip, vrf['rd']))
                for rt in vrf['import_targets']:
                  print("    route-target import evpn %s" % (rt['name']))
                for rt in vrf['export_targets']:
                  print("    route-target export evpn %s" % (rt['name']))

    # BGP VLAN Config
    for vlan in device[0]['site']['vlans']:
      try:
        if vlan['role']['slug'] == 'vxlan':
          vid = vlan['vid']
          rt = vlan['vxlan_rt']
          print("  vlan %s" % (vid))
          print("    rd auto")
          print("    route-target both %s:%s" % (rt, rt))
          print("    redistribute learned")
      except Exception:
        pass

