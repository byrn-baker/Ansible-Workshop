## Section 3: Creating plays
{% include section3.html %}
Documentation on creating Plays with ansible can be found [here](https://docs.ansible.com/ansible/latest/user_guide/playbooks.html). We will be using the [Cisco IOS Collection](https://github.com/ansible-collections/cisco.ios) and templates with [Jinja2](https://docs.ansible.com/ansible/latest/user_guide/playbooks_templating.html) to create the configurations that will be sent to each device via an SSH session from our Ansible control node. So with all of this information lets create a play to reach out to one of our switches and pull back the configured vlan database.

In your main folder (Ansible_Workshop) create a new file pb.get.vlans.yaml. Every play needs the below structure. At the top of the play we list what and how we are connecting to with 
* hosts: we will connect to podxsw3. 
* Gather_facts in our use case will always be false. 
* Connection will be network_cli.

Below these details we will list out the tasks to be performed in this play. Notice the structure of the file below. indentation is key to ensure that ansible can read in this file. Our first task is using the cisco ios collection to run the command on podxsw3 "show vlan". The register will store the output of "show vlan". Our next tasks is to take that stored result and display it on our terminal window. Ansible has a debug that will handle this and is a useful way to validate the results Ansible is getting from the device. We could also print it to a file if you desired. With the help of [clay584s parse_genie](https://github.com/clay584/parse_genie) this "show vlan" output will be displayed in a structured yaml format. 

To run the play type into the terminal ``` ansible-playbook -i inventory/inventory.yaml pb.get.vlans.yaml ```

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
[Parse_genie](https://github.com/clay584/parse_genie) parses results of the show vlan command and prints the result in our terminal window

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

[Installing Ansible - Section 1](installing_ansible.md)

[Creating an Inventory File - Section 2](inventory_file.md)

[Building Roles - Section 4](building_roles.md)

[Building the core switch Roles - Section 5](section5-coreswitch.md)

[Building the router Roles - Section 6](section6-router.md)

[Introducing Nautobot - Section 7](section7-nautobot.md)

[Introducing PyNautobot - Section 8](section8-pynautobot.md)

[Querying your device data from nautobot - Section 9](section9-querynautobot.md)

[Full configuration Jinja Templates - Section 10](section10-jinja_templates.md)

[Using the Nautobot Inventory module as your inventory source - Section 11](section11-nautobot-inventory.md)

[Nautobot Webhooks - Section 12](section12-nautobot-webhooks.md)