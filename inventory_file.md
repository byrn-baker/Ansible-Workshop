## Section 2: Creating the inventory yaml file
{% include section2.html %}
[Ansible inventory Documentation can be found here](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html#) 
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
Each host will be defined under the lower groupings (routers, core_switches, and access_switches). We can store variables in our plays in these folders, including sensitive information like passwords. In this workshop, we will keep information like usernames and passwords under the group_vars/all folder in a file called "all.yml" If you were to have devices or device groups that did not use the same password, then you could create a file of the device name under the host_vars/{{ device_name }} folder. In this workshop all devices share login and OS. If you want to learn more about encrypting files with ansible use the ansible docs on [Ansible Vault](https://docs.ansible.com/ansible/latest/user_guide/vault.html)
```
---
###########################################
# Stored variables for login and device OS
###########################################

ansible_password: Labuser!23
ansible_user: pod1
ansible_network_os: ios
```

[Installing Ansible - Section 1](installing_ansible.md)

[Creating a playbook - Section 3](first_play.md)

[Building Roles - Section 4](building_roles.md)

[Building the core switch Roles - Section 5](section5-coreswitch.md)

[Building the router Roles - Section 6](section6-router.md)

[Introducing Nautobot - Section 7](section7-nautobot.md)

[Introducing PyNautobot - Section 8](section8-pynautobot.md)

[Querying your device data from nautobot - Section 9](section9-querynautobot.md)

[Full configuration Jinja Templates - Section 10](section10-jinja_templates.md)

[Using the Nautobot Inventory module as your inventory source - Section 11](section11-nautobot-inventory.md)

[Nautobot Webhooks - Section 12](section12-nautobot-webhooks.md)