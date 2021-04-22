## Section 5: Building tasks for the core switches
{% include section5.html %}
We have built out several tasks for configuring the access switches; now, it is time to move on to our core switch configuration tasks. You will remember that two of the configuration tasks for the core switches are to create VLANs and layer2 trunking interfaces. Because these tasks are the same on the access switches as the core switches, we can copy those roles from the access switch to the core switch roles folder. In part, this is a significant benefit to automation with tools like Ansible.

Let us address our host_vars files for our core switches. These files are essential as they will contain all of the information required to configure our pod. We should have created folders called host_vars under our inventory directory, which contains folders for each of our devices in the pod. Copy the vlans.yaml and trunk_interfaces.yaml files from your podxsw3 host_vars folder and place those into both the podxsw1 and podxsw2 folders. We will maintain the same structure in the YAML file and update the interfaces for our core switches. 

Our vlans.yaml should look exactly the same in all three of our switches
```
---
configuration:
  vlans:
    vlan:
      - name: "USERS"
        vlan_id: "300"

      - name: "SERVERS"
        vlan_id: "350"

      - name: "GUEST"
        vlan_id: "400"

      - name: "NATIVE_VLAN"
        vlan_id: "666"
```

Our trunk_interfaces.yaml will look similar to podxsw3 with just the descriptions and interfaces updated to reflect this side of the core switch connections.
Here is podxsw1 as an example:
```
---
configuration:
  interfaces:
    trunk:
      - name: Gi0/1
        description: "TRUNK TO POD1SW2"
        interface_mode: trunk
        native_vlan:
          members: "666"
        allowed_vlans:
            members: "300,350,400"
        port_channel: 12    

      - name: Gi0/2
        description: "TRUNK TO POD1SW2"
        interface_mode: trunk
        native_vlan:
          members: "666"
        allowed_vlans:
            members: "300,350,400"
        port_channel: 12

      - name: po12
        description: "TRUNK TO POD1SW2"
        interface_mode: trunk
        native_vlan:
          members: "666"
        allowed_vlans:
            members: "300,350,400"  

      - name: Gi0/3
        description: "TRUNK TO POD1SW3"
        interface_mode: trunk
        native_vlan:
          members: "666"
        allowed_vlans:
            members: "300,350,400"
```
One change you will notice between the podxsw3 and podxsw1 and podxsw2 is we have added a port channel to some of the interfaces. When building the add_trunk_interface template in Jinja for our trunk ports, you will recall an if statement for a channel group. When thinking through your Jinja templates, it is a good idea to think through the different combinations of ways the interfaces could be configured. Sometimes, it is possible to catch a lot of the caveats and create a template for those; this enables you to easily reuse templates in different scenarios and avoid having to redo similar work down the road. Cisco switch port channels will inherit the configuration of the individual interfaces; however, it is good practice to keep those interface configurations the same. The interface name "po12" will allow our jinja template to iterate and configure that interface as well. 

