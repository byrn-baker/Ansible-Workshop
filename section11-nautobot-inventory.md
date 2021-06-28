## Nautobot Inventory
Replacing the static inventory files with the Nautobot Inventory module is the last piece of the puzzle in getting rid of  the static group and host vars files. You check out the docs on how to use Nautobot Inventory [here](https://nautobot-ansible.readthedocs.io/en/latest/plugins/inventory_inventory.html#ansible-collections-networktocode-nautobot-inventory-inventory). I will still keep one static file under ```group_vars/all/all.yaml``` which holds the device username and password as well as the nautobot url and token. This is a demo instance and you would not want to store either of these in clear text. 

```
### inventory/nautobot_inventory.yaml
---
plugin: networktocode.nautobot.inventory
api_endpoint: "https://192.168.130.204"
token: "c7fdc6be609a244bb1e851c5e47b3ccd9d990b58"
validate_certs: False
config_context: False
group_by:
  - device_roles
query_filters:
  - site: 'pod1'
device_query_filters:
  - has_primary_ip: 'true'
compose:
  ansible_network_os: platform.name
  ansible_host: primary_ip4.address | ipaddr('address')
```

We want to group and filter our responses to mimic the inventory file. We want to group by device_roles which should be pod_router, pod_l3_switch, pod_l2_switch. I am working with pod1 so my filter will only pull the pod1 site. We can drill down further and filter out any device without a primary_ip configured. The compose section is used to take existing variables and transform those into something that Ansible can use. We transform the nautobot ```platform.name``` into ```ansible_network_os```
Ansible needs to know the type of network device it is connecting to when using vendor specific modules. If you are not using DNS then the hosts IP address will also be needed so we tranform the devices ```primary_ip4.address``` to ``` ansible_host```

We can test this new inventory file with ```ansible-inventory -v --list -i inventory/nautobot_inventory.yaml``` this will give you an output with devices based on our filters and groups, you should also see our 2 composed items as well. 



[Installing Ansible - Section 1](installing_ansible.md)

[Creating an Inventory File - Section 2](inventory_file.md)

[Creating a playbook - Section 3](first_play.md)

[Building Roles - Section 4](building_roles.md)

[Building the core switch Roles - Section 5](section5-coreswitch.md)

[Building the router Roles - Section 6](section6-router.md)

[Introducing Nautobot - Section 7](section7-nautobot.md)

[Introducing PyNautobot - Section 8](section8-pynautobot.md)

[Querying your device data from nautobot - Section 9](section9-querynautobot.md)

[Full configuration Jinja Templates - Section 10](section10-jinja_templates.md)