# leaf-eBGP-underlay-builder
import yaml
hostname = 'borderleaf2-DC1'
config = """
spine1-DC1:
    interfaces:
        Loopback0:
            ipv4: 192.168.101.101
            mask: 32
        Ethernet2:
            ipv4: 192.168.103.1
            mask: 31
        Ethernet3:
            ipv4: 192.168.103.7
            mask: 31
        Ethernet4:
            ipv4: 192.168.103.13
            mask: 31
        Ethernet5:
            ipv4: 192.168.103.19
            mask: 31
        Ethernet6:
            ipv4: 192.168.103.25
            mask: 31
        Ethernet7:
            ipv4: 192.168.103.31
            mask: 31
    bgp:
        asn: 65100
spine2-DC1:
    interfaces:
        Loopback0:
            ipv4: 192.168.101.102
            mask: 32
        Ethernet2:
            ipv4: 192.168.103.3
            mask: 31
        Ethernet3:
            ipv4: 192.168.103.9
            mask: 31
        Ethernet4:
            ipv4: 192.168.103.15
            mask: 31
        Ethernet5:
            ipv4: 192.168.103.21
            mask: 31
        Ethernet6:
            ipv4: 192.168.103.27
            mask: 31
        Ethernet7:
            ipv4: 192.168.103.33
            mask: 31
    bgp:
        asn: 65100
spine3-DC1:
    interfaces:
        Loopback0:
            ipv4: 192.168.101.103
            mask: 32
        Ethernet2:
            ipv4: 192.168.103.5
            mask: 31
        Ethernet3:
            ipv4: 192.168.103.11
            mask: 31
        Ethernet4:
            ipv4: 192.168.103.17
            mask: 31
        Ethernet5:
            ipv4: 192.168.103.23
            mask: 31
        Ethernet6:
            ipv4: 192.168.103.29
            mask: 31
        Ethernet7:
            ipv4: 192.168.103.35
            mask: 31
    bgp:
        asn: 65100
leaf1-DC1:
    interfaces:
        Loopback0: 
            ipv4: 192.168.101.11
            mask: 32
        Loopback1:
            ipv4: 192.168.102.11
            mask: 32
        Ethernet3:
            ipv4: 192.168.103.0
            mask: 31
        Ethernet4:
            ipv4: 192.168.103.2
            mask: 31
        Ethernet5:
            ipv4: 192.168.103.4
            mask: 31
    bgp:
        asn: 65101
        spine_peers:
            - 192.168.103.1
            - 192.168.103.3
            - 192.168.103.5
        leaf_peers:
            - 192.168.255.2
leaf2-DC1:
    interfaces:
        Loopback0: 
            ipv4: 192.168.101.12
            mask: 32
        Loopback1:
            ipv4: 192.168.102.11
            mask: 32
        Ethernet3:
            ipv4: 192.168.103.6
            mask: 31
        Ethernet4:
            ipv4: 192.168.103.8
            mask: 31
        Ethernet5:
            ipv4: 192.168.103.10
            mask: 31
    bgp:
        asn: 65101
        spine_peers:
            - 192.168.103.7
            - 192.168.103.9
            - 192.168.103.11
        leaf_peers:
            - 192.168.255.1   
leaf3-DC1:
    interfaces:
        Loopback0: 
            ipv4: 192.168.101.13
            mask: 32
        Loopback1:
            ipv4: 192.168.102.13
            mask: 32
        Ethernet3:
            ipv4: 192.168.103.12
            mask: 31
        Ethernet4:
            ipv4: 192.168.103.14
            mask: 31
        Ethernet5:
            ipv4: 192.168.103.16
            mask: 31
    bgp:
        asn: 65102
        spine_peers:
            - 192.168.103.13
            - 192.168.103.15
            - 192.168.103.17
        leaf_peers:
            - 192.168.255.2  
leaf4-DC1:
    interfaces:
        Loopback0: 
            ipv4: 192.168.101.14
            mask: 32
        Loopback1:
            ipv4: 192.168.102.13
            mask: 32
        Ethernet3:
            ipv4: 192.168.103.18
            mask: 31
        Ethernet4:
            ipv4: 192.168.103.20
            mask: 31
        Ethernet5:
            ipv4: 192.168.103.22
            mask: 31
    bgp:
        asn: 65102
        spine_peers:
            - 192.168.103.19
            - 192.168.103.21
            - 192.168.103.23
        leaf_peers:
            - 192.168.255.1   
borderleaf1-DC1:
    interfaces:
        Loopback0: 
            ipv4: 192.168.101.21
            mask: 32
        Loopback1:
            ipv4: 192.168.102.21
            mask: 32
        Ethernet3:
            ipv4: 192.168.103.24
            mask: 31
        Ethernet4:
            ipv4: 192.168.103.26
            mask: 31
        Ethernet5:
            ipv4: 192.168.103.28
            mask: 31
        Ethernet12: 
            ipv4: 192.168.254.0
            mask: 31
    bgp:
        asn: 65103
        spine_peers:
            - 192.168.103.25
            - 192.168.103.27
            - 192.168.103.29
        leaf_peers:
            - 192.168.255.2    
borderleaf2-DC1:
    interfaces:
        Loopback0: 
            ipv4: 192.168.101.22
            mask: 32
        Loopback1:
            ipv4: 192.168.102.21
            mask: 32
        Ethernet3:
            ipv4: 192.168.103.30
            mask: 31
        Ethernet4:
            ipv4: 192.168.103.32
            mask: 31
        Ethernet5:
            ipv4: 192.168.103.34
            mask: 31
        Ethernet12: 
            ipv4: 192.168.254.2
            mask: 31
    bgp:
        asn: 65103
        spine_peers:
            - 192.168.103.31
            - 192.168.103.33
            - 192.168.103.35
        leaf_peers:
            - 192.168.255.1
spine1-DC2:
    interfaces:
        Loopback0:
            ipv4: 192.168.201.101
            mask: 32
        Ethernet2:
            ipv4: 192.168.203.1
            mask: 31
        Ethernet3:
            ipv4: 192.168.203.7
            mask: 31
        Ethernet4:
            ipv4: 192.168.203.13
            mask: 31
        Ethernet5:
            ipv4: 192.168.203.19
            mask: 31
        Ethernet6:
            ipv4: 192.168.203.25
            mask: 31
        Ethernet7:
            ipv4: 192.168.203.31
            mask: 31
    bgp:
        asn: 65100
spine2-DC2:
    interfaces:
        Loopback0:
            ipv4: 192.168.201.102
            mask: 32
        Ethernet2:
            ipv4: 192.168.203.3
            mask: 31
        Ethernet3:
            ipv4: 192.168.203.9
            mask: 31
        Ethernet4:
            ipv4: 192.168.203.15
            mask: 31
        Ethernet5:
            ipv4: 192.168.203.21
            mask: 31
        Ethernet6:
            ipv4: 192.168.203.27
            mask: 31
        Ethernet7:
            ipv4: 192.168.203.33
            mask: 31
    bgp:
        asn: 65100
spine3-DC2:
    interfaces:
        Loopback0:
            ipv4: 192.168.201.103
            mask: 32
        Ethernet2:
            ipv4: 192.168.203.5
            mask: 31
        Ethernet3:
            ipv4: 192.168.203.11
            mask: 31
        Ethernet4:
            ipv4: 192.168.203.17
            mask: 31
        Ethernet5:
            ipv4: 192.168.203.23
            mask: 31
        Ethernet6:
            ipv4: 192.168.203.29
            mask: 31
        Ethernet7:
            ipv4: 192.168.203.35
            mask: 31
    bgp:
        asn: 65100
leaf1-DC2:
    interfaces:
        Loopback0: 
            ipv4: 192.168.201.11
            mask: 32
        Loopback1:
            ipv4: 192.168.102.11
            mask: 32
        Ethernet3:
            ipv4: 192.168.203.0
            mask: 31
        Ethernet4:
            ipv4: 192.168.203.2
            mask: 31
        Ethernet5:
            ipv4: 192.168.203.4
            mask: 31
    bgp:
        asn: 65101
        spine_peers:
            - 192.168.203.1
            - 192.168.203.3
            - 192.168.203.5
        leaf_peers:
            - 192.168.255.2
leaf2-DC2:
    interfaces:
        Loopback0: 
            ipv4: 192.168.201.12
            mask: 32
        Loopback1:
            ipv4: 192.168.102.11
            mask: 32
        Ethernet3:
            ipv4: 192.168.203.6
            mask: 31
        Ethernet4:
            ipv4: 192.168.203.8
            mask: 31
        Ethernet5:
            ipv4: 192.168.203.10
            mask: 31
    bgp:
        asn: 65101
        spine_peers:
            - 192.168.203.7
            - 192.168.203.9
            - 192.168.203.11
        leaf_peers:
            - 192.168.255.1    
leaf3-DC2:
    interfaces:
        Loopback0: 
            ipv4: 192.168.201.13
            mask: 32
        Loopback1:
            ipv4: 192.168.102.13
            mask: 32
        Ethernet3:
            ipv4: 192.168.203.12
            mask: 31
        Ethernet4:
            ipv4: 192.168.203.14
            mask: 31
        Ethernet5:
            ipv4: 192.168.203.16
            mask: 31
    bgp:
        asn: 65102
        spine_peers:
            - 192.168.203.13
            - 192.168.203.15
            - 192.168.203.17
        leaf_peers:
            - 192.168.255.2    
leaf4-DC2:
    interfaces:
        Loopback0: 
            ipv4: 192.168.201.14
            mask: 32
        Loopback1:
            ipv4: 192.168.102.13
            mask: 32
        Ethernet3:
            ipv4: 192.168.203.18
            mask: 31
        Ethernet4:
            ipv4: 192.168.203.20
            mask: 31
        Ethernet5:
            ipv4: 192.168.203.22
            mask: 31
    bgp:
        asn: 65102
        spine_peers:
            - 192.168.203.19
            - 192.168.203.21
            - 192.168.203.23
        leaf_peers:
            - 192.168.255.1    
borderleaf1-DC2:
    interfaces:
        Loopback0: 
            ipv4: 192.168.201.21
            mask: 32
        Loopback1:
            ipv4: 192.168.102.21
            mask: 32
        Ethernet3:
            ipv4: 192.168.203.24
            mask: 31
        Ethernet4:
            ipv4: 192.168.203.26
            mask: 31
        Ethernet5:
            ipv4: 192.168.203.28
            mask: 31
        Ethernet12: 
            ipv4: 192.168.254.0
            mask: 31
    bgp:
        asn: 65103
        spine_peers:
            - 192.168.203.25
            - 192.168.203.27
            - 192.168.203.29
        leaf_peers:
            - 192.168.255.2    
borderleaf2-DC2:
    interfaces:
        Loopback0: 
            ipv4: 192.168.201.22
            mask: 32
        Loopback1:
            ipv4: 192.168.102.21
            mask: 32
        Ethernet3:
            ipv4: 192.168.203.30
            mask: 31
        Ethernet4:
            ipv4: 192.168.203.32
            mask: 31
        Ethernet5:
            ipv4: 192.168.203.34
            mask: 31
        Ethernet12: 
            ipv4: 192.168.254.2
            mask: 31
    bgp:
        asn: 65103
        spine_peers:
            - 192.168.203.31
            - 192.168.203.33
            - 192.168.203.35
        leaf_peers:
            - 192.168.255.1                
"""
switches = yaml.load(config, Loader=yaml.FullLoader)
for iface in switches[hostname]['interfaces']:
    print("interface %s" % (iface))
    ip = switches[hostname]['interfaces'][iface]['ipv4']
    mask = switches[hostname]['interfaces'][iface]['mask']
    print(" ip address %s/%s" % (ip, mask))
    if "Ethernet" in iface:
        print(" no switchport")
