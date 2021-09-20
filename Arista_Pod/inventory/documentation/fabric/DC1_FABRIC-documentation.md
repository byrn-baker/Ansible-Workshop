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
| DC1_FABRIC | l3leaf | dc1-leaf1 | 10.42.0.24/24 | vEOS-LAB | Provisioned |
| DC1_FABRIC | l3leaf | dc1-leaf2 | 10.42.0.25/24 | vEOS-LAB | Provisioned |
| DC1_FABRIC | spine | dc1-spine1 | 10.42.0.21/24 | vEOS-LAB | Provisioned |
| DC1_FABRIC | spine | dc1-spine2 | 10.42.0.22/24 | vEOS-LAB | Provisioned |

> Provision status is based on Ansible inventory declaration and do not represent real status from CloudVision.

## Fabric Switches with inband Management IP
| POD | Type | Node | Management IP | Inband Interface |
| --- | ---- | ---- | ------------- | ---------------- |

# Fabric Topology

| Type | Node | Node Interface | Peer Type | Peer Node | Peer Interface |
| ---- | ---- | -------------- | --------- | ----------| -------------- |
| l2leaf | dc1-l2leaf1 | Ethernet3 | l3leaf | dc1-leaf1 | Ethernet7 |
| l2leaf | dc1-l2leaf1 | Ethernet4 | l3leaf | dc1-leaf2 | Ethernet7 |
| l3leaf | dc1-leaf1 | Ethernet1 | mlag_peer | dc1-leaf2 | Ethernet1 |
| l3leaf | dc1-leaf1 | Ethernet2 | mlag_peer | dc1-leaf2 | Ethernet2 |
| l3leaf | dc1-leaf1 | Ethernet3 | spine | dc1-spine1 | Ethernet2 |
| l3leaf | dc1-leaf1 | Ethernet4 | spine | dc1-spine2 | Ethernet2 |
| l3leaf | dc1-leaf2 | Ethernet3 | spine | dc1-spine1 | Ethernet3 |
| l3leaf | dc1-leaf2 | Ethernet4 | spine | dc1-spine2 | Ethernet3 |

# Fabric IP Allocation

## Fabric Point-To-Point Links

| P2P Summary | Available Addresses | Assigned addresses | Assigned Address % |
| ----------- | ------------------- | ------------------ | ------------------ |
| 172.31.0.0/24 | 256 | 8 | 3.13 % |

## Point-To-Point Links Node Allocation

| Node | Node Interface | Node IP Address | Peer Node | Peer Interface | Peer IP Address |
| ---- | -------------- | --------------- | --------- | -------------- | --------------- |
| dc1-leaf1 | Ethernet3 | 172.31.0.1/31 | dc1-spine1 | Ethernet2 | 172.31.0.0/31 |
| dc1-leaf1 | Ethernet4 | 172.31.0.3/31 | dc1-spine2 | Ethernet2 | 172.31.0.2/31 |
| dc1-leaf2 | Ethernet3 | 172.31.0.9/31 | dc1-spine1 | Ethernet3 | 172.31.0.8/31 |
| dc1-leaf2 | Ethernet4 | 172.31.0.11/31 | dc1-spine2 | Ethernet3 | 172.31.0.10/31 |

## Overlay Loopback Interfaces (BGP EVPN Peering)

| Overlay Loopback Summary | Available Addresses | Assigned addresses | Assigned Address % |
| ------------------------ | ------------------- | ------------------ | ------------------ |
| 192.168.0.0/24 | 256 | 4 | 1.57 % |

## Loopback0 Interfaces Node Allocation

| POD | Node | Loopback0 |
| --- | ---- | --------- |
| DC1_FABRIC | dc1-leaf1 | 192.168.0.5/32 |
| DC1_FABRIC | dc1-leaf2 | 192.168.0.6/32 |
| DC1_FABRIC | dc1-spine1 | 192.168.0.1/32 |
| DC1_FABRIC | dc1-spine2 | 192.168.0.2/32 |

## VTEP Loopback VXLAN Tunnel Source Interfaces (Leafs Only)

| VTEP Loopback Summary | Available Addresses | Assigned addresses | Assigned Address % |
| --------------------- | ------------------- | ------------------ | ------------------ |
| 192.168.1.0/24 | 256 | 2 | 0.79 % |

## VTEP Loopback Node allocation

| POD | Node | Loopback1 |
| --- | ---- | --------- |
| DC1_FABRIC | dc1-leaf1 | 192.168.1.5/32 |
| DC1_FABRIC | dc1-leaf2 | 192.168.1.5/32 |
