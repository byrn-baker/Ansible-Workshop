# Ansible_Workshop
## Section 1: Install Python3, pip3 and Ansible
Open the terminal window. type pwd in the terminal and it should be showing you your home directory (/home/lab_user1) for example.
In the terminal window type the below commands one at a time.
```
mkdir Ansible_Workshop && cd Ansible_Workshop
sudo apt update
sudo apt install software-properties-common python3-pip python3-venv
```
Now we will create a new python virtual environment
```
python3 -m venv .venv
```
Activate the virtual environment
```
source .venv/bin/activate
```
Now that we are inside the python environment we can install packages here that will not affect our system python environment. This allows you to use different versions of ansible or other python packages that can potentially conflict. This also helps make your Ansible playbooks portable.

Now run the below command in terminal to install the packages
```
pip3 install wheel ansible pyats genie colorama 
```
Now that we have ansible installed we need to add a module that will help us connect and configure our topolgy
```
ansible-galaxy collection install cisco.ios clay584.genie
```
## Section 2: Creating the inventory yaml file
![Ansible inventory Documentation can be found here](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html#) 
We will be constructing our inventory file with yaml format. Each pod has a bootstrap configuration that includes IP addressing to each node. Your control nodes (Jumpbox VM) has the /etc/hosts file built and each node has been assigned a hostname and an IP address.
Here are the groupings we will be building in our inventory file.
1. Routers
    *   podxr1
2. Core Switches
    *   podxsw1
    *   podxsw2
3. Access Switches
    *   podxsw3

The inventory file is what Ansible will use to connect to each of the managed hosts. We can assign each host to a group and each group to a parent group. Our file structure example is below along with the inventory.yml file.
```
inventory/
    inventory.yml
    group_vars/
        all/
            all.yml
    host_vars/
        podxr1/
        podxsw1/
        podxsw2/
        podxsw3/
```
inventory.yml - Our inventory file will use groupings of "all". "pod1" will be a child group of the parent "all". "routers", "core_switches" and "access_switches" will all be children of the parent group "pod1". 
```
---
all:
  children:
    pod1:
      children:
        routers:
          hosts:
            pod1r1:    
        core_switches:
          hosts:
            pod1sw1:
            pod1sw2:
        access_switches:
          hosts:
            pod1sw3:
```
Each host will be defined under the lower groupings (routers, core_switches, and access_switches). We can store variables in our plays in these folders, including sensitive information like passwords. In this workshop, we will keep information like usernames and passwords under the group_vars/all folder in a file called "all.yml" If you were to have devices or device groups that did not use the same password, then you could create a file of the device name under the host_vars/{{ device_name }} folder. In this workshop all devices share login and OS. If you want to learn more about encrypting files with ansible use the ansible docs on ![Ansible Vault](https://docs.ansible.com/ansible/latest/user_guide/vault.html)
```
---
###########################################
# Stored variables for login and device OS
###########################################

ansible_password: Labuser!23
ansible_user: pod1
ansible_network_os: ios
```

## Section 3: Creating plays
Documentation on creating Plays with ansible can be found ![here](https://docs.ansible.com/ansible/latest/user_guide/playbooks.html). We will be using the ![Cisco IOS Collection](https://github.com/ansible-collections/cisco.ios) and templating with ![Jinja2](https://docs.ansible.com/ansible/latest/user_guide/playbooks_templating.html) to create the configurations that will be sent to each device via an SSH session from our Ansible controll node. So with all of this information lets create a play to reach out to one of our switches and pull back the configured vlan database.

In your main folder (Ansible_Workshop) create a new file pb.get.vlans.yml. Every play needs the below structure. At the top of the play we list what and how we are connecting to with hosts: we will connect to podxsw3. Gather_facts in our use case will always be false. Connection will be network_cli. Below these details we will list out the tasks to be peformed in this play. Notice the structure of the file below. indentation is key to ensure that ansible can read in this file. Our first task is using the cisco ios collection to run the command on podxsw3 (show vlan). The register will store the output of the SSH sessions command (show vlan). Our next tasks is to take that store result and display it on our terminal window. Ansible has a debug that will handle this and is a useful way to validate the results you are getting from the terminal window. We could also print it to a file if you desired. With the help of ![clay584s parse_genie collection](https://github.com/clay584/parse_genie) this (show vlan) output will be displayed in a structured yaml format. 

To run this play in terminal

```
---
############################################################
# Pulls down the existing vlan database from a cisco switch
############################################################

- name: Connect to access switches
  hosts: pod1sw3
  gather_facts: false
  connection: network_cli

  tasks:
  - name: show vlan
    ios_command:
      commands: 
        - "show vlan"
    register: ios_output

  - name: Print Structured Data
    debug:
      msg: "{{ ios_output['stdout'][0] | clay584.genie.parse_genie(command='show vlan', os='ios')  }}"
    delegate_to: localhost
```
The results of (show vlan) from the cli would look like this
```
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Gi0/0, Gi0/1, Gi0/2, Gi0/3
                                                Gi1/0, Gi1/1, Gi1/2
300  USERS                            active    
350  SERVERS                          active    
400  GUEST                            active    
666  NATIVE_VLAN                      active    
1002 fddi-default                     act/unsup 
1003 token-ring-default               act/unsup 
1004 fddinet-default                  act/unsup 
1005 trnet-default                    act/unsup 

VLAN Type  SAID       MTU   Parent RingNo BridgeNo Stp  BrdgMode Trans1 Trans2
---- ----- ---------- ----- ------ ------ -------- ---- -------- ------ ------
1    enet  100001     1500  -      -      -        -    -        0      0   
300  enet  100300     1500  -      -      -        -    -        0      0   
350  enet  100350     1500  -      -      -        -    -        0      0   
400  enet  100400     1500  -      -      -        -    -        0      0   
666  enet  100666     1500  -      -      -        -    -        0      0   
1002 fddi  101002     1500  -      -      -        -    -        0      0   
1003 tr    101003     1500  -      -      -        -    -        0      0   
          
VLAN Type  SAID       MTU   Parent RingNo BridgeNo Stp  BrdgMode Trans1 Trans2
---- ----- ---------- ----- ------ ------ -------- ---- -------- ------ ------
1004 fdnet 101004     1500  -      -      -        ieee -        0      0   
1005 trnet 101005     1500  -      -      -        ibm  -        0      0   

Primary Secondary Type              Ports
------- --------- ----------------- ------------------------------------------
```
![Parse_genie](https://github.com/clay584/parse_genie) parses results of the show vlan command and prints the result in our terminal window

```
msg:
    vlans:
      '1':
        interfaces:
        - GigabitEthernet0/0
        - GigabitEthernet0/1
        - GigabitEthernet0/2
        - GigabitEthernet0/3
        - GigabitEthernet1/0
        - GigabitEthernet1/1
        - GigabitEthernet1/2
        mtu: 1500
        name: default
        said: 100001
        shutdown: false
        state: active
        trans1: 0
        trans2: 0
        type: enet
        vlan_id: '1'
      '1002':
        mtu: 1500
        name: fddi-default
        said: 101002
        shutdown: false
        state: unsupport
        trans1: 0
        trans2: 0
        type: fddi
        vlan_id: '1002'
      '1003':
        mtu: 1500
        name: token-ring-default
        said: 101003
        shutdown: false
        state: unsupport
        trans1: 0
        trans2: 0
        type: tr
        vlan_id: '1003'
      '1004':
        mtu: 1500
        name: fddinet-default
        said: 101004
        shutdown: false
        state: unsupport
        stp: ieee
        trans1: 0
        trans2: 0
        type: fdnet
        vlan_id: '1004'
      '1005':
        mtu: 1500
        name: trnet-default
        said: 101005
        shutdown: false
        state: unsupport
        stp: ibm
        trans1: 0
        trans2: 0
        type: trnet
        vlan_id: '1005'
      '300':
        mtu: 1500
        name: USERS
        said: 100300
        shutdown: false
        state: active
        trans1: 0
        trans2: 0
        type: enet
        vlan_id: '300'
      '350':
        mtu: 1500
        name: SERVERS
        said: 100350
        shutdown: false
        state: active
        trans1: 0
        trans2: 0
        type: enet
        vlan_id: '350'
      '400':
        mtu: 1500
        name: GUEST
        said: 100400
        shutdown: false
        state: active
        trans1: 0
        trans2: 0
        type: enet
        vlan_id: '400'
      '666':
        mtu: 1500
        name: NATIVE_VLAN
        said: 100666
        shutdown: false
        state: active
        trans1: 0
        trans2: 0
        type: enet
        vlan_id: '666'
```
The results are now in a format that we can store and reuse for validation of changes. This is something that is currently out scope, but will be something added to this workshop eventually.

## Section 4: Building Roles
We have the following tasks to complete the rollout of our pod. We will be breaking each tasks down into their own play that we will refer to as a ![Role](https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html). Our Pods will be making use of the Cisco vIOS router and vIOS switch.

1. (1) Access switch
    * Configure the following vlans:
      * Users - Vlan 300
      * Servers - Vlan 350
      * Guests - Vlan 400
      * Native Vlan - Vlan 666
    * Configure the following Access ports:
      * Users - Port Gi0/3 
      * Servers - Port Gi1/0
      * Guests - Port Gi1/1
    *  Configure a Layer 2 trunk to core switch 1 and core switch 2 on the Ports Gi0/1 and Gi0/2
      * Trunks should only pass the configured vlans
    * A linux VM has been connect to port Gi0/3 on the access switch and is accessable from the Guacamole front end
2. (2) Core switches
    * Configure the following vlans:
      * Users - Vlan 300
      * Servers - Vlan 350
      * Guests - Vlan 400
      * Native Vlan - Vlan 666
    * Configure Layer 2 trunk ports to the access switch on ports Gi0/3
      * Trunks should only pass the configured vlans
    * Configure a Layer 2 port channel between both core switches on Ports Gi0/1 and Gi0/2
      * Trunks should only pass the configured vlans
      * Use Port-Channel 12
    * Configure SVIs for the following: 
      * Users - IP 155.x.1.0/26
      * Servers - IP 155.x.1.64/26
      * Guest - IP 155.x.1.128/26
    * Configure VRRP protocol for redunancy on above vlans
      * Use the first IP in the scope as your gateway
    * Configure Layer 3 interfaces as UPLINKS to the router
      * Core Switch 1 Port Gi0/0 with IP 10.x0.1.1/31
      * Core Switch 2 Port Gi0/0 with IP 10.x0.1.3/31
    * Configure Loopback0 interface to facilitate iBGP protocol peering
      * Core Switch 1 Loopback0 IP 10.x.1.2/32
      * Core Switch 2 Loopback0 IP 10.x.1.3/32
    * Configure OSPF to facilitate iBGP Loopback0 peering
    * Use iBGP to advertise Users, Servers, and Guest subnets to the router
      * Use AS 6500x
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

The Lab diagram below consists of the IP addressing for each POD. The (x) will be replaced with the POD number you are using. 
### Lab Pod Diagram
![Lab Pod diagram](https://github.com/TwistByrn/Ansible_Workshop/blob/main/images/Ansible-WorkShop.png)

Create new folders with the following structure:
```
inventory/
  group_vars/
    podx/
      pod1.yml
  host_vars/
    podxr1/
    podxsw1/
    podxsw2/
    podxsw3/
```
```
roles/
  access_switch/
  core_switch/
  routers/
```
In the roles/access_switch folder create the following structure:
```
add_access_interface/
  tasks/
  templates/
add_trunk_interface/
  tasks/
  templates/
add_vlan/
  meta/
  tasks/
  templates/

Create a new file under 'inventory/group_vars/' called 'pod1.yml'. In this file we will store our username and password for the assigned pod place the following text in your file:
```
---
ansible_password: Labuser!23
ansible_user: podx
ansible_network_os: ios
```

Create a new file under 'inventory/host_vars/podxsw3/' called 'vlans.yml'. In this file we will create a list of vlans that we need to create on our access switch and can reuse this same file for our core switches later on. Place the following text in your file:
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

Create a new file under 'add_vlan/meta/' called 'main.yml'. This file will pull the collection we are using to deploy the configurations to the IOS switches in the pod. This simply replaces the Collection section inside a standard playbook and assigns it to this task. Inside the meta.yml file place the following text:
```
collections:
  - clay584.parse_genie
```
Create a new file under 'add_vlan/tasks/' called 'main.yml'. This file will be structure similar to the Playbook we created to pull down a list of vlans from the podxsw3 host. In this play we will use a Jinja2 template to create and name the vlans for the 3 user groups (Users, Servers, Guests).

In the main.yml file we will use the playbook tasks structure. Roles simply replace tasks of a playbook.

```
---
- name: Add new vlan to vlan database on {{ inventory_hostname }}
  cisco.ios.ios_config:
    src: add_vlan.j2

- name: Saving the running config on {{ inventory_hostname }}
  ios_config:
    save_when: always
```

Create a new file under 'add_vlan/templates/ called 'add_vlan.j2'. this will store our Jinja2 template that will utlize the host_vars we created above. Jinja templates print out the text in the file while give you the ability to insert predefined variables at any location in the text that you wish. Ansible holds this information in memory and the cisco IOS module pushes the full text to our switch similar to a copy and paste from an SSH session on the CLI.

In the 'add_vlan.j2' file place the following text:
```
#jinja2: lstrip_blocks: "True (or False)", trim_blocks: "True (or False)"
{#- ---------------------------------------------------------------------------------- #}
{# configuration.vlans                                                                 #}
{# ---------------------------------------------------------------------------------- -#}
{% if configuration.vlans is defined %}
{% if configuration.vlans.vlan is not mapping and configuration.vlans.vlan is not string %}
{% for vlan in configuration.vlans.vlan %}
vlan {{ vlan.vlan_id }}
    {% if vlan.name is defined %}
    name {{ vlan.name }}
    {% endif %}
{% endfor %}
{% endif %}
{% endif %}
```
Lets go over what we are doing
'#jinja2: lstrip_blocks: "True (or False)", trim_blocks: "True (or False)"' - This line tells the Jinja template to remove any white space that is added before or after our IF statements or FOR statements. 
'{# #}' - These characters tell the jinja template not to render the text between the characters. This is what we call commenting and allows you to tell someone else reading your template what you are doing and why with rendered the text in the file output.
'{% if configuration.vlans.vlan is not mapping and configuration.vlans.vlan is not string %}' - This is looking to make sure our VLANs are actually a string of numbers and not text or some other character as anything other than a number would not be accepted by the cisco CLI.
'{% if configuration.vlans is defined %}' - Any 'IF' statement will always need to be followed with an '{% endif %}'. In our case we will only render the below text 'if configuration.vlans exists or is defined' in our host_vars files otherwise move on to the next task. 
'{% for vlan in configuration.vlans.vlan %}' - This line will always need to be followed with an '{% endfor %}'. The 'FOR LOOP' is a loop and it will continue printing the text between '{% for vlan in configuration.vlans.vlan %}' and '{% endfor %}' until the entire list has been iterated through. This allows us to create an easy to read lists of things we want to configure in our host_vars files. In this case we created a list of vlans and its names in the '/host_vars/podxsw3/vlans.yml' file.
'{% if vlan.name is defined %}' - This line will print the name of the vlan if it has been included in our '/host_vars/podxsw3/vlans.yml' file. If it has not been defined then we just skip that portion of text in the rendering and move on to the next task.