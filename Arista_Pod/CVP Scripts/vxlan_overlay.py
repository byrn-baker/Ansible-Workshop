import json
import requests
# from netaddr import *
# from cvplibrary import CVPGlobalVariables, GlobalVariableNames

# GraphQL query for Device data
def conf_vrf_vlans_svi():
#   device_name = CVPGlobalVariables.getValue(GlobalVariableNames.CVP_SYSTEM_LABELS)
#   for item in device_name:
#     if item.startswith('hostname'):
#       device = item.strip('hostname:')
    url = "http://192.168.130.74:8000/api/graphql/"
    # hostname = device.replace(":","")
    payload = json.dumps({
    "query": "query ($device: [String]) { devices(name__isw: $device){name config_context local_asn: cf_device_bgp viritual_router_mac: cf_virtual_router_mac tags {slug} site {vlans {name vid vxlan_rt: cf_vxlan_vlan_rt role {slug}}} interfaces {name role: cf_role virtual_router: cf_virtual_router_ipv4 vlan_vni: cf_vxlan_vlan_vni label description enabled mode lag {name} ip_addresses {address vrf {name rd}} connected_interface{device{name}name ip_addresses{address}}}}}",
    "variables": {
    "device": device
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

    conf_vrf_vlans_svi.device = output['data']['devices']
    # print(json.dumps(output, indent=2))
    # print (device)
      
# GraphQL query for VRF data
def conf_vxlan1():
    url = "http://192.168.130.74:8000/api/graphql/"
    payload = json.dumps({
    "query": "query {vrfs {name vni: cf_vrf_vni}}"
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Token c7fdc6be609a244bb1e851c5e47b3ccd9d990b58',
    'Token': 'c7fdc6be609a244bb1e851c5e47b3ccd9d990b58'
    }

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)

    vrf_data = response.content
    vrf_output = json.loads(vrf_data)
   
    conf_vxlan1.vrfs = vrf_output['data']['vrfs']
    # print(json.dumps(vrf_output, indent=2))
    # print (vrfs)

conf_vrf_vlans_svi()
device = conf_vrf_vlans_svi.device
conf_vxlan1()
if 'spine' in device[0]['name']:
    # BGP Config
    print("router bgp %s" % (device[0]['local_asn']))
    print("  address-famliy evpn\n"
            "    neighbor LEAF_UNDERLAY activate")
if 'leaf' in device[0]['name']:
    # VRF Configuration
    for vrf in conf_vxlan1.vrfs:
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

    # Router Virtual Address Configuration
    try:
        if device[0]['viritual_router_mac'] != None:
            print("ip virtual-router mac-address %s" % (device[0]['viritual_router_mac']))
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
    if conf_vxlan1.vrfs:
        print("interface vxlan1\n"
            "  vxlan source-interface Loopback1\n"
            "  vxlan udp-port 4789")
        for vrf in conf_vxlan1.vrfs:
            print("  vxlan vrf %s vni %s" % (vrf['name'], vrf['vni']))
        for iface in device[0]['interfaces']:
            if 'Vlan' in iface['name']:
                if iface['role'] == 'vxlan':
                    vlan = iface['name']
                    vln = vlan.replace('Vlan',"")
                    print("  vxlan vlan %s vni %s" % (vln, iface['vlan_vni']))
    # BGP Config
    print("router bgp %s" % (device[0]['local_asn']))
    print("  address-famliy evpn\n"
            "    neighbor SPINE_UNDERLAY activate")
    # BGP Configuration vrf
    if conf_vxlan1.vrfs:
        for vrf in conf_vxlan1.vrfs:
            print("  vrf %s" % (vrf['name']))
            for iface in device[0]['interfaces']:
                if iface['name'] == 'Loopback1':
                    for ip in iface['ip_addresses']:
                        lo1 = IPNetwork(ip['address'])
                        print("    rd %s:%s" % (lo1.ip, vrf['vni']))
                        print("    route-target import evpn %s:%s" % (vrf['vni'], vrf['vni']))
                        print("    route-target export evpn %s:%s" % (vrf['vni'], vrf['vni']))

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