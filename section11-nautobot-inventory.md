## Nautobot Inventory
Replacing the static inventory files with the Nautobot Inventory module is the last piece of the puzzle in getting rid of the static group and host vars files. You check out the docs on how to use Nautobot Inventory [here](https://nautobot-ansible.readthedocs.io/en/latest/plugins/inventory_inventory.html#ansible-collections-networktocode-nautobot-inventory-inventory). I will still keep one static file under ```group_vars/all/all.yaml``` which holds the device username and password as well as the nautobot URL and token. This is a demo instance, and you would not want to store either of these in cleartext. 

```
### inventory/nautobot_inventory.yaml
---
plugin: networktocode.nautobot.inventory
api_endpoint: "https://192.168.130.204"
token: "c7fdc6be609a244bb1e851c5e47b3ccd9d990b58"
validate_certs: False
config_context: False
group_by:
  - device_roles
query_filters:
  - site: 'pod1'
device_query_filters:
  - has_primary_ip: 'true'
compose:
  ansible_network_os: platform.name
  ansible_host: primary_ip4.address | ipaddr('address')
```

We want to group and filter our responses to mimic the inventory file. We want to group by device_roles which should be pod_router, pod_l3_switch, pod_l2_switch. I am working with pod1, so my filter will only pull the pod1 site. We can drill down further and filter out any device without a primary_ip configured. The composed section is used to take existing variables and transform those into something that Ansible can use. We transform the nautobot ```platform.name``` into ```ansible_network_os```
Ansible needs to know the type of network device it is connecting to when using vendor-specific modules. If you are not using DNS, then the hosts IP address will also be needed, so we transform the devices ```primary_ip4.address``` to ``` ansible_host```.

We can test this new inventory file with ```ansible-inventory -v --list -i inventory/nautobot_inventory.yaml``` this will give you an output with devices based on our filters and groups. You should also see our two composed items as well. 

Here is an example of the output you should see:

```
(.venv) root@c1557e2bca38:/home/Ansible-Workshop# ansible-inventory -v --list -i inventory/nautobot_inventory.yaml
Using /home/Ansible-Workshop/ansible.cfg as config file
Fetching: https://192.168.130.204/api/docs/?format=openapi
Fetching: https://192.168.130.204/api/dcim/devices/?limit=0&site=pod1&has_primary_ip=true&exclude=config_context
Fetching: https://192.168.130.204/api/virtualization/virtual-machines/?limit=0&site=pod1&exclude=config_context
Fetching: https://192.168.130.204/api/dcim/sites/?limit=0
Fetching: https://192.168.130.204/api/dcim/regions/?limit=0
Fetching: https://192.168.130.204/api/tenancy/tenants/?limit=0
Fetching: https://192.168.130.204/api/dcim/racks/?limit=0
Fetching: https://192.168.130.204/api/dcim/rack-groups/?limit=0
Fetching: https://192.168.130.204/api/dcim/device-roles/?limit=0
Fetching: https://192.168.130.204/api/dcim/platforms/?limit=0
Fetching: https://192.168.130.204/api/dcim/device-types/?limit=0
Fetching: https://192.168.130.204/api/dcim/manufacturers/?limit=0
Fetching: https://192.168.130.204/api/virtualization/clusters/?limit=0
Fetching: https://192.168.130.204/api/ipam/services/?limit=0
{
    "_meta": {
        "hostvars": {
            "pod1r1": {
                "ansible_host": "192.168.4.17",
                "ansible_network_os": "cisco_ios",
                "ansible_password": "N@utobot123",
                "ansible_user": "nautobot",
                "configuration": {
                    "bgp": {
                        "address_family_ipv4": {
                            "advertised_networks": {
                                "155.1.1.0": {
                                    "net_mask": "255.255.255.192"
                                },
                                "155.1.1.128": {
                                    "net_mask": "255.255.255.192"
                                },
                                "155.1.1.64": {
                                    "net_mask": "255.255.255.192"
                                }
                            },
                            "agg_mask": "255.255.255.0",
                            "agg_network": "155.1.1.0"
                        },
                        "ebgp": {
                            "neighbors": {
                                "24.24.1.1": {
                                    "r_asn": 400
                                }
                            }
                        },
                        "ibgp": {
                            "l_asn": 65001,
                            "neighbors": [
                                "10.1.1.2",
                                "10.1.1.3"
                            ]
                        }
                    },
                    "dhcp_pool": [
                        {
                            "default_router": "155.1.1.1",
                            "excluded_address": "155.1.1.1 155.1.1.3",
                            "lease": 30,
                            "name": 300,
                            "network": "155.1.1.0/26"
                        },
                        {
                            "default_router": "155.1.1.65",
                            "excluded_address": "155.1.1.65 155.1.1.67",
                            "lease": 30,
                            "name": 350,
                            "network": "155.1.1.64/26"
                        },
                        {
                            "default_router": "155.1.1.129",
                            "excluded_address": "155.1.1.129 155.1.1.131",
                            "lease": 30,
                            "name": 400,
                            "network": "155.1.1.128/26"
                        }
                    ],
                    "interfaces": {
                        "l3_interfaces": [
                            {
                                "description": "UPLINK TO INTERNET PROVIDER",
                                "ipv4": "24.24.1.2",
                                "ipv4_mask": "255.255.255.0",
                                "name": "GigabitEthernet0/0"
                            },
                            {
                                "description": "DOWNLINK POD1SW1",
                                "ipv4": "10.10.1.0",
                                "ipv4_mask": "255.255.255.254",
                                "name": "GigabitEthernet0/1",
                                "ospf": {
                                    "area": 0,
                                    "network": "point-to-point"
                                }
                            },
                            {
                                "description": "DOWNLINK POD1SW2",
                                "ipv4": "10.10.1.2",
                                "ipv4_mask": "255.255.255.254",
                                "name": "GigabitEthernet0/2",
                                "ospf": {
                                    "area": 0,
                                    "network": "point-to-point"
                                }
                            },
                            {
                                "description": "iBGP LOOPBACK",
                                "ipv4": "10.1.1.1",
                                "ipv4_mask": "255.255.255.255",
                                "name": "Loopback0",
                                "ospf": {
                                    "area": 0,
                                    "network": "point-to-point"
                                }
                            }
                        ]
                    },
                    "ospf": {
                        "instance": 1,
                        "router_id": "10.1.1.1"
                    }
                },
                "custom_fields": {},
                "device_roles": [
                    "pod_router"
                ],
                "device_types": [
                    "vios_router"
                ],
                "is_virtual": false,
                "local_context_data": [
                    {
                        "bgp": {
                            "address_family_ipv4": {
                                "advertised_networks": [
                                    "155.1.1.0/26",
                                    "155.1.1.128/26",
                                    "155.1.1.64/26"
                                ],
                                "agg_network": [
                                    "155.1.1.0/24"
                                ]
                            },
                            "ebgp": {
                                "neighbors": {
                                    "24.24.1.1": {
                                        "r_asn": 400
                                    }
                                }
                            },
                            "ibgp": {
                                "l_asn": 65001,
                                "neighbors": [
                                    "10.0.1.2",
                                    "10.0.1.3"
                                ]
                            }
                        }
                    }
                ],
                "manufacturers": [
                    "cisco"
                ],
                "nb_token": "c7fdc6be609a244bb1e851c5e47b3ccd9d990b58",
                "nb_url": "https://192.168.130.204",
                "platforms": [
                    "cisco_ios"
                ],
                "primary_ip4": "192.168.4.17",
                "rack_groups": [],
                "racks": [
                    "pod1_rr_1"
                ],
                "regions": [],
                "services": [],
                "sites": [
                    "pod1"
                ],
                "status": {
                    "label": "Active",
                    "value": "active"
                },
                "tags": [
                    "ospf",
                    "pod1_dhcp_server"
                ]
            },
            "pod1sw1": {
                "ansible_host": "192.168.4.18",
                "ansible_network_os": "cisco_ios",
                "ansible_password": "N@utobot123",
                "ansible_user": "nautobot",
                "configuration": {
                    "bgp": {
                        "address_family_ipv4": {
                            "advertised_networks": {
                                "155.1.1.0": {
                                    "net_mask": "255.255.255.192"
                                },
                                "155.1.1.128": {
                                    "net_mask": "255.255.255.192"
                                },
                                "155.1.1.64": {
                                    "net_mask": "255.255.255.192"
                                }
                            }
                        },
                        "ibgp": {
                            "l_asn": 65001,
                            "neighbors": [
                                "10.1.1.1",
                                "10.1.1.3"
                            ]
                        }
                    },
                    "interfaces": {
                        "l3_interfaces": [
                            {
                                "description": "USER_SVI",
                                "dhcp_helper": "10.0.1.1",
                                "ipv4": "155.1.1.2",
                                "ipv4_mask": "255.255.255.192",
                                "name": "vlan300",
                                "vrrp_description": "USER_VLAN",
                                "vrrp_group": 1,
                                "vrrp_primary_ip": "155.1.1.1",
                                "vrrp_priority": 200
                            },
                            {
                                "description": "SERVER_SVI",
                                "dhcp_helper": "10.0.1.1",
                                "ipv4": "155.1.1.66",
                                "ipv4_mask": "255.255.255.192",
                                "name": "vlan350",
                                "vrrp_description": "USER_VLAN",
                                "vrrp_group": 2,
                                "vrrp_primary_ip": "155.1.1.65",
                                "vrrp_priority": 200
                            },
                            {
                                "description": "GUEST_SVI",
                                "dhcp_helper": "10.0.1.1",
                                "ipv4": "155.1.1.130",
                                "ipv4_mask": "255.255.255.192",
                                "name": "vlan400",
                                "vrrp_description": "GUEST_VLAN",
                                "vrrp_group": 3,
                                "vrrp_primary_ip": "155.1.1.129",
                                "vrrp_priority": 200
                            },
                            {
                                "description": "UPLINK POD1R1",
                                "ipv4": "10.10.1.1",
                                "ipv4_mask": "255.255.255.254",
                                "name": "GigabitEthernet0/0",
                                "ospf": {
                                    "area": 0,
                                    "network": "point-to-point"
                                }
                            },
                            {
                                "description": "iBGP LOOPBACK",
                                "ipv4": "10.1.1.2",
                                "ipv4_mask": "255.255.255.255",
                                "name": "Loopback0",
                                "ospf": {
                                    "area": 0,
                                    "network": "point-to-point"
                                }
                            }
                        ],
                        "trunk": [
                            {
                                "allowed_vlans": {
                                    "members": "300,350,400"
                                },
                                "description": "TRUNK TO POD1SW2",
                                "interface_mode": "trunk",
                                "name": "GigabitEthernet0/1",
                                "native_vlan": {
                                    "members": "666"
                                },
                                "port_channel": 12
                            },
                            {
                                "allowed_vlans": {
                                    "members": "300,350,400"
                                },
                                "description": "TRUNK TO POD1SW2",
                                "interface_mode": "trunk",
                                "name": "GigabitEthernet0/2",
                                "native_vlan": {
                                    "members": "666"
                                },
                                "port_channel": 12
                            },
                            {
                                "allowed_vlans": {
                                    "members": "300,350,400"
                                },
                                "description": "TRUNK TO POD1SW2",
                                "interface_mode": "trunk",
                                "name": "Port-Channel12",
                                "native_vlan": {
                                    "members": "666"
                                }
                            },
                            {
                                "allowed_vlans": {
                                    "members": "300,350,400"
                                },
                                "description": "TRUNK TO POD1SW3",
                                "interface_mode": "trunk",
                                "name": "GigabitEthernet0/3",
                                "native_vlan": {
                                    "members": "666"
                                }
                            }
                        ]
                    },
                    "ospf": {
                        "instance": 1,
                        "router_id": "10.1.1.2"
                    },
                    "vlans": {
                        "vlan": [
                            {
                                "name": "USERS",
                                "vlan_id": "300"
                            },
                            {
                                "name": "SERVERS",
                                "vlan_id": "350"
                            },
                            {
                                "name": "GUEST",
                                "vlan_id": "400"
                            },
                            {
                                "name": "NATIVE_VLAN",
                                "vlan_id": "666"
                            }
                        ]
                    }
                },
                "custom_fields": {},
                "device_roles": [
                    "pod_l3_switch"
                ],
                "device_types": [
                    "vios_switch"
                ],
                "is_virtual": false,
                "local_context_data": [
                    {
                        "bgp": {
                            "address_family_ipv4": {
                                "advertised_networks": [
                                    "155.1.1.0/26",
                                    "155.1.1.128/26",
                                    "155.1.1.64/26"
                                ]
                            },
                            "ibgp": {
                                "l_asn": 65001,
                                "neighbors": [
                                    "10.0.1.1",
                                    "10.0.1.3"
                                ]
                            }
                        }
                    }
                ],
                "manufacturers": [
                    "cisco"
                ],
                "nb_token": "c7fdc6be609a244bb1e851c5e47b3ccd9d990b58",
                "nb_url": "https://192.168.130.204",
                "platforms": [
                    "cisco_ios"
                ],
                "primary_ip4": "192.168.4.18",
                "rack_groups": [],
                "racks": [
                    "pod1_rr_1"
                ],
                "regions": [],
                "services": [],
                "sites": [
                    "pod1"
                ],
                "status": {
                    "label": "Active",
                    "value": "active"
                },
                "tags": [
                    "ospf"
                ]
            },
            "pod1sw2": {
                "ansible_host": "192.168.4.19",
                "ansible_network_os": "cisco_ios",
                "ansible_password": "N@utobot123",
                "ansible_user": "nautobot",
                "configuration": {
                    "bgp": {
                        "address_family_ipv4": {
                            "advertised_networks": {
                                "155.1.1.0": {
                                    "net_mask": "255.255.255.192"
                                },
                                "155.1.1.128": {
                                    "net_mask": "255.255.255.192"
                                },
                                "155.1.1.64": {
                                    "net_mask": "255.255.255.192"
                                }
                            }
                        },
                        "ibgp": {
                            "l_asn": 65001,
                            "neighbors": [
                                "10.1.1.1",
                                "10.1.1.2"
                            ]
                        }
                    },
                    "interfaces": {
                        "l3_interfaces": [
                            {
                                "description": "USER_SVI",
                                "dhcp_helper": "10.0.1.1",
                                "ipv4": "155.1.1.3",
                                "ipv4_mask": "255.255.255.192",
                                "name": "vlan300",
                                "vrrp_description": "USER_VLAN",
                                "vrrp_group": 1,
                                "vrrp_primary_ip": "155.1.1.1",
                                "vrrp_priority": 100
                            },
                            {
                                "description": "SERVER_SVI",
                                "dhcp_helper": "10.0.1.1",
                                "ipv4": "155.1.1.67",
                                "ipv4_mask": "255.255.255.192",
                                "name": "vlan350",
                                "vrrp_description": "USER_VLAN",
                                "vrrp_group": 2,
                                "vrrp_primary_ip": "155.1.1.65",
                                "vrrp_priority": 100
                            },
                            {
                                "description": "GUEST_SVI",
                                "dhcp_helper": "10.0.1.1",
                                "ipv4": "155.1.1.131",
                                "ipv4_mask": "255.255.255.192",
                                "name": "vlan400",
                                "vrrp_description": "USER_VLAN",
                                "vrrp_group": 3,
                                "vrrp_primary_ip": "155.1.1.129",
                                "vrrp_priority": 100
                            },
                            {
                                "description": "UPLINK POD1R1",
                                "ipv4": "10.10.1.3",
                                "ipv4_mask": "255.255.255.254",
                                "name": "GigabitEthernet0/0",
                                "ospf": {
                                    "area": 0,
                                    "network": "point-to-point"
                                }
                            },
                            {
                                "description": "iBGP LOOPBACK",
                                "ipv4": "10.1.1.3",
                                "ipv4_mask": "255.255.255.255",
                                "name": "Loopback0",
                                "ospf": {
                                    "area": 0,
                                    "network": "point-to-point"
                                }
                            }
                        ],
                        "trunk": [
                            {
                                "allowed_vlans": {
                                    "members": "300,350,400"
                                },
                                "description": "TRUNK TO POD1SW1",
                                "interface_mode": "trunk",
                                "name": "GigabitEthernet0/1",
                                "native_vlan": {
                                    "members": "666"
                                },
                                "port_channel": 12
                            },
                            {
                                "allowed_vlans": {
                                    "members": "300,350,400"
                                },
                                "description": "TRUNK TO POD1SW1",
                                "interface_mode": "trunk",
                                "name": "GigabitEthernet0/2",
                                "native_vlan": {
                                    "members": "666"
                                },
                                "port_channel": 12
                            },
                            {
                                "allowed_vlans": {
                                    "members": "300,350,400"
                                },
                                "description": "TRUNK TO POD1SW1",
                                "interface_mode": "trunk",
                                "name": "Port-Channel12",
                                "native_vlan": {
                                    "members": "666"
                                }
                            },
                            {
                                "allowed_vlans": {
                                    "members": "300,350,400"
                                },
                                "description": "TRUNK TO POD1SW3",
                                "interface_mode": "trunk",
                                "name": "GigabitEthernet0/3",
                                "native_vlan": {
                                    "members": "666"
                                }
                            }
                        ]
                    },
                    "ospf": {
                        "instance": 1,
                        "router_id": "10.1.1.3"
                    },
                    "vlans": {
                        "vlan": [
                            {
                                "name": "USERS",
                                "vlan_id": "300"
                            },
                            {
                                "name": "SERVERS",
                                "vlan_id": "350"
                            },
                            {
                                "name": "GUEST",
                                "vlan_id": "400"
                            },
                            {
                                "name": "NATIVE_VLAN",
                                "vlan_id": "666"
                            }
                        ]
                    }
                },
                "custom_fields": {},
                "device_roles": [
                    "pod_l3_switch"
                ],
                "device_types": [
                    "vios_switch"
                ],
                "is_virtual": false,
                "local_context_data": [
                    {
                        "bgp": {
                            "address_family_ipv4": {
                                "advertised_networks": [
                                    "155.1.1.0/26",
                                    "155.1.1.128/26",
                                    "155.1.1.64/26"
                                ]
                            },
                            "ibgp": {
                                "l_asn": 65001,
                                "neighbors": [
                                    "10.0.1.1",
                                    "10.0.1.2"
                                ]
                            }
                        }
                    }
                ],
                "manufacturers": [
                    "cisco"
                ],
                "nb_token": "c7fdc6be609a244bb1e851c5e47b3ccd9d990b58",
                "nb_url": "https://192.168.130.204",
                "platforms": [
                    "cisco_ios"
                ],
                "primary_ip4": "192.168.4.19",
                "rack_groups": [],
                "racks": [
                    "pod1_rr_1"
                ],
                "regions": [],
                "services": [],
                "sites": [
                    "pod1"
                ],
                "status": {
                    "label": "Active",
                    "value": "active"
                },
                "tags": [
                    "ospf"
                ]
            },
            "pod1sw3": {
                "ansible_host": "192.168.4.20",
                "ansible_network_os": "cisco_ios",
                "ansible_password": "N@utobot123",
                "ansible_user": "nautobot",
                "configuration": {
                    "interfaces": {
                        "access": [
                            {
                                "description": "USERS",
                                "interface_mode": "access",
                                "name": "GigabitEthernet0/3",
                                "vlan": {
                                    "members": "300"
                                }
                            },
                            {
                                "description": "SERVERS",
                                "interface_mode": "access",
                                "name": "GigabitEthernet1/0",
                                "vlan": {
                                    "members": "350"
                                }
                            },
                            {
                                "description": "GUEST",
                                "interface_mode": "access",
                                "name": "GigabitEthernet1/1",
                                "vlan": {
                                    "members": "400"
                                }
                            }
                        ],
                        "trunk": [
                            {
                                "allowed_vlans": {
                                    "members": "300,350,400"
                                },
                                "description": "TRUNK TO POD1SW1",
                                "interface_mode": "trunk",
                                "name": "GigabitEthernet0/1",
                                "native_vlan": {
                                    "members": "666"
                                }
                            },
                            {
                                "allowed_vlans": {
                                    "members": "300,350,400"
                                },
                                "description": "TRUNK TO POD1SW2",
                                "interface_mode": "trunk",
                                "name": "GigabitEthernet0/2",
                                "native_vlan": {
                                    "members": "666"
                                }
                            }
                        ]
                    },
                    "vlans": {
                        "vlan": [
                            {
                                "name": "USERS",
                                "vlan_id": "300"
                            },
                            {
                                "name": "SERVERS",
                                "vlan_id": "350"
                            },
                            {
                                "name": "GUEST",
                                "vlan_id": "400"
                            },
                            {
                                "name": "NATIVE_VLAN",
                                "vlan_id": "666"
                            }
                        ]
                    }
                },
                "custom_fields": {},
                "device_roles": [
                    "pod_l2_switch"
                ],
                "device_types": [
                    "vios_switch"
                ],
                "is_virtual": false,
                "local_context_data": [
                    null
                ],
                "manufacturers": [
                    "cisco"
                ],
                "nb_token": "c7fdc6be609a244bb1e851c5e47b3ccd9d990b58",
                "nb_url": "https://192.168.130.204",
                "platforms": [
                    "cisco_ios"
                ],
                "primary_ip4": "192.168.4.20",
                "rack_groups": [],
                "racks": [
                    "pod1_rr_1"
                ],
                "regions": [],
                "services": [],
                "sites": [
                    "pod1"
                ],
                "status": {
                    "label": "Active",
                    "value": "active"
                },
                "tags": []
            }
        }
    },
    "all": {
        "children": [
            "device_roles_pod_l2_switch",
            "device_roles_pod_l3_switch",
            "device_roles_pod_router",
            "ungrouped"
        ]
    },
    "device_roles_pod_l2_switch": {
        "hosts": [
            "pod1sw3"
        ]
    },
    "device_roles_pod_l3_switch": {
        "hosts": [
            "pod1sw1",
            "pod1sw2"
        ]
    },
    "device_roles_pod_router": {
        "hosts": [
            "pod1r1"
        ]
    }
}
```

As you can see at the top, this module performs several API calls and pulls pack several pieces of info based on our filters, and it looks similar to our graphQL query. All of this information is then distilled down into a file-like inventory format at the bottom. The most significant difference is in this inventory file. You will not see the two things we wanted to compose, ```ansible_network_os``` or ```ansible_host```. These items are found as part of the device query above the bottom's inventory file area. So scroll up to the last device above our inventory format to what should be pod1sw3. You will see a printout that looks like this

```
pod1sw3": {
                "ansible_host": "192.168.4.20",
                "ansible_network_os": "cisco_ios",
                "ansible_password": "N@utobot123",
                "ansible_user": "nautobot",
```

Here we can see the items that we set to be composed. These become the host_vars of the inventory file at the bottom of the query. Notice that the napalm username and password set up when installing Nautobot is used as the ```ansible_user``` and ```ansible_password```. 

That brings us to a point now where we can rely entirely on Nautobot to provide the host_vars and group_vars to any of our playbooks. 



[Installing Ansible - Section 1](installing_ansible.md)

[Creating an Inventory File - Section 2](inventory_file.md)

[Creating a playbook - Section 3](first_play.md)

[Building Roles - Section 4](building_roles.md)

[Building the core switch Roles - Section 5](section5-coreswitch.md)

[Building the router Roles - Section 6](section6-router.md)

[Introducing Nautobot - Section 7](section7-nautobot.md)

[Introducing PyNautobot - Section 8](section8-pynautobot.md)

[Querying your device data from nautobot - Section 9](section9-querynautobot.md)

[Full configuration Jinja Templates - Section 10](section10-jinja_templates.md)