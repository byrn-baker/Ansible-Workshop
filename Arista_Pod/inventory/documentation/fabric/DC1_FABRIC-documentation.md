# DC1_FABRIC

# Table of Contents
<!-- toc -->

- [Fabric Switches and Management IP](#fabric-switches-and-management-ip)
  - [Fabric Switches with inband Management IP](#fabric-switches-with-inband-management-ip)
- [Fabric Topology](#fabric-topology)
- [Fabric IP Allocation](#fabric-ip-allocation)
  - [Fabric Point-To-Point Links](#fabric-point-to-point-links)
  - [Point-To-Point Links Node Allocation](#point-to-point-links-node-allocation)
  - [Overlay Loopback Interfaces (BGP EVPN Peering)](#overlay-loopback-interfaces-bgp-evpn-peering)
  - [Loopback0 Interfaces Node Allocation](#loopback0-interfaces-node-allocation)
  - [VTEP Loopback VXLAN Tunnel Source Interfaces (Leafs Only)](#vtep-loopback-vxlan-tunnel-source-interfaces-leafs-only)
  - [VTEP Loopback Node allocation](#vtep-loopback-node-allocation)

<!-- toc -->
# Fabric Switches and Management IP

| POD | Type | Node | Management IP | Platform | Provisioned in CloudVision |
| --- | ---- | ---- | ------------- | -------- | -------------------------- |
| DC1_FABRIC | l2leaf | dc1-l2leaf1 | 10.42.0.28/24 | vEOS-LAB | Provisioned |
| DC1_FABRIC | l2leaf | dc1-l2leaf2 | 10.42.0.29/24 | vEOS-LAB | Provisioned |
| DC1_FABRIC | l3leaf | dc1-leaf1 | 10.42.0.24/24 | vEOS-LAB | Provisioned |
| DC1_FABRIC | l3leaf | dc1-leaf2 | 10.42.0.25/24 | vEOS-LAB | Provisioned |
| DC1_FABRIC | l3leaf | dc1-leaf3 | 10.42.0.26/24 | vEOS-LAB | Provisioned |
| DC1_FABRIC | l3leaf | dc1-leaf4 | 10.42.0.27/24 | vEOS-LAB | Provisioned |
| DC1_FABRIC | spine | dc1-spine1 | 10.42.0.21/24 | vEOS-LAB | Provisioned |
| DC1_FABRIC | spine | dc1-spine2 | 10.42.0.22/24 | vEOS-LAB | Provisioned |
| DC1_FABRIC | spine | dc1-spine3 | 10.42.0.23/24 | vEOS-LAB | Provisioned |

> Provision status is based on Ansible inventory declaration and do not represent real status from CloudVision.

## Fabric Switches with inband Management IP
| POD | Type | Node | Management IP | Inband Interface |
| --- | ---- | ---- | ------------- | ---------------- |

# Fabric Topology

| Type | Node | Node Interface | Peer Type | Peer Node | Peer Interface |
| ---- | ---- | -------------- | --------- | ----------| -------------- |
| l2leaf | dc1-l2leaf1 | Ethernet1 | l3leaf | dc1-leaf1 | Ethernet6 |
| l2leaf | dc1-l2leaf1 | Ethernet2 | l3leaf | dc1-leaf2 | Ethernet6 |
| l2leaf | dc1-l2leaf2 | Ethernet1 | l3leaf | dc1-leaf3 | Ethernet6 |
| l2leaf | dc1-l2leaf2 | Ethernet2 | l3leaf | dc1-leaf4 | Ethernet6 |
| l3leaf | dc1-leaf1 | Ethernet1 | mlag_peer | dc1-leaf2 | Ethernet1 |
| l3leaf | dc1-leaf1 | Ethernet2 | mlag_peer | dc1-leaf2 | Ethernet2 |
| l3leaf | dc1-leaf3 | Ethernet1 | mlag_peer | dc1-leaf4 | Ethernet1 |
| l3leaf | dc1-leaf3 | Ethernet2 | mlag_peer | dc1-leaf4 | Ethernet2 |

# Fabric IP Allocation

## Fabric Point-To-Point Links

| P2P Summary | Available Addresses | Assigned addresses | Assigned Address % |
| ----------- | ------------------- | ------------------ | ------------------ |
| 172.31.0.0/24 | 256 | 0 | 0.0 % |

## Point-To-Point Links Node Allocation

| Node | Node Interface | Node IP Address | Peer Node | Peer Interface | Peer IP Address |
| ---- | -------------- | --------------- | --------- | -------------- | --------------- |

## Overlay Loopback Interfaces (BGP EVPN Peering)

| Overlay Loopback Summary | Available Addresses | Assigned addresses | Assigned Address % |
| ------------------------ | ------------------- | ------------------ | ------------------ |
| 192.168.0.0/24 | 256 | 7 | 2.74 % |

## Loopback0 Interfaces Node Allocation

| POD | Node | Loopback0 |
| --- | ---- | --------- |
| DC1_FABRIC | dc1-leaf1 | 192.168.0.4/32 |
| DC1_FABRIC | dc1-leaf2 | 192.168.0.5/32 |
| DC1_FABRIC | dc1-leaf3 | 192.168.0.6/32 |
| DC1_FABRIC | dc1-leaf4 | 192.168.0.7/32 |
| DC1_FABRIC | dc1-spine1 | 192.168.0.1/32 |
| DC1_FABRIC | dc1-spine2 | 192.168.0.2/32 |
| DC1_FABRIC | dc1-spine3 | 192.168.0.3/32 |

## VTEP Loopback VXLAN Tunnel Source Interfaces (Leafs Only)

| VTEP Loopback Summary | Available Addresses | Assigned addresses | Assigned Address % |
| --------------------- | ------------------- | ------------------ | ------------------ |
| 192.168.1.0/24 | 256 | 4 | 1.57 % |

## VTEP Loopback Node allocation

| POD | Node | Loopback1 |
| --- | ---- | --------- |
| DC1_FABRIC | dc1-leaf1 | 192.168.1.4/32 |
| DC1_FABRIC | dc1-leaf2 | 192.168.1.4/32 |
| DC1_FABRIC | dc1-leaf3 | 192.168.1.6/32 |
| DC1_FABRIC | dc1-leaf4 | 192.168.1.6/32 |
