## Section 9: Querying your device data from nautobot
I left off in [Section 7](https://www.workshop.ansible-lab.com/section7-nautobot.html) building playbooks to load Nautobot with all of our POD devices and connectivity. Now we have something to run graphql against that we will use to build our device configurations with. We will be creating ansible playbooks that will perform a query using the [Ansible Nautobot Module](https://nautobot-ansible.readthedocs.io/en/latest/).

First thing we need to create is the actual query and to do that we can test it from the graphiQL link on the bottom right side of your Nautobot gui. 
<img src="/assets/images/nautobot_graphql_1.png" alt="">

You should be presented with the GraphiQL page after clicking the GraphQL link.
<img src="/assets/images/nautobot_graphql_2.png" alt="">

The first thing we will want to do is test out some query to see what kind of information we can get back. To help me get started I used this example [query](https://github.com/nautobot/nautobot-plugin-golden-config/blob/develop/docs/navigating-sot-agg.md) and then added or changes things to fit my needs. You can also watch some of these [NTC](https://blog.networktocode.com/post/leveraging-the-power-of-graphql-with-nautobot/) blog as well to learn a little more around GraphQL. 

So lets try a  simple query for the device name. Our query should look like this to start
```
query {
        devices(name: "pod1r1") {
    name
  }
}
```
The results on the right side of the window should look like this 
```
{
  "data": {
    "devices": [
      {
        "name": "pod1r1"
      }
    ]
  }
}
```
Now there is something called aliasing that can be done to transform the names of the categories in the results. So for example we want name to readout in the results as inventory_hostname. We simply add inventory_hostname into our query like this.
```
query {
        devices(name: "pod1r1") {
    inventory_hostname:name
  }
}
```
Now the result should display this way
```
{
  "data": {
    "devices": [
      {
        "inventory_hostname": "pod1r1"
      }
    ]
  }
}
```
So with aliasing we can transform things like hostname into a predefined ansible variable that could be used in later tasks. So lets talk about the things we do need from Nautobot and recall that what we are attempting to do here is really replace the need for host_vars in our Ansible project. 

With that in mind we know we need several key components from each device. 
1. The device name
2. configuration specifics for BGP and OSPF
3. Interface configurations for access ports, trunk ports, layer3 ports, vlan interfaces
4. IP addressing
5. static routes
6. dhcp server configuration
7. CDP/LLDP configuration
8. AAA configuration

So with that list above lets start building out the query to pull this data from Nautobot. The device name we already have, BGP, OSPF, static routes, dhcp server, CDP/LLDP, and AAA configuration we will need to build into Nautobot using something called config_context. One of the nice features that Nautobot has provided that differs from Netbox is the ability to sync a github repo with Nautobot. One of the function for these repos are to manage things like config_context. You simply create a repo and place into a folder named '''config_contexts''' and add that repo to your Nautobot from the Extensibility menu on the top right and from there just click on the add button.
<img src="/assets/images/nautobot_git_1.png" alt="">
<img src="/assets/images/nautobot_git_2.png" alt="">
<img src="/assets/images/nautobot_git_3.png" alt="">

You'll need to create a git token and then you'll want to highlight in the provides section config contexts. If you done all of that correctly you should see a succesful sync. Now lets start creating some of the files we will want in our config context repo for the OSPF and BGP protocols. Another added bonus is that we can manage our config contexts in YAML format as apposed to JSON format. If you add anything to your Nautobot devices config context from the webapp you need to do that in JSON. Here is where you will find the device config context tab.
<img src="/assets/images/nautobot_config_context_1.png" alt="">

The YAML file for our config_context will need to include some data for Nautobot to recognize it as such.  We use the ```_metadata:``` sort of like a tag that tells nautobot to read in variables that we specify for how the config_context should function. The obvious variables are name, description and is_active, the weight determines when this should appear and is useful when you might have multiple different configurations that might take precendence over another. Last is the role variable, this is used to match devices up based on a specific role is has been assigned, so in our case the config_context will be applied to any device in the pod_router or pod_l3_switch role. For this to sync to nautobot your tag must already exist. 

We will structure the OSPF variables like you would a normal YAML file, we will want to start all of our files to the left and indent as appropriate. Notice that we are only specifying the OSPF router instance (ID). If we needed to add more to this OSPF configuration to the device we could do that on the devices config_context tab or by creating another file with something like a router-id or some kind of area configuration by using the same ```ospf:``` header and including new variables for the items that would be required. These are stackable and are rendered based on the indentation you are providing. 

### pod_ospf.yaml
```
_metadata:
  name: POD_OSPF
  weight: 1000
  description: POD ospf configuration
  is_active: true
  roles:
    - slug: pod_router
    - slug: pod_l3_switch
ospf:
  id: 1
```

Next we need to include configuration for the DHCP server we will be running on each router in the pod. We will use a tag to indicate where this configuration should exist. 

### pod1_dhcp_pool.yaml
```
_metadata:
  name: POD1_DHCP_SERVER
  weight: 1000
  description: POD1 DHCP Server configuration
  is_active: true
  tags:
    - slug: pod1_dhcp_server
dhcp_pool:
  - name: USERS_POOL
    network: "155.1.1.0/26"
    default_router: 155.1.1.1
    lease: 30
    excluded_address: "155.1.1.1 155.1.1.3"

  - name: SERVERS_POOL
    network: "155.1.1.64/26"
    default_router: 155.1.1.65
    lease: 30
    excluded_address: "155.1.1.65 155.1.1.67"

  - name: GUEST_POOL
    network: "155.1.1.128/26"
    default_router: 155.1.1.129
    lease: 30
    excluded_address: "155.1.1.129 155.1.1.131"
```

Lets make our static route file. This time we want this to apply to all of the pods because they are all managed from the same subnet. Instead of a tags field we will use the site field and list the sites this should apply. 

### mgmt_gateway.yaml
```
_metadata:
  name: MGMT_GATEWAY
  weight: 1000
  description: Default route for the MGMT VRF
  is_active: true
  site:
  - POD1
  - POD2
  - POD3
  - POD4
  - POD5
  - POD6
routes:  
  mgmt_gateway: 192.168.4.254
```

Next is the CDP/LLDP configuration, we will use the role variable again to assign this to all devices in each site.

### cdp_lldp.yaml
```
_metadata:
  name: LLDP AND CDP
  weight: 1000
  description: LLDP AND CDP CONFIGURATION 
  is_active: true
  roles:
  - slug: pod_router
  - slug: pod_l3_switch
  - slug: pod_l2_switch
lldp: true
cdp: false 
```

The last one is the AAA configuration and is optional as we did not cover setting up a radius or AAA server in this workshop.

### aaa_new_model.yaml
```
_metadata:
  name: AAA_CONFIGURATION
  weight: 1000
  description: AAA configuration for pods
  is_active: true
  roles:
  - slug: pod_router
  - slug: pod_l3_switch
  - slug: pod_l2_switch
aaa-new-model:
  name: RAD_SERVERS
  type: radius
  ip_address: 192.168.4.253
  auth_port: 1812
  acct_port: 1813
  key: cisco
```

Push these changes to your repo and sync the changes to nautobot. Edit your pod router device and add the tag ```pod1_dhcp_server``` and then add the bgp confuguration to the local config context box just below the tags box. This will need to be done in JSON format, click update and then click over to the config context tab.

```
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
```
<img src="/assets/images/nautobot_config_context_2.png" alt="">

<img src="/assets/images/nautobot_config_context_1.png" alt="">
You should see a rendered configuration and it can be viewed as JSON or YAML format.

<img src="/assets/images/nautobot_config_context_3.png" alt="">

Now that we have all that completed we should look at our graphql query and see if we can pull all of this config_context stuff into the query.
The Query should now look like this

```
query {
        devices(name: "pod1r1") {
    inventory_hostname:name
    config_context
  }
}
```
It should render a result like this

```
{
  "data": {
    "devices": [
      {
        "inventory_hostname": "pod1r1",
        "config_context": {
          "aaa-new-model": {
            "key": "cisco",
            "name": "RAD_SERVERS",
            "type": "radius",
            "acct_port": 1813,
            "auth_port": 1812,
            "ip_address": "192.168.4.253"
          },
          "cdp": false,
          "lldp": true,
          "routes": {
            "mgmt_gateway": "192.168.4.254"
          },
          "dhcp_pool": [
            {
              "name": "USERS_POOL",
              "lease": 30,
              "network": "155.1.1.0/26",
              "default_router": "155.1.1.1",
              "excluded_address": "155.1.1.1 155.1.1.3"
            },
            {
              "name": "SERVERS_POOL",
              "lease": 30,
              "network": "155.1.1.64/26",
              "default_router": "155.1.1.65",
              "excluded_address": "155.1.1.65 155.1.1.67"
            },
            {
              "name": "GUEST_POOL",
              "lease": 30,
              "network": "155.1.1.128/26",
              "default_router": "155.1.1.129",
              "excluded_address": "155.1.1.129 155.1.1.131"
            }
          ],
          "ospf": {
            "id": 1
          },
          "bgp": {
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
            },
            "address_family_ipv4": {
              "agg_network": [
                "155.1.1.0/24"
              ],
              "advertised_networks": [
                "155.1.1.0/26",
                "155.1.1.128/26",
                "155.1.1.64/26"
              ]
            }
          }
        }
      }
    ]
  }
```
Excellent we know have all of this data rendering with the specific device in a similar fashion as it would appear in a file under a host_var folder. Lets add in all of the fields that we will require to build out the configuration.

```
query {
        devices(name: "pod1r1") {
    inventory_hostname:name
    config_context
    primary_ip4 {
            address
            }
    device_role {
            name
            }
            platform {
            name
            slug
            manufacturer {
                name
            }
            napalm_driver
            }
    site{
      slug
      vlans{
        name
        vid
      }
    }
    interfaces {
            name
            description
            enabled
            label
            ip_addresses {
                address
                tags {
                slug
                }
            }
            _custom_field_data
            lag {
                name
            }
            tagged_vlans {
                vid
            }
            untagged_vlan {
                vid
            }
            tagged_vlans {
                vid
            }
            tags {
                slug
            }
      connected_interface{
        device {
          name
        }
        name
      }
            }
  }
}
```
Notice that we have added several new fields to query. Starting at the top after the device name we need the config_context data, the role of the device, the vlans assigned to the site, and the interface configuration details. Lets run this query on our graphiQL interface and make sure the results returned are what we expect to see and that is actually works. If you type out the query yourself you will also notice that there is autocomplete provided by the interface which can be useful for figure out what works in the query and what does not. Also on the right side there is a Docs button that can be used to look up fields you are interested in and how to access them from a query perspective. Alright lets look at the results of our query.

```
{
  "data": {
    "devices": [
      {
        "inventory_hostname": "pod1r1",
        "config_context": {
          "aaa-new-model": {
            "key": "cisco",
            "name": "RAD_SERVERS",
            "type": "radius",
            "acct_port": 1813,
            "auth_port": 1812,
            "ip_address": "192.168.4.253"
          },
          "cdp": false,
          "lldp": true,
          "routes": {
            "mgmt_gateway": "192.168.4.254"
          },
          "dhcp_pool": [
            {
              "name": "USERS_POOL",
              "lease": 30,
              "network": "155.1.1.0/26",
              "default_router": "155.1.1.1",
              "excluded_address": "155.1.1.1 155.1.1.3"
            },
            {
              "name": "SERVERS_POOL",
              "lease": 30,
              "network": "155.1.1.64/26",
              "default_router": "155.1.1.65",
              "excluded_address": "155.1.1.65 155.1.1.67"
            },
            {
              "name": "GUEST_POOL",
              "lease": 30,
              "network": "155.1.1.128/26",
              "default_router": "155.1.1.129",
              "excluded_address": "155.1.1.129 155.1.1.131"
            }
          ],
          "ospf": {
            "id": 1
          },
          "bgp": {
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
            },
            "address_family_ipv4": {
              "agg_network": [
                "155.1.1.0/24"
              ],
              "advertised_networks": [
                "155.1.1.0/26",
                "155.1.1.128/26",
                "155.1.1.64/26"
              ]
            }
          }
        },
        "device_role": {
          "slug": "pod_router"
        },
        "site": {
          "slug": "pod1",
          "vlans": [
            {
              "name": "USERS",
              "vid": 300
            },
            {
              "name": "SERVERS",
              "vid": 350
            },
            {
              "name": "GUESTS",
              "vid": 400
            },
            {
              "name": "NATIVE_VLAN",
              "vid": 666
            }
          ]
        },
        "interfaces": [
          {
            "name": "GigabitEthernet0/0",
            "description": "UPLINK TO INTERNET PROVIDER",
            "enabled": true,
            "label": "layer3",
            "ip_addresses": [
              {
                "address": "24.24.1.2/24",
                "tags": []
              }
            ],
            "_custom_field_data": {
              "vrrp_group": null,
              "dhcp_helper": null,
              "vrrp_priority": null,
              "vrrp_primary_ip": null,
              "vrrp_description": null
            },
            "lag": null,
            "tagged_vlans": [],
            "untagged_vlan": null,
            "tags": [],
            "connected_interface": null
          },
          {
            "name": "GigabitEthernet0/1",
            "description": "DOWNLINK POD1SW1",
            "enabled": true,
            "label": "layer3",
            "ip_addresses": [
              {
                "address": "10.10.1.0/31",
                "tags": [
                  {
                    "slug": "ospf_area_0"
                  },
                  {
                    "slug": "p2p"
                  }
                ]
              }
            ],
            "_custom_field_data": {
              "vrrp_group": null,
              "dhcp_helper": null,
              "vrrp_priority": null,
              "vrrp_primary_ip": null,
              "vrrp_description": null
            },
            "lag": null,
            "tagged_vlans": [],
            "untagged_vlan": null,
            "tags": [],
            "connected_interface": {
              "device": {
                "name": "pod1sw1"
              },
              "name": "GigabitEthernet0/0"
            }
          },
          {
            "name": "GigabitEthernet0/2",
            "description": "DOWNLINK POD1SW2",
            "enabled": true,
            "label": "layer3",
            "ip_addresses": [
              {
                "address": "10.10.1.2/31",
                "tags": [
                  {
                    "slug": "ospf_area_0"
                  },
                  {
                    "slug": "p2p"
                  }
                ]
              }
            ],
            "_custom_field_data": {
              "vrrp_group": null,
              "dhcp_helper": null,
              "vrrp_priority": null,
              "vrrp_primary_ip": null,
              "vrrp_description": null
            },
            "lag": null,
            "tagged_vlans": [],
            "untagged_vlan": null,
            "tags": [],
            "connected_interface": {
              "device": {
                "name": "pod1sw2"
              },
              "name": "GigabitEthernet0/0"
            }
          },
          {
            "name": "GigabitEthernet0/3",
            "description": "",
            "enabled": false,
            "label": "",
            "ip_addresses": [],
            "_custom_field_data": {
              "vrrp_group": null,
              "dhcp_helper": null,
              "vrrp_priority": null,
              "vrrp_primary_ip": null,
              "vrrp_description": null
            },
            "lag": null,
            "tagged_vlans": [],
            "untagged_vlan": null,
            "tags": [],
            "connected_interface": null
          },
          {
            "name": "GigabitEthernet0/4",
            "description": "",
            "enabled": false,
            "label": "",
            "ip_addresses": [],
            "_custom_field_data": {
              "vrrp_group": null,
              "dhcp_helper": null,
              "vrrp_priority": null,
              "vrrp_primary_ip": null,
              "vrrp_description": null
            },
            "lag": null,
            "tagged_vlans": [],
            "untagged_vlan": null,
            "tags": [],
            "connected_interface": null
          },
          {
            "name": "GigabitEthernet0/5",
            "description": "",
            "enabled": false,
            "label": "",
            "ip_addresses": [],
            "_custom_field_data": {
              "vrrp_group": null,
              "dhcp_helper": null,
              "vrrp_priority": null,
              "vrrp_primary_ip": null,
              "vrrp_description": null
            },
            "lag": null,
            "tagged_vlans": [],
            "untagged_vlan": null,
            "tags": [],
            "connected_interface": null
          },
          {
            "name": "GigabitEthernet0/6",
            "description": "",
            "enabled": false,
            "label": "",
            "ip_addresses": [],
            "_custom_field_data": {
              "vrrp_group": null,
              "dhcp_helper": null,
              "vrrp_priority": null,
              "vrrp_primary_ip": null,
              "vrrp_description": null
            },
            "lag": null,
            "tagged_vlans": [],
            "untagged_vlan": null,
            "tags": [],
            "connected_interface": null
          },
          {
            "name": "GigabitEthernet0/7",
            "description": "MGMT-INTERFACE",
            "enabled": true,
            "label": "mgmt",
            "ip_addresses": [
              {
                "address": "192.168.4.17/24",
                "tags": []
              }
            ],
            "_custom_field_data": {
              "vrrp_group": null,
              "dhcp_helper": null,
              "vrrp_priority": null,
              "vrrp_primary_ip": null,
              "vrrp_description": null
            },
            "lag": null,
            "tagged_vlans": [],
            "untagged_vlan": null,
            "tags": [],
            "connected_interface": null
          },
          {
            "name": "Loopback0",
            "description": "iBGP LOOPBACK",
            "enabled": true,
            "label": "",
            "ip_addresses": [
              {
                "address": "10.0.1.1/32",
                "tags": [
                  {
                    "slug": "ospf_area_0"
                  }
                ]
              }
            ],
            "_custom_field_data": {
              "vrrp_group": null,
              "dhcp_helper": null,
              "vrrp_priority": null,
              "vrrp_primary_ip": null,
              "vrrp_description": null
            },
            "lag": null,
            "tagged_vlans": [],
            "untagged_vlan": null,
            "tags": [],
            "connected_interface": null
          }
        ]
      }
    ]
  }
}
```
Perfect! I believe we have enough to start building out our Jinja templates based on this query, but first lets look at how to use Ansible and the Nautobot module to retrieve this data from a playbook.

The first thing we will want to do is create a new folder under our roles folder called nautobot_query, along with two sub-folders called tasks and vars. 

In the tasks folder create a file called main.yaml and build out the task similar to the following:

### roles/nautobot_query/tasks/main.yaml
```
- name: Get data from Nautobot
  networktocode.nautobot.query_graphql:
    url: "{{ nb_url }}"
    token: "{{ nb_token }}"
    validate_certs: False
    query: "{{ query_string }}"
  register: "nb_devices"

- name: Create directory if none exist
  file:
    path: querys
    state: directory
    
- name: Print to file
  copy:
    content: "{{ nb_devices | to_json }}"
    dest: "querys/{{ inventory_hostname }}.json"
```

We will make the request to the nautobot query_graphql plugin. The url, token, and validate_certs settings should be the same as what we used in Section 7. We will reference our query_string as a variable and place that file in the vars folder we created earlier. The results will be registered as a new variable called nb_devices which will create a new file that shows the results of the query so that we can reference it when building out the Jinja templates.

Create a new file under the vars folder called main.yaml and place the working query from the GraphiQL interface.

### roles/nautobot_query/vars/main.yaml
```
query {
        devices(name: "pod1r1") {
    inventory_hostname:name
    config_context
    device_role {
            slug
            }
    site{
      slug
      vlans{
        name
        vid
      }
    }
    interfaces {
            name
            description
            enabled
            label
            ip_addresses {
                address
                tags {
                slug
                }
            }
            _custom_field_data
            lag {
                name
            }
            tagged_vlans {
                vid
            }
            untagged_vlan {
                vid
            }
            tagged_vlans {
                vid
            }
            tags {
                slug
            }
      connected_interface{
        device {
          name
        }
        name
      }
            }
  }
}
```
