## Section 8: Introducing pynautobot
So we just walked through building out a couple of yaml files to use with the Ansible Nautobot module. Now we are going to look at using the python nautobot module to import not just one pod, but all six pods created for this workshop originally. The benefit to using python is we can structure the yaml file using a more nested approach. Because I have six sites worth of yaml files I used Ansible to combine all of this into a single file to be consumed by python.

My pb.transform.data.yaml
```
---
- name: Load Nautobot
  connection: local
  hosts: localhost
  gather_facts: False

  vars_files:
   - vars/sites.yaml
   - vars/tags.yaml
   - vars/vrfs.yaml
   - vars/devices.yaml
   - vars/nodes_design.yaml
   - vars/custom_fields.yaml
   - vars/device_connections.yaml

  tasks:
  - name: transform into a single file
    template: 
      src: "transform.j2"
      dest: "/home/Nautobot_Workshop/pynautobot/nb_initial_load.yaml"
```

I have several files created under vars_files that I used to track all of the things I needed inside Nautobot.