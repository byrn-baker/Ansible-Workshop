## Section 10: Building configuration Jinja templates
{% include section9.html %}

If you have been following along, we just finished building out the graphQL query that will pull the data we want back to Ansible. Now we will take that data and run it through Jinja templates that will create a complete device configuration. We will be using very similar approaches as sections 4, 5, and 6. The only difference is that a single playbook will be used to generate a complete configuration that should look as if you did a ```show run``` on your switch or router.

The first step will be to create a new playbook, and I've called mine ```pb.nautobot_build_full_config.yaml```. We will use two roles in this play, the first will be the nautobot_query role that we worked on in [section 9](https://www.workshop.ansible-lab.com/section9-querynautobot.html), and the second play will be the construction of the complete device configuration.

### pb.nautobot_build_full_config.yaml
```
---
- name: Query Nautobot for Device data and build full configuration
  hosts: all
  gather_facts: false
  connection: local
  
  vars:
    device: "{{inventory_hostname}}"
  roles:
  - { role: nautobot_query }
  - { role: full_configuration/build }
```

### nautobot_query role
```
### tasks/main.yaml
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

```
### vars/main.yaml
query_string: |
        query {
        devices(name: "{{device}}") {
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
                vrrp_group: cf_vrrp_group
                vrrp_description: cf_vrrp_description
                vrrp_priority: cf_vrrp_priority
                vrrp_primary_ip: cf_vrrp_primary_ip
                dhcp_helper: cf_dhcp_helper
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
This is what you will want your query role to look like. Note that we are registering the inventory_hostname as a variable called ```device``` and feeding that into the query.  Next we will put together the full_configuration role.

### full_configuration/build role
```
### full_configuration/build/tasks
- name: Configuration Assembly
  template:
    src: "cisco_ios.j2"
    dest: "configs/{{ inventory_hostname }}.conf"
```

We will use several different Jinja templates, and these templates will be called in as needed. To start will create different templates for each device in use on our pod. To ensure that each device configuration looks like a ```show run``` we will need to template the configuration with slite difference between the router and switch. This will be the only file in the root of ```full_configuration/build/templates/``` the rest will be stored inside of ```full_configuration/build/templates/ios```.
{% raw %}
```
### full_configuration/build/templates/cisco_ios.j2
#jinja2: lstrip_blocks: "True", trim_blocks: "True"
{% set devices = nb_devices["data"]["devices"] %}
{% if devices[0]["device_role"]["slug"] == "pod_l2_switch" %}
{% include "./ios/platform_templates/vios_switch.j2"%}
{% elif devices[0]["device_role"]["slug"] == "pod_l3_switch" %}
{% include "./ios/platform_templates/vios_switch.j2"%}
{% elif devices[0]["device_role"]["slug"] == "pod_router" %}
{% include "./ios/platform_templates/vios_router.j2"%}
{% endif %}
```
{% endraw %}
To help keep our variable names short I have included a set command that takes ```nb_devices["data"]["devices"]``` and shortens it to ```devices```. 

Create a new folder ```full_configuration/build/templates/ios/platform_templates``` this will store two different templates, vios_router.j2 and vios_switch.j2. This template will be used for all switches in the pod.
{% raw %}
```
### full_configuration/build/templates/ios/platform_templates/vios_switch.j2
!
version 15.2
service timestamps debug datetime msec
service timestamps log datetime msec
no service password-encryption
service compress-config
!
{% include './ios/hostname.j2' %}

boot-start-marker
boot-end-marker
!
!
vrf definition MGMT
 !
 address-family ipv4
 exit-address-family
!
!
{% include './ios/local_user.j2' %}

{% if devices[0]["config_context"]["aaa-new-model"] is defined %}
{% include './ios/aaa.j2' %}
{% else %}
no aaa new-model
{% endif %}

!
!
!
!
!
!         
!
!
{% include './ios/dns.j2' %}

ip cef
no ipv6 cef
!
!
!
spanning-tree mode rapid-pvst
spanning-tree extend system-id
!
vlan internal allocation policy ascending
{% if devices[0]["config_context"]["lldp"] == true %}
lldp run
{% endif %}
!
! 
!
!
!
!
!
!
!
!
!         
!
!
!
{% include './ios/interfaces.j2' %}

!
{% if devices[0]["config_context"]["ospf"] is defined %}
{% include './ios/ospf.j2' %}
{% endif %}
!
{% if devices[0]["config_context"]["bgp"] is defined %}
{% include './ios/bgp.j2' %}
{% endif %}
!
ip forward-protocol nd
!
!
no ip http server
no ip http secure-server
!
{% if devices[0]["config_context"]["routes"] is defined %}
{% if devices[0]["config_context"]["routes"]["static"] is defined %}
{% for static in devices[0]["config_context"]["routes"]["static"] %}
{{ static }}
{% endfor %}
{% endif %}
{% endif %}
{% if devices[0]["config_context"]["routes"]["mgmt_gateway"] is defined %}
ip route vrf MGMT 0.0.0.0 0.0.0.0 {{ devices[0]["config_context"]["routes"]["mgmt_gateway"] }}
{% endif %}
{% if devices[0]["device_role"]["slug"] == "pod_l2_switch" %}
ip ssh source-interface GigabitEthernet1/3
{% elif devices[0]["device_role"]["slug"] == "pod_l3_switch" %}
ip ssh source-interface GigabitEthernet1/3
{% elif devices[0]["device_role"]["slug"] == "pod_router" %}
ip ssh source-interface GigabitEthernet0/7
{% endif %}
ip ssh version 2
ip scp server enable
!
!
!
control-plane
!
banner exec ^C
**************************************************************************
* IOSv is strictly limited to use for evaluation, demonstration and IOS  *
* education. IOSv is provided as-is and is not supported by Cisco's      *
* Technical Advisory Center. Any use or disclosure, in whole or in part, *
* of the IOSv Software or Documentation to any third party for any       *
* purposes is expressly prohibited except as otherwise authorized by     *
* Cisco in writing.                                                      *
**************************************************************************
^C
banner incoming ^C
**************************************************************************
* IOSv is strictly limited to use for evaluation, demonstration and IOS  *
* education. IOSv is provided as-is and is not supported by Cisco's      *
* Technical Advisory Center. Any use or disclosure, in whole or in part, *
* of the IOSv Software or Documentation to any third party for any       *
* purposes is expressly prohibited except as otherwise authorized by     *
* Cisco in writing.                                                      *
**************************************************************************
^C
banner login ^C
**************************************************************************
* IOSv is strictly limited to use for evaluation, demonstration and IOS  *
* education. IOSv is provided as-is and is not supported by Cisco's      *
* Technical Advisory Center. Any use or disclosure, in whole or in part, *
* of the IOSv Software or Documentation to any third party for any       *
* purposes is expressly prohibited except as otherwise authorized by     *
* Cisco in writing.                                                      *
**************************************************************************
^C
!
{% include './ios/console_vty.j2' %}

!
end
```
{% endraw %}
When creating these templates, I will pull a running configuration and, starting from the top, replace the text for things I will want to include as their own Jinja templates. For example, at the start of this file, we have an ```{% include './ios/hostname.j2' %}``` that references a template for formating the cli text that would appear like this ```hostname pod1sw3```. Each section is pretty self-explanatory. So let's look down at the interface templates and walk through developing these.

I have split my interfaces into 4 different groupings which have their own templates. Loopback, and interfaces that are specific to the devices role in our pods network. 
{% raw %}
```
### full_configuration/build/templates/ios/interfaces.j2
{% for interface in devices[0]["interfaces"] %}
{% if 'Loop' in interface["name"] %}
{% include "./ios/interfaces/_loopback.j2" %}
{% elif devices[0]["device_role"]["slug"] == "pod_l2_switch" %}
{% include "./ios/interfaces/_switch_l2_physical.j2"%}
{% elif devices[0]["device_role"]["slug"] == "pod_l3_switch" %}
{% include "./ios/interfaces/_switch_l3_physical.j2"%}
{% elif devices[0]["device_role"]["slug"] == "pod_router" %}
{% include "./ios/interfaces/_router_physical.j2" %}
{% endif %}
{% endfor %}
```

- Loopback: In our pod design, the loopback has one purpose: to facilitate iBGP peering between the router and 2 L3 switches. So there is only one way to configure it in our design which keeps our options small. We can expand this, of course, and continue evaluating inside the loopback template if a new use case is designed. In this case, we are using tags to determine if this interface will be included in OSPF and the type of interface in OSPF it should be (Point to Point or broadcast). This will be common across all L3 interfaces in our templates.

{% raw %}
```
### full_configuration/build/templates/ios/interfaces/_loopback.j2
interface {{ interface["name"] }}
{% if interface["description"] | length > 1 %}
 description {{ interface["description"] }}
{% endif %}
{% if interface.ip_addresses | length > 0 %}
{% for addr in interface.ip_addresses %}
{% if addr.address is defined %}
 ip address {{ addr.address | ipaddr('address') }} {{ addr.address | ipaddr('netmask') }}
{% for tags in interface.ip_addresses[0].tags %}
{% if tags.slug is defined %}
{% if 'p2p' and 'ospf' in tags.slug %}
 ip ospf {{ devices[0].config_context.ospf.id }} area {{ tags.slug|replace("ospf_area_","") }}
 ip ospf network point-to-point
{% else %}
{% endif %}
{% endif %}
{% endfor %}
{% endif %}
{% endfor %}
!
{% else %}
 no ip address  
{% endif %}
{% if interface["enabled"] == false %}
 shutdown
{% endif %}
```
{% endraw %}

- pod_l2_switch: In our pod's network design, we have four types of interfaces that will be considered for configuration on a layer 2 (access) switch. In my template, I evaluate the data coming from Nautobot in the below order. I am also using the interface Labels in Nautobot to tell my templates the type of interface it should be (access, trunk, or layer3).
  1. Access interface:  if the port is has a label of access and enabled, then configure it as an access port.
  2. Trunk interface: else, if the port is has a label of trunk and is enabled, then configure it as a trunk port. 
     For allowed VLANs on trunks ports, we do not want to loop through each one because we will not be able to cleanly place them in the format cisco required (switch trunk allowed vlan 1,4,6). Instead, we need to join these different VLANs to match the correct cli structure. What is cool with Jinja is you can do this with a join statement and pulling a specific attribute from the list of tagged VLANs in the nautobot query.
  3. Management interface: else, if the port has a label mgmt, then configure it as a management port.
     Nothing special here, just including the port in the MGMT vrf and supplying it with an IP address. 
  4. Not used interface: else, if nothing matches above, then configure the put as an unused port and shut it down. 

{% raw %}
```
### full_configuration/build/templates/ios/interfaces/_switch_l2_physical.j2
{% if interface["label"] == "access" and interface["enabled"] == true %}
interface {{ interface["name"] }}
{% if interface["description"] is defined %}
 description {{ interface["description"] }}    
{% endif %}
 switchport mode access
 switchport access vlan {{ interface["untagged_vlan"]["vid"] }}
 spanning-tree portfast edge
 no cdp enable
 no shut 
 !
{% elif interface["label"] == "trunk" and interface["enabled"] == true %}
interface {{ interface["name"] }}
{% if interface["description"] is defined %}
 description {{ interface["description"] }}
{% endif %}
{% if interface["untagged_vlan"]["vid"] is defined %}
 switchport trunk native vlan {{ interface.untagged_vlan.vid }}
{% endif %}
{% if interface["tagged_vlans"][0]["vid"] is defined %}
 switch trunk allowed vlan {{ interface["tagged_vlans"] | join(',', attribute='vid') }}
{% endif %}
 switchport trunk encapsulation dot1q
 switchport mode trunk 
{% if interface['lag']["name"] is defined %}
 channel-group {{ interface['lag']["name"] | replace ('Port-Channel', '') }} mode active 
{% endif %}
 no shut  
 !
{% elif interface["label"] == "mgmt" %}
interface {{ interface["name"] }}
{% if interface["description"] is defined %}
 description {{ interface["description"] }}    
{% endif %}
 no switchport
 vrf forwarding MGMT
{% if interface["ip_addresses"] | length > 0 %}
{% for addr in interface["ip_addresses"] %}
{% if addr["address"] is defined %}
 ip address {{ addr["address"] | ipaddr('address') }} {{ addr["address"] | ipaddr('netmask') }}
 negotiation auto
 no cdp enable
 no shutdown
{% endif %}
{% endfor %}
{% endif %}
{% else %}
interface {{ interface["name"] }}
 description NOT IN USE
 negotiation auto
 shutdown
{% endif %}
```
{% endraw %}

- pod_l3_switch: In our pods network design we have 7 types of interfaces that will be considered for configuration on a layer 3 (core) switch. In my template I evaluate the data coming from Nautobot in the below order. Again using the interface Labels in Nautobot to tell my templates the type of interface it should be (access, trunk, or layer3).
  1. Access interface:  if the port is has a label of access and enabled, then configure it as an access port.
  2. Trunk interface: else, if the port is has a label of trunk and is enabled, then configure it as a trunk port. 
     For allowed VLANs on trunks ports, we do not want to loop through each one because we will not be able to cleanly place them in the format cisco required (switch trunk allowed vlan 1,4,6). Instead, we need to join these different VLANs to match the correct cli structure. What is cool with Jinja is you can do this with a join statement and pulling a specific attribute from the list of tagged VLANs in the nautobot query.
  3. Management interface: else, if the port has a label mgmt, then configure it as a management port.
     Nothing special here, just including the port in the MGMT vrf and supplying it with an IP address. 
  4. Not used interface: else, if nothing matches above, then configure the put as an unused port and shut it down. 



{% raw %}
```
### full_configuration/build/templates/ios/interfaces/_switch_l3_physical.j2
{% if interface["label"] == "access" and interface["enabled"] == true and 'GigabitEthernet' in interface["name"] %}
interface {{ interface["name"] }}
        {% if interface["description"] is defined %}
 description {{ interface["description"] }}
        {% endif %}
 switchport mode access
 switchport access vlan {{ interface["untagged_vlan"]["vid"] }}
 spanning-tree portfast edge
 no cdp enable
 no shut
 !
{% elif interface["label"] == "trunk" and interface["enabled"] == true and 'GigabitEthernet' in interface["name"] %}
interface {{ interface["name"] }}
        {% if interface["description"] is defined %}
 description {{ interface["description"] }}
        {% endif %}
        {% if interface["untagged_vlan"]["vid"] is defined %}
 switchport trunk native vlan {{ interface["untagged_vlan"]["vid"] }}
        {% endif %}
        {% if interface["tagged_vlans"][0]["vid"] is defined %}
 switch trunk allowed vlan {{ interface["tagged_vlans"] | join(',', attribute='vid') }}
        {% endif %}
 switchport trunk encapsulation dot1q
 switchport mode trunk 
        {% if interface["lag"]["name"] is defined %}
 channel-group {{ interface["lag"]["name"] | replace ('Port-Channel', '') }} mode active 
        {% endif %}
 no shut
 !
{% elif interface["label"] == "trunk" and interface["enabled"] == true and 'Port-Channel' in interface["name"] %}
interface {{ interface["name"] }}
        {% if interface["description"] is defined %}
 description {{ interface["description"] }}
        {% endif %}
        {% if interface["untagged_vlan"]["vid"] is defined %}
 switchport trunk native vlan {{ interface["untagged_vlan"]["vid"] }}
        {% endif %}
        {% if interface["tagged_vlans"][0]["vid"] is defined %}
 switch trunk allowed vlan {{ interface["tagged_vlans"] | join(',', attribute='vid') }}
        {% endif %}
 switchport trunk encapsulation dot1q
 switchport mode trunk
 no shut
 !
{% elif interface["label"] == "layer3" and interface["enabled"] == true and 'GigabitEthernet' in interface["name"] %}
interface {{ interface["name"]["split"]('.')[0] }}
        {% if interface["description"] is defined %}
 description {{ interface["description"] }}
        {% endif %}
 no switchport
        {% if interface["ip_addresses"] | length > 0 %}
            {% for addr in interface["ip_addresses"] %}
                {% if addr["address"] is defined %}
 ip address {{ addr["address"] | ipaddr('address') }} {{ addr["address"] | ipaddr('netmask') }}
                    {% for tags in interface["ip_addresses"][0]["tags"] %}
                        {% if tags["slug"] is defined %}
                            {% if 'ospf' in tags["slug"] %}
 ip ospf {{ devices[0]["config_context"]["ospf"]["id"] }} area {{ tags["slug"]|replace("ospf_area_","") }}
                            {% endif %}
                            {% if 'p2p' in tags["slug"] %}
 ip ospf network point-to-point
                            {% endif %}
                        {% endif %}
                    {% endfor %}
                {% endif %}
            {% endfor %}
        {% endif %}
        {% if devices[0]["config_context"]["acl"] is defined %}
            {% if devices[0]["config_context"]["acl"]["interfaces"][interface["name"]] is defined %}
ip access-group {{ devices[0]["config_context"]["acl"]["interfaces"][interface["name"]]["acl"] }} {{ devices[0]["config_context"]["acl"]["interfaces"][interface["name"]]["direction"] }}
            {% endif %}
        {% endif %}
        {% if interface["dhcp_helper"] %}
 ip helper-address {{ interface["dhcp_helper"] }}
        {% endif %}
        {% if interface["dhcp_helper"] %}
 vrrp {{ interface.vrrp_group }} ip {{ interface.vrrp_primary_ip }}
 vrrp {{ interface.vrrp_group }} description {{ interface.vrrp_description }}
 vrrp {{ interface.vrrp_group }} priority {{ interface.vrrp_priority }}
 vrrp {{ interface.vrrp_group }} timers learn
        {% endif %}
 no shut
 !
{% elif interface["label"] == "layer3" and interface["enabled"] == true and 'vlan' in interface["name"] %}
interface {{ interface.name.split('.')[0] }}
        {% if interface.description is defined %}
 description {{ interface.description }}
        {% endif %}
        {% if interface.ip_addresses | length > 0 %}
            {% for addr in interface.ip_addresses %}
                {% if addr.address is defined %}
 ip address {{ addr.address | ipaddr('address') }} {{ addr.address | ipaddr('netmask') }}
                    {% for tags in interface.ip_addresses[0].tags %}
                        {% if tags.slug is defined %}
                            {% if 'ospf' in tags.slug %}
 ip ospf {{ devices[0].config_context.ospf.id }} area {{ tags.slug|replace("ospf_area_","") }}
                            {% endif %}
                            {% if 'p2p' in tags.slug%} 
 ip ospf network point-to-point
                            {% endif %}     
                            {% else %}
                        {% endif %}
                    {% endfor %}
                {% endif %}
            {% endfor %}
        {% else %}
        {% endif %}
        {% if devices[0]["config_context"]["acl"] is defined %}
            {% if devices[0]["config_context"]["acl"]["interfaces"][interface["name"]] is defined %}
ip access-group {{ devices[0]["config_context"]["acl"]["interfaces"][interface["name"]]["acl"] }} {{ devices[0]["config_context"]["acl"]["interfaces"][interface["name"]]["direction"] }}
            {% endif %}
        {% endif %}
        {% if interface.dhcp_helper %}
 ip helper-address {{ interface.dhcp_helper }}
        {% endif %}
        {% if interface["vrrp_group"] %}
 vrrp {{ interface["vrrp_group"] }} ip {{ interface["vrrp_primary_ip"] }}
 vrrp {{ interface["vrrp_group"] }} description {{ interface["vrrp_description"] }}
 vrrp {{ interface["vrrp_group"] }} priority {{ interface["vrrp_priority"] }}
 vrrp {{ interface["vrrp_group"] }} timers learn
        {% else %}
        {% endif %}
 no shut
 !
{% elif interface["label"] == "mgmt" %}
interface {{ interface["name"] }}
    {% if interface["description"] is defined %}
 description {{ interface["description"] }}
    {% endif %}
 no switchport
 vrf forwarding MGMT
    {% if interface["ip_addresses"] | length > 0 %}
        {% for addr in interface["ip_addresses"] %}
            {% if addr["address"] is defined %}
 ip address {{ addr["address"] | ipaddr('address') }} {{ addr["address"] | ipaddr('netmask') }}
 negotiation auto
 no cdp enable
 no shutdown
 !
            {% endif %}
        {% endfor %}
    {% endif %}
{% else %}
interface {{ interface["name"] }}
 description NOT IN USE
 negotiation auto
 shutdown
 !
{% endif %}
```
{% endraw %}













[Installing Ansible - Section 1](installing_ansible.md)

[Creating an Inventory File - Section 2](inventory_file.md)

[Creating a playbook - Section 3](first_play.md)

[Building Roles - Section 4](building_roles.md)

[Building the core switch Roles - Section 5](section5-coreswitch.md)

[Building the router Roles - Section 6](section6-router.md)

[Introducing Nautobot - Section 7](section7-nautobot.md)

[Introducing PyNautobot - Section 8](section8-pynautobot.md)

[Querying your device data from nautobot - Section 9](section9-querynautobot.md)