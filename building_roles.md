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
* ```cisco.ios.ios_config:``` - This tells Ansible the module we want to use in the task. These modules use name space similar to a dns record. The cisco.ios.ios_config module has a couple different ways to push configurations to an IOS device. For our purposes we will use jinja templates method.
*   ```src: add_vlan.j2``` - This tells Ansible what file in the templates folder to use in rendering our text that will be pushed to the cisco device.
* ```ios_config:``` - This second task simply tells Ansible to perform a write memory after passing the rendered text via the SSH connection. 
*  ```save_when: always``` - This does exactly what is says. The ios_config module has a few options on when to save the configuration to startup (write memory). [Check out the ios module readme docs](https://docs.ansible.com/ansible/latest/collections/cisco/ios/ios_config_module.html) The ios_config module attempts to provide some idempotency and so if no changes are actually made to the configuration you could tell the module not to perform a write memory.

Create a new file under 'add_vlan/templates/ called 'add_vlan.j2'. this will store our Jinja2 template that will utilize the host_vars we created above. Jinja templates print out the text in the file while give you the ability to insert predefined variables at any location in the text that you wish. Ansible holds this information in memory and the cisco IOS module pushes the full text to our switch similar to a copy and paste from an SSH session on the CLI. [Check out this blog post from Network to Code](https://blog.networktocode.com/post/Jinja2_assemble_strategy/)

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