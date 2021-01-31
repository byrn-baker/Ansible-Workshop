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
        a. Access ports for Users, Servers, and Guests
        b. Layer 2 trunk to the core switches
2. (2) Core switches
        a. Layer 2 trunk ports to the access switch
        b. Layer 2 port channel between both core switches
        c. SVIs for the Users, Servers, and Guest vlans
            1. VRRP protocol for redunancy
        d. Layer 3 P2P interfaces as UPLINKS to the router
        e. Loopback0 interface to facilitate iBGP protocol
        f. OSPF protocol to facilitate iBGP protocol
        g. iBGP protocol to advertise Users, Servers, and Guest subnets to the router
3.  (1) Router
        a. Layer 3 P2P interfaces as DOWNLINKS to the core switches
        b. Loopback0 interface to facilitate iBGP protocol
        c. OSPF protocol to facilitate iBGP protocol
        d. iBGP protocol to receive advertised Users, Servers, and Guest subnets from the core switches
        e. eBGP protocol to advertise Users, Servers, and Guest subnets to the ISP and receive a default route from the ISP
        f. DHCP server for Users, Servers, and Guest subnets
The Lab diagram below consists of the IP addressing for each POD. The (x) will be replaced with the POD number you are using. 
### Lab Pod Diagram

![Lab Pod diagram](https://github.com/TwistByrn/Ansible_Workshop/blob/main/images/Ansible-WorkShop.png)