for switch in switches:
    for iface in switches[switch]['interfaces']:

        ip = switches[switch]['interfaces'][iface]['ipv4']
        
        mask = switches[switch]['interfaces'][iface]['mask']
        
        if 'Loopback0' in iface:
            print(" ip prefix-list LOOPBACK permit %s/%s" % (ip, mask)
                )
print (" route-map LOOPBACK permit 10\n"
"   match ip address prefix-list LOOPBACK\n"
"   peer-filter LEAF-AS-RANGE\n"
"   10 match as-range 65000-65535 result accept")
print(" router bgp %s" % (switches[hostname]['bgp']['asn']))
print("   router-id %s" % (switches[hostname]['interfaces']['Loopback0']['ipv4']))
print("   no bgp default ipv4-unicast\n"
"   maximum-paths 3\n"
"   distance bgp 20 200 200\n"
"   neighbor SPINE_Underlay peer group")
print("   neighbor SPINE_Underlay remote-as %s" % (switches['spine1-DC1']['bgp']['asn']))
print("   neighbor SPINE_Underlay send-community\n"
      "   neighbor SPINE_Underlay maximum-routes 12000\n"
      "   neighbor LEAF_Peer peer group")
print("   neighbor LEAF_Peer remote-as %s" % (switches[hostname]['bgp']['asn']))
print("   neighbor LEAF_Peer next-hop-self\n"
      "   neighbor LEAF_Peer update-source Loopback0\n"
      "   neighbor LEAF_Peer maximum-routes 12000")
for peer in switches[hostname]['bgp']['spine_peers']:
  print("   neighbor %s peer group SPINE_Underlay" % (peer))
for peer in switches[hostname]['bgp']['leaf_peers']:
  print("   neighbor %s peer group LEAF_Peer" % (peer))
print("   redistribute connected route-map LOOPBACK\n"
      "   address-family ipv4\n"
      "     neighbor SPINE_Underlay activate\n"
      "     neighbor LEAF_Peer activate\n"
      "     redistribute connected route-map LOOPBACK")    