bgp.yaml - location of this file should be under inventory/host_vars/podxsw1
```
---
configuration:
  bgp:
    ibgp:
      l_asn: 65001
      neighbors:
        - 10.1.1.1
        - 10.1.1.3
    address_family_ipv4:
      advertised_networks:
        155.1.1.0: {net_mask: 255.255.255.192 }
        155.1.1.64: {net_mask: 255.255.255.192 }
        155.1.1.128: {net_mask: 255.255.255.192 }
```
add_bgp.j2 - location of this file should be under roles/core_switch/add_bgp/templates
{% raw %}
```
#jinja2: lstrip_blocks: "True (or False)", trim_blocks: "True (or False)"

{% if configuration.bgp is defined %}
router bgp {{ configuration.bgp.ibgp.l_asn }}
  bgp router-id {{ configuration.ospf.router_id }}
  {% for ibgp_peers in configuration.bgp.ibgp.neighbors %}
  neighbor {{ ibgp_peers }} remote-as {{ configuration.bgp.ibgp.l_asn }}
  neighbor {{ ibgp_peers }} update-source Loopback0
  {% endfor%}
  {% if configuration.bgp.ebgp is defined %}
    {% for ebgp_peers,ebgp_peers_attr in configuration.bgp.ebgp.neighbors.items() %}
  neighbors {{ ebgp_peers }} remote-as {{ ebgp_peers_attr.r_asn }}
    {% endfor %}
  {% endif %}
  address-family ipv4
  {% for ibgp_peers in configuration.bgp.ibgp.neighbors %}
   neighbor {{ ibgp_peers }} activate
   neighbor {{ ibgp_peers }} next-hop-self
  {% endfor %}
  {% if configuration.bgp.ebgp.neighbors is defined %}
    {% for ebgp_peers,ebgp_peers_attr in configuration.bgp.ebgp.neighbors.items() %}
   neighbor {{ ebgp_peers }} activate
    {% endfor%}
  {% endif %}
  {% if configuration.bgp.address_family_ipv4.advertised_networks is defined %}
    {% for adv_nets,adv_nets_attr in configuration.bgp.address_family_ipv4.advertised_networks.items() %}
   network {{ adv_nets }} mask {{ adv_nets_attr.net_mask }} 
    {% endfor %}
    {% if configuration.bgp.address_family_ipv4.agg_network is defined %}
   aggregate-address {{ configuration.bgp.address_family_ipv4.agg_network }} {{ configuration.bgp.address_family_ipv4.agg_mask }} summary-only
    {% endif %}  
  {% endif %}
  exit-address-family
{% endif %}
```
{% endraw %}
ospf.yaml - location of this file should be under inventory/host_vars/podxsw1
```
---
configuration:
  ospf:
    instance: 1
    router_id: 10.1.1.2
```
add_ospf.j2 - location of this file should be under roles/core_switch/add_ospf/templates
{% raw %}
```
#jinja2: lstrip_blocks: "True (or False)", trim_blocks: "True (or False)"
{#- ---------------------------------------------------------------------------------- #}
{# configuration.ospf                                                                  #}
{# ---------------------------------------------------------------------------------- -#}
{% if configuration.ospf is defined %}
router ospf {{ configuration.ospf.instance }}
    router-id {{ configuration.ospf.router_id }}
    passive-interface Loopback 0
{% endif %}
```
{% endraw %}
l3_interfaces.yaml - location of this file should be under inventory/host_vars/podxsw1
```
---
configuration:
  interfaces:
    l3_interfaces:
      - name: vlan300
        description: "USER_SVI"
        ipv4: 155.1.1.2
        ipv4_mask: 255.255.255.192
        dhcp_helper: 10.0.1.1
        vrrp_group: 1
        vrrp_description: USER_VLAN
        vrrp_priority: 200
        vrrp_primary_ip: 155.1.1.1

      - name: vlan350
        description: "SERVER_SVI"
        ipv4: 155.1.1.66
        ipv4_mask: 255.255.255.192
        dhcp_helper: 10.0.1.1
        vrrp_group: 2
        vrrp_description: USER_VLAN
        vrrp_priority: 200
        vrrp_primary_ip: 155.1.1.65

      - name: vlan400
        description: "GUEST_SVI"
        ipv4: 155.1.1.130
        ipv4_mask: 255.255.255.192
        dhcp_helper: 10.0.1.1
        vrrp_group: 3
        vrrp_description: GUEST_VLAN
        vrrp_priority: 200
        vrrp_primary_ip: 155.1.1.129

      - name: GigabitEthernet0/0
        description: "UPLINK POD1R1"
        ipv4: 10.10.1.1
        ipv4_mask: 255.255.255.254
        ospf:
          area: 0
          network: "point-to-point"

      - name: Loopback0
        description: "iBGP LOOPBACK"
        ipv4: 10.1.1.2
        ipv4_mask: 255.255.255.255
        ospf:
          area: 0
          network: "point-to-point"
```
add_l3_interfaces.j2 - location of this file should be under roles/core_switch/add_l3_interfaces/templates
{% raw %}
```
#jinja2: lstrip_blocks: "True (or False)", trim_blocks: "True (or False)"

{% if configuration.interfaces.l3_interfaces is defined %}
  {% for l3_interface in configuration.interfaces.l3_interfaces %}
    {% if 'Loopback0' in l3_interface.name %}
interface {{ l3_interface.name }}
      {% if l3_interface.description is defined %}
 description {{ l3_interface.description}}
      {% endif %}
 ip address {{ l3_interface.ipv4 }} {{ l3_interface.ipv4_mask }}
      {% if l3_interface.ospf is defined %}
 ip ospf network {{ l3_interface.ospf.network }}
 ip ospf {{ configuration.ospf.instance }} area {{ l3_interface.ospf.area }}
      {% endif %}
 no shut     
    {% elif 'GigabitEthernet' in l3_interface.name and l3_interface.ospf is defined %}
interface {{ l3_interface.name }}
 no switchport
       {% if l3_interface.description is defined %}
 description {{ l3_interface.description }}
       {% endif %}
 ip address {{ l3_interface.ipv4 }} {{ l3_interface.ipv4_mask }}
 ip ospf network {{ l3_interface.ospf.network }}
 ip ospf {{ configuration.ospf.instance }} area {{ l3_interface.ospf.area }}
 no shut   
    {% elif 'vlan' in l3_interface.name and l3_interface.vrrp_group is defined %}
interface {{ l3_interface.name }}
      {% if l3_interface.description is defined %}
 description {{ l3_interface.description}}
      {% endif %}
 ip address {{ l3_interface.ipv4 }} {{ l3_interface.ipv4_mask }}
 no shut
      {% if l3_interface.dhcp_helper is defined %}
 ip helper-address {{ l3_interface.dhcp_helper }}
      {% endif %}
 vrrp {{ l3_interface.vrrp_group }} ip {{ l3_interface.vrrp_primary_ip }}
 vrrp {{ l3_interface.vrrp_group }} description {{ l3_interface.vrrp_description }}
 vrrp {{ l3_interface.vrrp_group }} priority {{ l3_interface.vrrp_priority }}
 vrrp {{ l3_interface.vrrp_group }} timers learn
    {% else %}
interface {{ l3_interface.name }}
      {% if l3_interface.description is defined %}
 description {{ l3_interface.description}}
      {% endif %}
 ip address {{ l3_interface.ipv4 }} {{ l3_interface.ipv4_mask }}
 no shut   
    {% endif %}
  {% endfor %}
{% endif %}
```
{% endraw %}
Once you have these roles and variables completed we will need to create our playbook. 

Create a new file under your main project folder Ansible_Workshop and name it pb.setup_core_switches.yaml

```
- name: Configuring core switches
  hosts: core_switches
  gather_facts: false
  connection: network_cli
  
  roles:
    - { role: core_switch/add_vlan }
    - { role: core_switch/add_trunk_interface }
    - { role: core_switch/add_l3_interface }
    - { role: core_switch/add_ospf }
    - { role: core_switch/add_bgp }
```

The previous playbook targeted one switch to connect to; this time, we have two devices to configure. We can use the group name of the switches to target multiple devices with Ansible. So, in this case, our hosts are "core_switches" to match our grouping in the inventory file we are using. Everything else in the playbook is pretty much the same as before, except, of course, our Roles location has changed. Remember that each folder created in your roles/core_switch folder should contain two folders inside, "tasks" and "templates." Above, we showed examples of the host variables and the Jinja templates, be sure to add your tasks/main.yaml to each new role created.

[Installing Ansible - Section 1](installing_ansible.md)

[Creating an Inventory File - Section 2](inventory_file.md)

[Creating a playbook - Section 3](first_play.md)

[Building Roles - Section 4](building_roles.md)
