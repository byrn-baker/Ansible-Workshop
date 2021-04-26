## Section 6: Building tasks for the Router
<!-- {% include section5.html %} -->

We have our access switch and our core switches configured; now, we need to complete the tasks for the router. 
### Tasks
3.  (1) Router
    * Configure Layer 3 interfaces as DOWNLINKS to both core switches
      * Port Gi0/1 to Core Switch 1 with IP 10.x0.1.0/31
      * Port Gi0/2 to Core Switch 2 with IP 10.x0.1.2/31
    * Configure Loopback0 interface to facilitate iBGP protocol
      * IP 10.x.1.1/32
    * Configure OSPF to facilitate iBGP protocol
    * Configure iBGP receive advertised Users, Servers, and Guest subnets from the core switches
      * Use AS 6500x
    * Configure Port Gi0/0 with IP 24.24.x.2/24
      * The ISP ASN is 400 and the ISP IP address will be 24.24.x.1
      * Configure eBGP to advertise and Aggregate subnet from the Users, Servers, and Guest subnets 
      * Accept a default route from the ISP
    * Configure DHCP server for the Users, Servers, and Guest subnets

We can break down the above list of tasks into four roles in Ansible; BGP, DHCP server, layer3 interfaces, and OSPF. Let's knock out the three tasks that look familiar from our core switch section because there is an excellent chance we can reuse all or most of what we have already created in the BGP, layer3 interfaces, and OSPF roles. 

### Adding BGP, OSPF, l3_interfaces
Recall our work on the BGP role for the core switches we built into the Jinja template language that covered eBGP and aggregate addressing. We did that specifically to reuse the template outside of the specific core switch use case and broadened it to be used for the router's use case. So copy that core switch roles folder into a new folder under roles called routers.

Now we want to create a new variables file under our inventory/host_vars/podxr1 folder. Again we can copy over from the podxsw1 folder the bgp.yaml, l3_interface.yaml, and the ospf.yaml files to our podxr1 folder.
We will need to update these files to reflect the correct information about the podxr1 router. The significant differences in this file will be the neighbors under the ibgp grouping, the addition of the ebgp grouping, and the agg_network statements. 

bgp.yaml - location of this file should be under inventory/host_vars/podxr1
```
---
configuration:
  bgp:
    ibgp:
      l_asn: 65001
      neighbors:
        - 10.1.1.2
        - 10.1.1.3
    ebgp:
      neighbors: 
        24.24.1.1: {r_asn: 400}
    address_family_ipv4:
      agg_network: 155.1.1.0
      agg_mask: 255.255.255.0
      advertised_networks:
        155.1.1.0: {net_mask: 255.255.255.192 }
        155.1.1.64: {net_mask: 255.255.255.192 }
        155.1.1.128: {net_mask: 255.255.255.192 }
```

ospf.yaml - location of this file should be under inventory/host_vars/podxr1
```
---
configuration:
  ospf:
    instance: 1
    router_id: 10.1.1.1
```

l3_interfaces.yaml - location of this file should be under inventory/host_vars/podxr1
```
---
configuration:
  interfaces:
    l3_interfaces:
      - name: GigabitEthernet0/0
        description: "UPLINK TO INTERNET PROVIDER"
        ipv4: 24.24.1.2
        ipv4_mask: 255.255.255.0

      - name: GigabitEthernet0/1
        description: "DOWNLINK POD1SW1"
        ipv4: 10.10.1.0
        ipv4_mask: 255.255.255.254
        ospf:
          area: 0
          network: "point-to-point"

      - name: GigabitEthernet0/2
        description: "DOWNLINK POD1SW2"
        ipv4: 10.10.1.2
        ipv4_mask: 255.255.255.254
        ospf:
          area: 0
          network: "point-to-point"        

      - name: Loopback0
        description: "iBGP LOOPBACK"
        ipv4: 10.1.1.1
        ipv4_mask: 255.255.255.255
        ospf:
          area: 0
          network: "point-to-point"
```

### Adding DHCP
The last variables file that we will need is the dhcp.yaml file. This will store the information needed to configure the DHCP server on the router.

dhcp.yaml - location of this file should be under inventory/host_vars/podxr1
```
---
configuration:
  dhcp_pool:
    - name: 300
      network: "155.1.1.0/26"
      default_router: 155.1.1.1
      lease: 30
      excluded_address: "155.1.1.1 155.1.1.3"

    - name: 350
      network: "155.1.1.64/26"
      default_router: 155.1.1.65
      lease: 30
      excluded_address: "155.1.1.65 155.1.1.67"

    - name: 400
      network: "155.1.1.128/26"
      default_router: 155.1.1.129
      lease: 30
      excluded_address: "155.1.1.129 155.1.1.131"
```

dhcp_pool.j2 - location of this file should be under roles/routers/add_dhcp_pool/templates
{% raw %}
```
#jinja2: lstrip_blocks: "True (or False)", trim_blocks: "True (or False)"

{% if configuration.dhcp_pool is defined %}
{% for address in configuration.dhcp_pool %}
ip dhcp excluded-address {{ address.excluded_address }}
{% endfor %}
{% for pool in configuration.dhcp_pool %}
ip dhcp pool {{ pool.name }}
    network {{ pool.network | replace("/"," /") }}
    default-router {{ pool.default_router }}
    lease {{ pool.lease }}
{% endfor %}
{% endif %}
```
{% endraw %}

All of this looks pretty familiar from the previous Jinja templates we have created so far. Notice that under the ip dhcp pool section, we have a network statement that lists a variable to use, but a ```"|"``` has been added with the word replace. You can target specific text with Jinja to replace in the variable that you use. Why is this important? In our case, when configuring the DHCP pool on a Cisco router, you can not just place the network and its mask length with "1.1.1.0/24" it will reject this because it expects you to format it this way "1.1.1.0 /24". So we will create this space as we format it through our template. We won't have to remember that a space is even required when creating these variable files. 

main.yaml - location of this file should be under roles/routers/add_dhcp_pool/main
```
- name: configuring dhcp server on {{ inventory_hostname }}
  cisco.ios.ios_config:
    src: dhcp_pool.j2

- name: Saving the running config on {{ inventory_hostname }}
  ios_config:
    save_when: always
```

Ok we should have four new folders under the roles/routers folder now. Create a new playbook to validate everything we have just created works called pb.deploy_router.yaml.

```
- name: Configuring routers
  hosts: routers
  gather_facts: false
  connection: network_cli

  roles:
    - { role: routers/add_l3_interface }
    - { role: routers/add_ospf }
    - { role: routers/add_bgp }
    - { role: routers/add_dhcp_pool }
```

[Installing Ansible - Section 1](installing_ansible.md)

[Creating an Inventory File - Section 2](inventory_file.md)

[Creating a playbook - Section 3](first_play.md)

[Building Roles - Section 4](building_roles.md)

[Building the core switch Roles - Section 5](section5-coreswitch.md)