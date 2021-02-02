# Ansible_Workshop
## Section 1: Install Python3, pip3 and Ansible
Open the terminal window. type pwd in the terminal and it should be showing you your home directory (/home/lab_user1) for example.
In the terminal window type the below commands one at a time.
```
mkdir Ansible_workshop && cd Ansible_workshop
apt update
apt install software-properties-common
apt install python3-pip
apt install python3-venv
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

Create a text file using your terminal and name it requirements.txt we will use this to install the required python packages.
```
nano requirements.txt
```
Paste in the following text. 
```
ansible
pyats
genie
colorama
```
Now run the below command in terminal to install the packages
```
pip3 install -r requirements.txt
```
Now that we have ansible installed we need to add a module that will help us connect and configure our topolgy
```
ansible-galaxy collection install cisco.ios clay584.genie
```

## Section 2: Building playbooks
Our task is to build out a set of playbooks that will deploy a full office with following configuration:
1. (1) Access switch
    * Access ports for Users, Servers, and Guests
    * Layer 2 trunk to the core switches
2. (2) Core switches
    * Layer 2 trunk ports to the access switch
    * Layer 2 port channel between both core switches
    * SVIs for the Users, Servers, and Guest vlans
    * VRRP protocol for redunancy
    * Layer 3 P2P interfaces as UPLINKS to the router
    * Loopback0 interface to facilitate iBGP protocol peering
    * OSPF protocol to facilitate iBGP protocol Loopback0 peering
    * iBGP protocol to advertise Users, Servers, and Guest subnets to the router
3.  (1) Router
    * Layer 3 P2P interfaces as DOWNLINKS to the core switches
    * Loopback0 interface to facilitate iBGP protocol
    * OSPF protocol to facilitate iBGP protocol
    * iBGP protocol to receive advertised Users, Servers, and Guest subnets from the core switches
    * eBGP protocol to advertise Users, Servers, and Guest subnets to the ISP and receive a default route from the ISP
    * DHCP server for Users, Servers, and Guest subnets
The Lab diagram below consists of the IP addressing for each POD. The (x) will be replaced with the POD number you are using. 
### Lab Pod Diagram
![Lab Pod diagram](https://github.com/TwistByrn/Ansible_Workshop/blob/main/images/Ansible-WorkShop.png)
## Section 2.1: Creating the inventory yaml file
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

## Section 2.2: Creating plays
Documentation on creating Plays with ansible can be found ![here](https://docs.ansible.com/ansible/latest/user_guide/playbooks.html). We will be using the ![Cisco IOS Collection](https://github.com/ansible-collections/cisco.ios) and templating with ![Jinja2](https://docs.ansible.com/ansible/latest/user_guide/playbooks_templating.html) to create the configurations that will be sent to each device via an SSH session from our Ansible controll node. So with all of this information lets create a play to reach out to one of our switches and pull back the configured vlan database.

In your main folder (Ansible_Workshop) create a new file pb.get.vlans.yml. Every play needs the below structure. At the top of the play we list what and how we are connecting to with hosts: we will connect to podxsw3. Gather_facts in our use case will always be false. Connection will be network_cli. Below these details we will list out the tasks to be peformed in this play. Notice the structure of the file below. indentation is key to ensure that ansible can read in this file. Our first task is using the cisco ios collection to run the command on podxsw3 (show vlan). The register will store the output of the SSH sessions command (show vlan). Our next tasks is to take that store result and display it on our terminal window. Ansible has a debug that will handle this and is a useful way to validate the results you are getting from the terminal window. We could also print it to a file if you desired. With the help of clay584s parsing collection this (show vlan) output will be displayed in a structured yaml format. 
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
The built in parser for this command will print the result this way in our terminal window

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