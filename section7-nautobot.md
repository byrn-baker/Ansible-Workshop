## Section 7: Introducing a source of truth to our Ansible workflow 
{% include section7.html %}

We have built out our roles to deploy our pod. Now lets take a look at how we can replace all of the group_vars, host_vars, and inventory folders and files with a database. To do this we will take a look at a tool called [Nautobot](https://www.networktocode.com/nautobot/)

### What is Nautobot?
*At its core, Nautobot is a Source of Truth that defines the intended state of the network. Throw away those spreadsheets and deploy a trusted source of data that enables good data hygiene. Nautobot enables strict adherence to data standards allowing users to define business rules on the network data that is stored within Nautobot. Nautobot also allows organizations to define custom fields and their own unique relationships between data stored in Nautobot showcasing its flexibility.*

I hope that helps, the basics are its a web app on top of a database that allows us to visualize the placement and locations of our hardware along with the ability to trace out and document the connections between them. The reason we will be working with it:
1. It's open source
2. Network to code (NTC) actively develops this project
3. There is robust support for Ansible and Python to query for data stored in Nautobot

### Setup Nautbot
NTC provides a couple of  ways for us to set this tool up. We can use a [docker](https://hub.docker.com/r/networktocode/nautobot-lab) container, or follow the [docs](https://nautobot.readthedocs.io/en/latest/) and install it on a Linux VM. 

For our demonstration purposes we will be using the docker container. Following these [instruction](https://github.com/nautobot/nautobot-lab) get it up and running. We will not need to load the mock data as we will be creating our own data to match our pod deployment. Create a super user from within the docker container, once that is done we should be good to start using Nautobot. Assuming you are running the container on your local machine navigate your browser to localhost:8000

### Building the data into Nautobot
Now that we have Nautobot running, we want to start filling it with the relevant data we created during our previous sections deploying the pod from Ansible.  Nautobot provides multiple options for importing data into the tool. You can import via CSV structure, you can use the Ansible module, or you can use pynautobot. We will continue to use Ansible for our demonstration and push the required data into Nautobot with its Ansible module.

Let's talk about the data requirements are in Nautobot:
1. Token that is used for the API calls 
2. Site for our pod.
3. Rack that will reside at our site.
4. Manufacturer of the equipment installed at this site.
5. Device Type of the equipment associated to the manufacturer
6. Platform (OS) that the device type will be using (ios, iosxr, junos, etc)
7. Device roles that will group the devices together (router, l3 switch, l2 switch, etc)


After all of this has been created we can start adding the specific devices to our site and installed into our rack. You will need to generate a token, to do that you will want to navigate to https://localhost:8000 and login with your super user account created when you setup the container. On the top right you will see your super user name. When you click the name you are presented with a dropdown menu that contains profile, admin, and log out.
<img src="/assets/images/nautobot_admin_panel.PNG" alt="">
<img src="/assets/images/nautobot_admin_panel_2.PNG" alt="">
Click the admin button. This will take you to a new admin page and you will see under USERS there is a button to add Tokens.
<img src="/assets/images/nautobot_admin_panel_3.PNG" alt=""> 
This token will be used in our Ansible playbooks to interact with the Nautobot API. Because we went through the trouble of creating all of these variables, it seems a waste to not come up with a way to automate the data entry of Nautobot. 

#### Creating the Ansible playbooks for data creation in Nautobot
The Ansible module for Nautobot is detailed [here](https://nautobot-ansible.readthedocs.io/en/latest/index.html) and provides installation instruction and examples for how to construct the playbooks that will interact with Nautobot.

Our first playbook will focus on generating the site within Nautobot. With Nautobot, there is term "slug". This normalizes the data you are entering to ensure there is no camel casing and ensure when we request the data it will not be incorrectly called back because of a capitalized character. Take care to not use dashes because Ansible interprets it as a subtraction. For example, pod-router as a grouping will cause Ansible to complain that the '-' is unacceptable, instead use pod_router and avoid '-' in your variables. 


Lets make a folder under inventory called nautobot_vars. We will store the variable called in our nautobot playbooks. Let us also make a new folder under roles called ```roles/create_load_file/site``` and inside of this folder create your tasks and templates folders. Inside of the tasks folder we will again create main.yaml, and inside of templates lets call our jinja template site_load.j2. We will also want a playbook to run the two tasks we will be making, let us name it pb.build_nautobot_load_files.yaml.

pb.build_nautobot_load_files.yaml:

{% raw %}
```
# requires ansible-galaxy collection install networktocode.nautobot & pip3 install pynautobot
---
- name: "Setup Nautobot"
  hosts: localhost
  connection: local
  gather_facts: False
  
  vars_files:
   - inventory/nautobot_vars/site.yaml
   - inventory/nautobot_vars/tags.yaml
   - inventory/nautobot_vars/vrfs.yaml
   - inventory/nautobot_vars/devices.yaml
   - inventory/nautobot_vars/node_design.yaml

  roles:
  - { role: load_nautobot/create_site }
  - { role: load_nautobot/create_rack }
  - { role: load_nautobot/create_vlans }
  - { role: load_nautobot/create_vrfs }
  - { role: load_nautobot/create_prefixes }
  - { role: load_nautobot/create_manufacturer }
  - { role: load_nautobot/create_platform }
  - { role: load_nautobot/create_device_types }
  - { role: load_nautobot/create_device_roles }
  - { role: load_nautobot/create_devices }
  - { role: load_nautobot/create_access_interfaces }
  - { role: load_nautobot/create_trunk_interfaces }
  - { role: load_nautobot/create_lag_interfaces }
  - { role: load_nautobot/create_l3_interfaces }
  - { role: load_nautobot/create_disabled_interfaces }
  - { role: load_nautobot/assign_ipv4_to_interfaces }
  - { role: load_nautobot/create_tags }
```
{% endraw %}


We will import a few host_vars that can be used to generate the site.yaml file

roles/create_load_file/site/tasks/main.yaml:

```
---
- name: Building File to load nautobot
  template: 
    src: "site_load.j2"
    dest: "inventory/nautobot_vars/site.yaml"
```

We will dump this data under inventory/nautobot_vars/


roles/create_load_file/site/templates/site_load.j2:

{% raw %}
```
sites:
- name: {{ ansible_user | upper }}
  status: Active
  asn: {{ configuration.bgp.ibgp.l_asn }}
  time_zone: "America/Denver"
  description: "Ansible Workshop for POD1"
  physical_address: "Denver, CO, 80209"
  shipping_address: "Denver, CO, 80209"
  latitude: "39.764518"
  longitude: "-104.995535"
  contact_name: Joe
  contact_phone: "867-5309"
  contact_email: "joe@pod1.com"
  slug: {{ ansible_user }}
  comments: "### Placeholder"
  racks:
  - name: "pod1_rr_1"
    status: active
  vlans:
{% for vlan in configuration.vlans.vlan %}
  - name: {{ vlan.name }}
    vid: {{ vlan.vlan_id }}
    status: active
    {% for interface in configuration.interfaces.l3_interfaces %}
        {% if interface.name | replace('vlan','') == vlan.vlan_id %}
        {% set prfx = interface.vrrp_primary_ip+'/'+interface.ipv4_mask %}
    prefix: {{ prfx | ipaddr('network/prefix')}}
        {% endif %}
    {% endfor %}
{% endfor %}      
  int_prefixes:
  - prefix: 10.10.1.0/31
    description: "R1-GI0/1 - SW1-GI0/0"
  - prefix: 10.10.1.2/31
    description: "R1-GI0/2 - SW2-GI0/0"
  - prefix: 24.24.1.0/24
    description: "R1-GI0/0 - INTERNET"
```    
{% endraw %}


We should end up with a file like this:

```
sites:
- name: POD1
  status: Active
  asn: 65001
  time_zone: "America/Denver"
  description: "Ansible Workshop for POD1"
  physical_address: "Denver, CO, 80209"
  shipping_address: "Denver, CO, 80209"
  latitude: "39.764518"
  longitude: "-104.995535"
  contact_name: Joe
  contact_phone: "867-5309"
  contact_email: "joe@pod1.com"
  slug: pod1
  comments: "### Placeholder"
  racks:
  - name: "pod1_rr_1"
    status: active
  vlans:
  - name: USERS
    vid: 300
    status: active
    prefix: 155.1.1.0/26
  - name: SERVERS
    vid: 350
    status: active
    prefix: 155.1.1.64/26
  - name: GUEST
    vid: 400
    status: active
    prefix: 155.1.1.128/26
  - name: NATIVE_VLAN
    vid: 666
    status: active
      
  int_prefixes:
  - prefix: 10.10.1.0/31
    description: "R1-GI0/1 - SW1-GI0/0"
  - prefix: 10.10.1.2/31
    description: "R1-GI0/2 - SW2-GI0/0"
  - prefix: 24.24.1.0/24
    description: "R1-GI0/0 - INTERNET"
```

Next create another folder under ```roles/create_load_file/node_design``` with your tasks and template folders. Inside the main.yaml file we will template out 3 files that use our host_vars to generate a device_list.

```
---
- name: Building File to load nautobot
  template: 
    src: "node_design_load.j2"
    dest: "inventory/nautobot_vars/{{inventory_hostname}}_node_design.yaml"
```

In the templates folder put a jinja file called node_design_load.j2

{% raw %}
```
#jinja2: lstrip_blocks: "True", trim_blocks: "True"
device_list:
  - name: {{ inventory_hostname }}
  {% if inventory_hostname == 'pod1r1'%}
    device_type: vios_router
    device_role: pod_router
  {% elif inventory_hostname == 'pod1sw1' or 'pod1sw2' %}
    device_type: vios_switch
    device_role: pod_core_switch
  {% elif inventory_hostname == 'pod1sw3' %}
    device_type: vios_switch
    device_role: pod_access_switch
  {% endif %}
    site: pod1
    rack: "pod1_rr_1"
    {% if inventory_hostname == 'pod1r1' %}
    position: 42
    {% elif inventory_hostname == 'pod1sw1' %}
    position: 40
    {% elif inventory_hostname == 'pod1sw2' %}
    position: 38
    {% elif inventory_hostname == 'pod1sw3' %}
    position: 36
    {% endif %}
    face: front
    status: active
    {% if configuration.interfaces.l3_interfaces is defined %}
    l3_interfaces:
    {% for interface in configuration.interfaces.l3_interfaces %}
      - name: {{ interface.name }}
        description: {{ interface.description }}
        {% if 'Loop' in interface.name %}
        type: virtual
        {% elif 'vlan' in interface.name %}
        type: virtual
        {% elif 'Gig' in interface.name %}
        type: 1000base-t
        {% endif %}
        enabled: True
        mtu: 1500
        mgmt_only: False
        {% if inventory_hostname == 'pod1r1' and interface.name == 'GigabitEthernet0/1' %}
        bside_device: pod1sw1
        bside_interface: GigabitEthernet0/0
        {% endif %}
        {% if inventory_hostname == 'pod1r1' and interface.name == 'GigabitEthernet0/2' %}
        bside_device: pod1sw2
        bside_interface: GigabitEthernet0/0
        {% endif %}
        {% set prfx = interface.ipv4+'/'+interface.ipv4_mask %}
        ipv4_address: {{ prfx | ipaddr('host/prefix')}}
        vrf: global
        status: active
        {% if interface.ospf is defined %}
        tags: 
            {% if interface.ospf.area is defined %}
        - ospf_area_{{ interface.ospf.area }}
            {% endif %}
            {% if interface.ospf.network is defined %}
        - p2p
            {% endif %}
        {% endif %}
        {% if interface.dhcp_helper is defined %}
        dhcp_helper: {{ interface.dhcp_helper }}
        {% endif %}
        {% if interface.vrrp_group is defined %}
        vrrp_group: {{ interface.vrrp_group }}
        vrrp_description: {{ interface.vrrp_description }}
        vrrp_priority: {{ interface.vrrp_priority }}
        vrrp_primary_ip: {{ interface.vrrp_primary_ip }}
        {% endif %}
    {% endfor %}
    {% endif %}
    {% if inventory_hostname == 'pod1r1' %}
      - name: GigabitEthernet0/7
        description: MGMT-INTERFACE
        type: 1000base-t
        label: mgmt
        enabled: True
        mtu: 1500
        mgmt_only: True
        ipv4_address: {{ ansible_host }}/24
        vrf: MGMT
        status: active
        primary: true
    {% elif inventory_hostname == 'pod1sw1' or inventory_hostname == 'pod1sw2' %}
      - name: GigabitEthernet1/3
        description: MGMT-INTERFACE
        type: 1000base-t
        label: mgmt
        enabled: True
        mtu: 1500
        mgmt_only: True
        ipv4_address: {{ ansible_host }}/24
        vrf: MGMT
        status: active
        primary: true
    {% elif inventory_hostname == 'pod1sw3' %}
    l3_interfaces:
      - name: GigabitEthernet1/3
        description: MGMT-INTERFACE
        type: 1000base-t
        label: mgmt
        enabled: True
        mtu: 1500
        mgmt_only: True
        ipv4_address: {{ ansible_host }}/24
        vrf: MGMT
        status: active
        primary: true
      {% endif %}
    {% if configuration.interfaces.trunk is defined %}
    trunk_interfaces:
      {% for interface in configuration.interfaces.trunk %}
      - name: {{ interface.name}}
        description: {{ interface.description }}
        {% if 'Loop' in interface.name %}
        type: virtual
        {% elif 'vlan' in interface.name %}
        type: virtual
        {% elif 'Gig' in interface.name %}
        type: 1000base-t
        {% elif 'Port' in interface.name %}
        type: lag
        {% endif %}
        label: trunk
        enabled: True
        mtu: 1500
        mgmt_only: False
        {% if inventory_hostname == 'pod1sw1' and interface.name == 'GigabitEthernet0/1' %}
        bside_device: pod1sw2
        bside_interface: GigabitEthernet0/1
        {% endif %}
        {% if inventory_hostname == 'pod1sw1' and interface.name == 'GigabitEthernet0/2' %}
        bside_device: pod1sw2
        bside_interface: GigabitEthernet0/2
        {% endif %}
        {% if inventory_hostname == 'pod1sw1' and interface.name == 'GigabitEthernet0/3' %}
        bside_device: pod1sw3
        bside_interface: GigabitEthernet0/1
        {% endif %}
        {% if inventory_hostname == 'pod1sw2' and interface.name == 'GigabitEthernet0/3' %}
        bside_device: pod1sw3
        bside_interface: GigabitEthernet0/2
        {% endif %}
        mode: Tagged
        untag_vlan: NATIVE_VLAN
        tagged_vlan_1: USERS
        tagged_vlan_2: SERVERS
        tagged_vlan_3: GUEST
    {% endfor %}
    {% endif %}
    {% if configuration.interfaces.access is defined %}
    access_interfaces:
      {% for interface in configuration.interfaces.access %}
      - name: {{ interface.name }}
        description: {{ interface.description }}
        type: 1000base-t
        label: access
        enabled: True
        mtu: 1500
        mgmt_only: False
        mode: Access
        untag_vlan: {{ interface.description }}
    {% endfor %}
    {% endif %}
    {% if configuration.interfaces.trunk is defined %}
    lag_interfaces:
    {% for interface in configuration.interfaces.trunk %}
    {% if interface.port_channel is defined %}
      - name: {{ interface.name }}
        lag: Port-Channel{{ interface.port_channel }}
    {% endif %}
    {% endfor %}
    {% endif %}
    {% if inventory_hostname == 'pod1r1' %}
    disabled_interfaces:
    - name: GigabitEthernet0/3
      type: 1000base-t
      enabled: false
    - name: GigabitEthernet0/4
      type: 1000base-t
      enabled: false
    - name: GigabitEthernet0/5
      type: 1000base-t
      enabled: false
    - name: GigabitEthernet0/6
      type: 1000base-t
      enabled: false
    {% endif %}
    {% if 'sw' in inventory_hostname %}
    disabled_interfaces:
    - name: GigabitEthernet1/0
      type: 1000base-t
      enabled: false
    - name: GigabitEthernet1/1
      type: 1000base-t
      enabled: false
    - name: GigabitEthernet1/2
      type: 1000base-t
      enabled: false
    {% endif %}
```
{% endraw %}

We should end up with three new files with the hostname appended with _node_design.yaml and it should look like this

```
device_list:
  - name: pod1r1
    device_type: vios_router
    device_role: pod_router
    site: pod1
    rack: "pod1_rr_1"
    position: 42
    face: front
    status: active
    l3_interfaces:
      - name: GigabitEthernet0/0
        description: UPLINK TO INTERNET PROVIDER
        type: 1000base-t
        enabled: True
        mtu: 1500
        mgmt_only: False
        ipv4_address: 24.24.1.2/24
        vrf: global
        status: active
      - name: GigabitEthernet0/1
        description: DOWNLINK POD1SW1
        type: 1000base-t
        enabled: True
        mtu: 1500
        mgmt_only: False
        bside_device: pod1sw1
        bside_interface: GigabitEthernet0/0
        ipv4_address: 10.10.1.0/31
        vrf: global
        status: active
        tags: 
        - ospf_area_0
        - p2p
      - name: GigabitEthernet0/2
        description: DOWNLINK POD1SW2
        type: 1000base-t
        enabled: True
        mtu: 1500
        mgmt_only: False
        bside_device: pod1sw2
        bside_interface: GigabitEthernet0/0
        ipv4_address: 10.10.1.2/31
        vrf: global
        status: active
        tags: 
        - ospf_area_0
        - p2p
      - name: Loopback0
        description: iBGP LOOPBACK
        type: virtual
        enabled: True
        mtu: 1500
        mgmt_only: False
        ipv4_address: 10.1.1.1/32
        vrf: global
        status: active
        tags: 
        - ospf_area_0
        - p2p
      - name: GigabitEthernet0/7
        description: MGMT-INTERFACE
        type: 1000base-t
        label: mgmt
        enabled: True
        mtu: 1500
        mgmt_only: True
        ipv4_address: 192.168.4.17/24
        vrf: MGMT
        status: active
        primary: true
    disabled_interfaces:
    - name: GigabitEthernet0/3
      type: 1000base-t
      enabled: false
    - name: GigabitEthernet0/4
      type: 1000base-t
      enabled: false
    - name: GigabitEthernet0/5
      type: 1000base-t
      enabled: false
    - name: GigabitEthernet0/6
      type: 1000base-t
      enabled: false
```

Ok well what the heck is all of this stuff? What we are attempting to do above? We are describing the intended structure of each device. This YAML file will be ingested into Nautobot and will show the same intended configuration in NAutobot. Look at interface GigabitEthernet0/1 for example, We have all of the items you would typically configure on the device (interface name, description, mtu, ip address) along with a few other items like tags. I will explain what the tags will be used for a little later.

I was unable to come up with an elegant way to combine these three files into a single file called invnetory/nautobot_vars/node_designs.yaml. So I just did it manually... I know right? Combine the 4 node_design files into the invnetory/nautobot_vars/node_designs.yaml file ensure that the the 4 devices are indented properly because we will use this file to loop through a playbook that will add all of this data to Nautobot.

We just need a couple more files that will contain device information, vrf, and tags. Here are the yaml files that I used.

```
# inventory/nautobot_vars/devices.yaml
manufacturer:
- name: cisco
  platform:
  - name: ios
    slug: ios
    napalm_driver: ios 
  device_types:
  - name: vios_router
    slug: vios_router
    part_number: vios-router
    u_height: 1
    is_full_depth: False
  - name: vios_switch
    slug: vios_switch
    part_number: vios-switch
    u_height: 1
    is_full_depth: False
  device_roles:
  - name: pod_router
    color: FFFFFF
  - name: pod_l3_switch
    color: FFFFFA
  - name: pod_l2_switch
    color: FFFFFB
```

```
# inventory/nautobot_vars/vrfs.yaml
vrf:
- name: MGMT
  description: "INBAND MGMT"
  prefix: 192.168.4.0/24
```

```
# inventory/nautobot_vars/tags.yaml
tags:
- name: ospf_area_0
  description: "Interface OSPF Area 0"
- name: p2p
  description: "Interface network type for OSPF Protocol"
```

Ok I think we have everything we need to start building the playbooks to import all of this stuff into Nautobot. We will approach the import in the order you would generate it via the GUI. I typically start with a site and relay rack. Since we are in there we might as well import all of the things associated with the site, like devices, device roles, vlans and prefixes associated with the vlans.  

Create a playbook, I called mine pb.load_nautobot.yaml. We will use this playbook to stack of all the tasks needed to load everything needed into Nautobot.

{% raw %}
```
# requires ansible-galaxy collection install networktocode.nautobot & pip3 install pynautobot
---
- name: "Setup Nautobot"
  hosts: localhost
  connection: local
  gather_facts: False
  
  vars_files:
   - inventory/nautobot_vars/site.yaml
   - inventory/nautobot_vars/tags.yaml
   - inventory/nautobot_vars/vrfs.yaml
   - inventory/nautobot_vars/devices.yaml
   - inventory/nautobot_vars/node_design.yaml

  roles:
  - { role: load_nautobot/create_site }
  - { role: load_nautobot/create_rack }
  - { role: load_nautobot/create_vlans }
  - { role: load_nautobot/create_vrfs }
  - { role: load_nautobot/create_prefixes }
  - { role: load_nautobot/create_manufacturer }
  - { role: load_nautobot/create_platform }
  - { role: load_nautobot/create_device_types }
  - { role: load_nautobot/create_device_roles }
  - { role: load_nautobot/create_devices }
  - { role: load_nautobot/create_access_interfaces }
  - { role: load_nautobot/create_trunk_interfaces }
  - { role: load_nautobot/create_lag_interfaces }
  - { role: load_nautobot/create_l3_interfaces }
  - { role: load_nautobot/create_disabled_interfaces }
  - { role: load_nautobot/assign_ipv4_to_interfaces }
  - { role: load_nautobot/create_tags }
```
{% endraw %}

Create a new file roles/load_nautobot/create_site/tasks/main.yaml

{% raw %}
```
# vars pulled from inventory/nautobot_vars/site
#############################################################
# Create Site in Nautobot
#############################################################
- name: Create site with all parameters
  networktocode.nautobot.site:
    url: "{{ nb_url }}"
    token: "{{ nb_token }}"
    validate_certs: no
    data:
      name: "{{ item.name }}"
      status: "{{ item.status }}"
      asn: "{{ item.asn }}"
      time_zone: "{{ item.time_zone }}"
      description: "{{ item.description }}"
      physical_address: "{{ item.physical_address }}"
      shipping_address: "{{ item.shipping_address }}"
      latitude: "{{ item.latitude }}"
      longitude: "{{ item.longitude }}"
      contact_name: "{{ item.contact_name }}"
      contact_phone: "{{ item.contact_phone }}"
      contact_email: "{{ item.contact_email }}"
      slug: "{{ item.slug }}"
      comments: "{{ item.comments }}"
    state: present
  loop: "{{ sites }}"
```
{% endraw %}

When using the loop function you will pre-pend with "item". Check out the Ansible documentation [here](https://docs.ansible.com/ansible/latest/user_guide/playbooks_loops.html). With this first task we will only focus on the specific items that are stored with the site. Give this play a run. You should now see that changes have been made on Nautobot. You should know have 1 new site created POD1.

Next up is the relay rack.
Add a new file roles/load_nautobot/create_rack/tasks.main.yaml 

{% raw %}
```
# vars pulled from inventory/nautobot_vars/site
#############################################################
# Create Rack in Nautobot
#############################################################
- name: "Create new rack"
  networktocode.nautobot.rack:
    url: "{{ nb_url }}"
    token: "{{ nb_token }}"
    validate_certs: no
    data:
      name: "{{ item.1.name }}"
      site: "{{ item.0.slug }}"
      status: "{{ item.1.status }}"
    state: present
  loop: "{{ sites | subelements('racks', 'skip_missing=True') }}"  
```
{% endraw %}

Here we are introducing something new. To enable Ansible to reach into the correct grouping we need to tell it where to look in our sites.yaml file. The looping inside Ansible is a little different than what we used in our Jinja templates previously. I found this [site](https://www.buildahomelab.com/2018/11/03/subelements-ansible-loop-nested-lists/) very helpful in explaining how this works. In our loop statement we use the filter subelements. This allows us to chose the list we want to iterate through, we are still pre-pending with "item", but now we need to tell Ansible the level in the list to look at. '1' indicates the level of the lists of lists to iterate over and 0 will reference the top list of lists (1 = racks and 0 = sites). Our task here is creating the rack, naming it, and then assigning it to a site. This is why we must reference item.0.slug, Nautobot will use the slug of each item to ensure that it assigns what you are creating to the correct element(site). Run this play again and you should now see that new racks have been created in each site.

In our next task we will start creating the vlans. Make a new file roles/load_nautobot/create_vlans/tasks/main.yaml.

{% raw %}
```
# vars pulled from inventory/nautobot_vars/site
#############################################################
# Create vlans for each site in Nautobot
#############################################################
- name: Create vlan within Nautobot with only required information
  networktocode.nautobot.vlan:
    url: "{{ nb_url }}"
    token: "{{ nb_token }}"
    validate_certs: no
    data:
      name: "{{ item.1.name }}"
      vid: "{{ item.1.vid }}"
      site: "{{ item.0.slug }}"
      status: "{{ item.1.status }}"
    state: present
  loop: "{{ sites | subelements('vlans', 'skip_missing=True') }}"
```
{% endraw %}

In our next task we will start creating the vrfs. Make a new file load_nautobot/create_vrfs/tasks/main.yaml.

{% raw %}
```
---
#############################################################
# Create VRFs in Nautobot
#############################################################    
- name: Create VRFs within Nautobot
  networktocode.nautobot.vrf:
    url: "{{ nb_url }}"
    token: "{{ nb_token }}"
    validate_certs: no
    data:
      name: "{{ item.name }}"
      description: "{{ item.description }}"
    state: present
  loop: "{{ vrf }}"

#############################################################
# Create prefixes for each VRF in Nautobot
#############################################################
- name: Create prefixes and assign to VRFs within Nautobot
  networktocode.nautobot.prefix:
    url: "{{ nb_url }}"
    token: "{{ nb_token }}"
    validate_certs: no
    data:
      family: 4
      prefix: "{{ item.prefix }}"
      description: "{{ item.description }}"
      vrf: "{{ item.name }}"
      status: active
    state: present  
  loop: "{{ vrf }}"
```
{% endraw %}


Then we will create the prefixes. Make a new file roles/load_nautobot/create_prefixes/tasks/main.yaml.

{% raw %}
```
# vars pulled from inventory/nautobot_vars/site
#############################################################
# Create prefixes for each site in Nautobot
#############################################################
- name: Create interface prefixes within Nautobot
  networktocode.nautobot.prefix:
    url: "{{ nb_url }}"
    token: "{{ nb_token }}"
    validate_certs: no
    data:
      family: 4
      prefix: "{{ item.1.prefix }}"
      site: "{{ item.0.slug }}"
      description: "{{ item.1.description }}"
      status: active
    state: present  
  loop: "{{ sites | subelements('int_prefixes', 'skip_missing=True') }}"
```
{% endraw %}

Now that we have all of the site specific items completed we can move on to all of the things our devices will require.

First up is adding the manufacturer, platform, device types and device roles.

Create more new files
- roles/load_nautobot/create_manufacturer/tasks/main.yaml
- roles/load_nautobot/create_platforms/tasks/main.yaml
- roles/load_nautobot/create_device_types/tasks/main.yaml
- roles/load_nautobot/create_device_roles/tasks/main.yaml

{% raw %}
```
#############################################################
# Create Manufacturer in Nautobot
#############################################################    
- name: Create manufacturer within Nautobot 
  networktocode.nautobot.manufacturer:
    url: "{{ nb_url }}"
    token: "{{ nb_token }}"
    validate_certs: no
    data:
      name: "{{ item.name }}"
    state: present
  loop: "{{ manufacturer }}"

#############################################################
# Create Platform in Nautobot
#############################################################   
- name: Create platform within Nautobot with only required information
  networktocode.nautobot.platform:
    url: "{{ nb_url }}"
    token: "{{ nb_token }}"
    validate_certs: no
    data:
      name: "{{ item.1.name }}"
      manufacturer: "{{ item.0.name }}"
      napalm_driver: "{{ item.1.napalm_driver }}"
    state: present
  loop: "{{ manufacturer | subelements('platform', 'skip_missing=True') }}"    

#############################################################
# Create Device Types in Nautobot
#############################################################     
- name: Create device type within Nautobot
  networktocode.nautobot.device_type:
    url: "{{ nb_url }}"
    token: "{{ nb_token }}"
    validate_certs: no
    data:
      slug: "{{ item.1.slug }}"
      model: "{{ item.1.name }}"
      manufacturer: "{{ item.0.name }}"
      part_number: "{{ item.1.part_number }}"
      u_height: "{{ item.1.u_height }}"
      is_full_depth: "{{ item.1.is_full_depth }}"
    state: present
  loop: "{{ manufacturer | subelements('device_types', 'skip_missing=True') }}"

#############################################################
# Create Device Roles in Nautobot
############################################################# 
- name: Create device role within Nautobot
  networktocode.nautobot.device_role:
    url: "{{ nb_url }}"
    token: "{{ nb_token }}"
    validate_certs: no
    data:
      name: "{{ item.1.name }}"
      color: "{{ item.1.color }}"
    state: present
  loop: "{{ manufacturer | subelements('device_roles', 'skip_missing=True') }}"  
```
{% endraw %}

Next we can start creating the devices and related items. We will need to make several more folders under roles. All of the variables will be pulled from the inventory/nautobot_vars/node_design.yaml file.
- roles/load_nautobot/create_devices/tasks/main.yaml
- roles/load_nautobot/create_access_interfaces/tasks/main.yaml
- roles/load_nautobot/create_trunk_interfaces/tasks/main.yaml
- roles/load_nautobot/create_lag_interfaces/tasks/main.yaml
- roles/load_nautobot/create_l3_interfaces/tasks/main.yaml
- roles/load_nautobot/create_disabled_interfaces/tasks/main.yaml

{% raw %}
```
#############################################################
# Create access interfaces in Nautobot
#############################################################
- name: Add access interfaces
  networktocode.nautobot.device_interface:
    url: "{{ nb_url }}"
    token: "{{ nb_token }}"
    validate_certs: no
    data:
      device: "{{ item.0.name }}"
      name: "{{ item.1.name }}"
      description: "{{ item.1.description }}"
      type: "{{ item.1.type }}"
      enabled: "{{ item.1.enabled }}"
      mode: "{{ item.1.mode }}"
      untagged_vlan:
        name: "{{ item.1.untag_vlan }}"
        site: "{{ item.0.site }}"
      mtu: "{{ item.1.mtu }}"
      mgmt_only: "{{ item.1.mgmt_only }}"  
    state: present
  loop: "{{ device_list | subelements('access_interfaces', 'skip_missing=True') }}"

#############################################################
# Update Device Trunk interfaces inherited in Nautobot
#############################################################
- name: Add Trunk interfaces
  networktocode.nautobot.device_interface:
    url: "{{ nb_url }}"
    token: "{{ nb_token }}"
    validate_certs: no
    data:
      device: "{{ item.0.name }}"
      name: "{{ item.1.name }}"
      description: "{{ item.1.description }}"
      type: "{{ item.1.type }}"
      enabled: "{{ item.1.enabled }}"
      mode: "{{ item.1.mode }}"
      untagged_vlan:
        name: "{{ item.1.untag_vlan }}"
        site: "{{ item.0.site }}"
      tagged_vlans:
        - name: "{{ item.1.tagged_vlan_1 }}"
          site: "{{ item.0.site }}"
        - name: "{{ item.1.tagged_vlan_2 }}"
          site: "{{ item.0.site }}"
        - name: "{{ item.1.tagged_vlan_3 }}"
          site: "{{ item.0.site }}"    
      mtu: "{{ item.1.mtu }}"
      mgmt_only: "{{ item.1.mgmt_only }}"  
    state: present
  loop: "{{ device_list | subelements('trunk_interfaces', 'skip_missing=True') }}"

#############################################################
# Update Device Lag interfaces inherited in Nautobot
#############################################################
- name: Add LAG interfaces
  networktocode.nautobot.device_interface:
    url: "{{ nb_url }}"
    token: "{{ nb_token }}"
    validate_certs: no
    data:
      device: "{{ item.0.name }}"
      name: "{{ item.1.name }}"
      lag:
        name: "{{ item.1.lag }}" 
    state: present
  loop: "{{ device_list | subelements('lag_interfaces', 'skip_missing=True') }}"

#############################################################
# Update Device Layer3 interfaces inherited in Nautobot
#############################################################
- name: Add Layer3 interfaces
  networktocode.nautobot.device_interface:
    url: "{{ nb_url }}"
    token: "{{ nb_token }}"
    validate_certs: no
    data:
      device: "{{ item.0.name }}"
      name: "{{ item.1.name }}"
      description: "{{ item.1.description }}"
      type: "{{ item.1.type }}"
      enabled: "{{ item.1.enabled }}"
      mtu: "{{ item.1.mtu }}"
      mgmt_only: "{{ item.1.mgmt_only }}"  
    state: present
  loop: "{{ device_list | subelements('l3_interfaces', 'skip_missing=True') }}"

#############################################################
# Update Device Disabled interfaces inherited in Nautobot
#############################################################
- name: Add disabled interfaces
  networktocode.nautobot.device_interface:
    url: "{{ nb_url }}"
    token: "{{ nb_token }}"
    validate_certs: no
    data:
      device: "{{ item.0.name }}"
      name: "{{ item.1.name }}"
      type: "{{ item.1.type }}"
      enabled: "{{ item.1.enabled }}" 
    state: present
  loop: "{{ device_list | subelements('disabled_interfaces', 'skip_missing=True') }}"
```
{% endraw %}

Now that we have all of the devices created and the interfaces added to each device we can add IP addressing and the tags we talked about earlier. We will be tagging the IP address that will be associated to the device interfaces. The reason for the tags will be to tell our Jinja2 Templates building the configurations that specific interfaces are in an OSPF area and that it should be a specific network type. Why not just tag the interfaces? You could, how you building your logic is really up to how you associate things, for me it made more sense to associate to the IP address because in the cisco configurations it goes below the IP addressing on the interface and the logic worked better for me this way.

Lets make a couple more files 
- roles/load_nautobot/assign_ipv4_to_interfaces/tasks/main.yaml
- roles/load_nautobot/create_tags/tasks/main.yaml

{% raw %}
```
# roles/load_nautobot/assign_ipv4_to_interfaces/tasks/main.yaml
#############################################################
# Assigning IP addresses to VRFs in Nautobot
#############################################################    
- name: Add IP addresses to Layer3 interfaces
  networktocode.nautobot.ip_address:
    url: "{{ nb_url }}"
    token: "{{ nb_token }}"
    validate_certs: no
    data:
      address: "{{ item.1.ipv4_address }}"
      vrf: "{{ item.1.vrf }}"
      status: "{{ item.1.status }}"
      assigned_object:
        name: "{{ item.1.name }}"
        device: "{{ item.0.name }}"
    state: present
  loop: "{{ device_list | subelements('l3_interfaces', 'skip_missing=True') }}"
  when: item.1.mgmt_only == true

#############################################################
# Assigning IP addresses to interfaces inherited in Nautobot
#############################################################    
- name: Add IP addresses to Layer3 interfaces
  networktocode.nautobot.ip_address:
    url: "{{ nb_url }}"
    token: "{{ nb_token }}"
    validate_certs: no
    data:
      address: "{{ item.1.ipv4_address }}"
      status: "{{ item.1.status }}"
      assigned_object:
        name: "{{ item.1.name }}"
        device: "{{ item.0.name }}"
    state: present
  loop: "{{ device_list | subelements('l3_interfaces', 'skip_missing=True') }}"
  when: item.1.mgmt_only == false

# roles/load_nautobot/create_tags/tasks/main.yaml
#############################################################
#Creating the tags in Nautobot
############################################################# 
- name: Create tags within Nautobot
  networktocode.nautobot.tag:
    url: "{{ nb_url }}"
    token: "{{ nb_token }}"
    validate_certs: no
    data:
      name: "{{ item.name }}"
      description: "{{ item.description }}"
    state: present  
  loop: "{{ tags }}"

#############################################################
# Associating tags to the IP addresses
#############################################################
- name: Add tags to IP addresses
  networktocode.nautobot.ip_address:
    url: "{{ nb_url }}"
    token: "{{ nb_token }}"
    validate_certs: no
    data:
      address: "{{ item.1.ipv4_address }}"
      status: "{{ item.1.status }}"
      tags: "{{ item.1.tags }}"
      assigned_object:
        name: "{{ item.1.name }}"
        device: "{{ item.0.name }}"
    state: present
  loop: "{{ device_list | subelements('l3_interfaces', 'skip_missing=True') }}"
  when: item.1.tags is defined
```
{% endraw %}

This covers as much of the data entry that we can do through the Ansible Module. In the next section we will cover making a python script that will do the same thing we just accomplished. 

[Installing Ansible - Section 1](installing_ansible.md)

[Creating an Inventory File - Section 2](inventory_file.md)

[Creating a playbook - Section 3](first_play.md)

[Building Roles - Section 4](building_roles.md)

[Building the core switch Roles - Section 5](section5-coreswitch.md)

[Building the router Roles - Section 6](section6-router.md)

[Introducing PyNautobot - Section 8](section8-pynautobot.md)

[Querying your device data from nautobot - Section 9](section9-querynautobot.md)

[Full configuration Jinja Templates - Section 10](section10-jinja_templates.md)

[Using the Nautobot Inventory module as your inventory source - Section 11](section11-nautobot-inventory.md)