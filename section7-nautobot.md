## Section 7: Introducing a source of truth to our Ansible workflow 
<!-- {% include section5.html %} -->

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
---
- name: Generate the site file
  hosts: localhost
  connection: local
  gather_facts: false

  vars_files:
    - inventory/host_vars/pod1sw1/bgp.yaml
    - inventory/host_vars/pod1sw1/l3_interfaces.yaml
    - inventory/host_vars/pod1sw1/vlans.yaml
  roles:
  - { role: create_load_file/site }
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
        {% if 'Loop' or 'vlan' in interface.name %}
        type: virtual
        {% elif 'Gigabit' in interface.name %}
        type: 1000base-t
        {% endif %}
        enabled: True
        mtu: 1500
        mgmt_only: False
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
    {% if configuration.interfaces.trunk is defined %}
    trunk_interfaces:
      {% for interface in configuration.interfaces.trunk %}
      - name: {{ interface.name}}
        description: {{ interface.description }}
        type: lag
        label: trunk
        enabled: True
        mtu: 1500
        mgmt_only: False
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
        type: virtual
        enabled: True
        mtu: 1500
        mgmt_only: False
        ipv4_address: 24.24.1.2/24
        vrf: global
        status: active
      - name: GigabitEthernet0/1
        description: DOWNLINK POD1SW1
        type: virtual
        enabled: True
        mtu: 1500
        mgmt_only: False
        ipv4_address: 10.10.1.0/31
        vrf: global
        status: active
        tags: 
        - ospf_area_0
        - p2p
      - name: GigabitEthernet0/2
        description: DOWNLINK POD1SW2
        type: virtual
        enabled: True
        mtu: 1500
        mgmt_only: False
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
```
  



Create a playbook, I called mine nb.create.sites.yaml. We will be using this single playbook to perform all of the tasks above. We will make use of the looping function inside of Ansible to digest all of the data for each of the 6 pods. The sites file above is an example and the full file can be found in the github repo. 

{% raw %}
```
---
- name: Load Nautobot
  connection: local
  hosts: localhost
  gather_facts: False

  vars:
    nb_url: "https://localhost:8000"
    nb_token: "YOUR GENERATED TOKEN HERE"

  tasks:
#############################################################
# Create Site in Nautobot
#############################################################
    - include_vars: "nb_vars/sites.yaml"
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
When using the loop function you will prepend with "item". Check out the Ansible documentation [here](https://docs.ansible.com/ansible/latest/user_guide/playbooks_loops.html). With this first task we will only focus on the specific items that are stored with the site. Give this play a run. You should now see that changes have been made on Nautobot. You should know have 6 new sites created POD1 through POD6.

Moving on we will now create the Relay Racks in each of the 6 pod sites. Notice that at the bottom of the example of sites.yaml we have a grouping called Racks. We will use that data to generate our racks inside of Nautobot.
```
racks:
  - name: "Pod1 Rack 1"
    status: active  
```
Add a new task to our nb.create.sites.yaml playbook. and place it below the creating site task. Take care and ensure the indentation is correct.
{% raw %}
```
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
Here we are introducing something new. To enable Ansible to reach into the correct grouping we need to tell it where to look in our sites.yaml file. The looping inside Ansible is a little different than what we used in our Jinja templates previously. I found this [site](https://www.buildahomelab.com/2018/11/03/subelements-ansible-loop-nested-lists/) very helpful in explaining how this works. In our loop statement we use the filter subelements. This allows us to chose the list we want to iterate through, we are still prepending with "item", but now we need to tell Ansible the level in the list to look at. '1' indicates the level of the lists of lists to iterate over and 0 will reference the top list of lists (1 = racks and 0 = sites). Our task here is creating the rack, naming it, and then assigning it to a site. This is why we must reference item.0.slug, Nautobot will use the slug of each item to ensure that it assigns what you are creating to the correct element(site). Run this play again and you should now see that new racks have been created in each site.

Add a two new tasks to our play. We want to generate vlans and prefixes for each site. These are the same vlans and prefixes we assigned to each pod at the beginning of the workshop. In your sites.yaml file create two new lists on each site int_prefixes and vlans

```
int_prefixes:
  - prefix: 10.10.1.0/31
    description: "R1-GI0/1 - SW1-GI0/0"
  - prefix: 10.10.1.2/31
    description: "R1-GI0/2 - SW2-GI0/0"
  - prefix: 24.24.1.0/24
    description: "R1-GI0/0 - INTERNET"  
  vlans:
  - name: USERS
    vid: 300
    status: active
    prefix: 155.1.1.0/26
  - name: SERVERS
    vid: 350
    status: active
    prefix: 155.1.1.64/26
  - name: GUESTS
    vid: 400
    status: active
    prefix: 155.1.1.128/26
```
In our new tasks we will start with creating the vlans first

{% raw %}
```
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
Then we will create the prefixes
{% raw %}
```
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

The next piece of the puzzle is generating the device specific items (manufacturer, device types, device roles, and platform). Create a new file in nb_vars named devices.yaml. In this file we will list out everything associated with the cisco devices being used in our pods. We will indent everything under manufacturer as it is all ultimately associated with cisco. 

```
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
We will also be adding four new tasks that will create of of the above elements inside of Nautobot.

{% raw %}
```
#############################################################
# Create Manufacturer in Nautobot
#############################################################    
    - include_vars: "nb_vars/devices.yaml"
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



[Installing Ansible - Section 1](installing_ansible.md)

[Creating an Inventory File - Section 2](inventory_file.md)

[Creating a playbook - Section 3](first_play.md)

[Building Roles - Section 4](building_roles.md)

[Building the core switch Roles - Section 5](section5-coreswitch.md)

[Building the router Roles - Section 6](section6-router.md)



