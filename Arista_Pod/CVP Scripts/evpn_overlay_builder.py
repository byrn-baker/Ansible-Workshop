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
        url = "http://192.168.130.74:8000/api/graphql/"
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
  device_name = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_SYSTEM_LABELS)
  for item in device_name:
    if item.startswith('hostname'):
        device = item.strip('hostname')
        url = "http://192.168.130.74:8000/api/graphql/"
        hostname = device.replace(":","")
        payload = json.dumps({
        "query": "query ($device: [String]) { devices(name__isw: $device){name config_context local_asn: cf_device_bgp viritual_router_mac: cf_virtual_router_mac tags {slug} site {vlans {name vid vxlan_rt: cf_vxlan_vlan_rt role {slug}}} interfaces {name role: cf_role virtual_router: cf_virtual_router_ipv4 vlan_vni: cf_vxlan_vlan_vni label description enabled mode lag {name} ip_addresses {address vrf {name rd}} connected_interface{device{name}name ip_addresses{address}}}}}",
        "variables": {
        "device": "spine"
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
spine_devices()

device = nautobot_device.device
spine_device = spine_devices.device


# BGP Peer Group config
print("router bgp %s" % (device[0]['local_asn']))
if 'spine' in device[0]['name']:
    print("  bgp listen range 192.168.0.0/16 peer-group EVPN-OVERLAY-PEERS peer-filter LEAF-AS-RANGE\n"
          "  neighbor EVPN-OVERLAY-PEERS peer group\n"
          "  neighbor EVPN-OVERLAY-PEERS next-hop-unchanged\n"
          "  neighbor EVPN-OVERLAY-PEERS update-source Loopback0\n"
          "  neighbor EVPN-OVERLAY-PEERS bfd\n"
          "  neighbor EVPN-OVERLAY-PEERS ebgp-multihop 3\n"
          "  neighbor EVPN-OVERLAY-PEERS send-community\n"
          "  neighbor EVPN-OVERLAY-PEERS maximum-routes 0\n"
          "  address-famliy evpn\n"
          "    neighbor EVPN-OVERLAY-PEERS activate"
          )
if 'leaf' in device[0]['name']:
    print("  neighbor EVPN-OVERLAY-PEERS peer group")
    print("  neighbor EVPN-OVERLAY-PEERS remote-as %s" % (device[0]['config_context']['bgp']['spine_asn']))
    print("  neighbor EVPN-OVERLAY-PEERS update-source Loopback0\n"
          "  neighbor EVPN-OVERLAY-PEERS bfd\n"
          "  neighbor EVPN-OVERLAY-PEERS ebgp-multihop 3\n"
          "  neighbor EVPN-OVERLAY-PEERS send-community\n"
          "  neighbor EVPN-OVERLAY-PEERS maximum-routes 0"
          )
    for spine in spine_device:
        for iface in spine['interfaces']:
            if 'Loopback0' in iface['name']:
                for ip in iface['ip_addresses']:
                    ip = IPNetwork(ip['address'])
                    peer = (ip.ip)
                    print("  neighbor %s peer group EVPN-OVERLAY-PEERS" % (peer))
    print("  address-family evpn\n"
          "    neighbor EVPN-OVERLAY-PEERS activate")

