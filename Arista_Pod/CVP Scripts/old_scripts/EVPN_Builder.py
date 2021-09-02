from cvplibrary import Form, Device
VLAN_ID = Form.getFieldByID('vlan_id').getValue()
anycast_addr = Form.getFieldByID('anycast_addr').getValue()
net_name = Form.getFieldByID('net_name').getValue()

def VLAN_DB(VLAN_ID):
  print("")
  print("vlan %s") % (VLAN_ID)
  
def SVI(VLAN_ID, anycast_addr, VRF, net_name):
  print("interface vlan %s") % (VLAN_ID)
  print("  description %s") % (net_name)
  print("  vrf %s") % (VRF)
  print("  ip address virtual %s/24") % (anycast_addr)
  print("  no autostate")
  
def VTI(VLAN_ID, VNI):
  print("")
  print("interface vxlan 1")
  print("  vxlan vlan %s vni %s") % (VLAN_ID, VNI)
  print("")
  
def BGP_EVPN(VLAN_ID, VNI):
  print("")
  print("router bgp %s") % (asn)
  print("  vlan %s") % (VLAN_ID)
  print("    rd auto")
  print("    route-target both %s:%s") % (VNI, VNI)
  print("")