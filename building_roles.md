## Section 4: Building Roles
We have several tasks to complete the deployment of our pod. We will be breaking each tasks down into its own play. This is called a [Role](https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html). This workshop Pod will be making use of the Cisco vIOS router and vIOS switch.

Lets create some folders to help structure where we will be placing data that will be used in our Ansible Plays.

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
```
Create a new file under 'inventory/group_vars/' called 'podx.yml'. In this file we will store our username and password for the assigned pod. Place the following text in your file:
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

Create a new file under 'add_vlan/meta/' called 'main.yml'. This file will pull the collection we are using to parse out from for our validation plays. This simply replaces the Collection section inside a standard playbook and assigns it to this task. Inside the meta.yml file place the following text:
```
collections:
  - clay584.parse_genie
```
Create a new file under 'add_vlan/tasks/' called 'main.yml'. This file will be structured similar to the Playbook we created to pull down a list of vlans from the podxsw3 host. In this play we will use a Jinja2 template to create and name the vlans for the 3 user groups (Users, Servers, Guests).

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
Lets go over what we are doing:
* ```name: Add new vlan to vlan database on {{ inventory_hostname }}``` - The name of the task appears in the Ansible console to let the operator know what is being performed in the background. ```{{ }}``` with Ansible anything between a double bracket is a variable and we can fill this in with anything available to Ansible like a hostname for example.