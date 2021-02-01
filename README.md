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
ansible-galaxy collection install cisco.ios
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
Each host will be defined under the lower groupings (routers, core_switches, and access_switches).
 