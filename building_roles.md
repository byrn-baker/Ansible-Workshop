## Section 4: Building Roles
{% include section4-part1.html %}
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
* ```name: Add new vlan to vlan database on {{ inventory_hostname }}``` - The name of the task appears in the Ansible console to let the operator know what is being performed in the background. "{{ }}" with Ansible anything between a double bracket is a variable and we can fill this in with anything available to Ansible like a hostname for example.
* ```src: add_vlan.j2``` - This tells Ansible what file in the templates folder to use in rendering our text that will be pushed to the cisco device.
* ```ios_config:``` - This second task simply tells Ansible to perform a write memory after passing the rendered text via the SSH connection. 
* ```save_when: always``` - This does exactly what is says. The ios_config module has a few options on when to save the configuration to startup (write memory). [Check out the ios module readme docs](https://docs.ansible.com/ansible/latest/collections/cisco/ios/ios_config_module.html) The ios_config module attempts to provide some idempotency and so if no changes are actually made to the configuration you could tell the module not to perform a write memory.

Create a new file under 'add_vlan/templates/ called 'add_vlan.j2'. this will store our Jinja2 template that will utilize the host_vars we created above. Jinja templates print out the text in the file while give you the ability to insert predefined variables at any location in the text that you wish. Ansible holds this information in memory and the cisco IOS module pushes the full text to our switch similar to a copy and paste from an SSH session on the CLI. [Check out this blog post from Network to Code](https://blog.networktocode.com/post/Jinja2_assemble_strategy/)

Lets take a look at add_vlan.j2

{% raw %}
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
{% endraw %}

Lets go over what we are doing:
* {% raw %}```#jinja2: lstrip_blocks: "True (or False)", trim_blocks: "True (or False)"```{% endraw %} - This line tells the Jinja template to remove any white space that is added before or after our IF statements or FOR statements. 
* {% raw %}```{# #}```{% endraw %} - These characters tell the jinja template not to render the text between the characters. This is what we call commenting and allows you to tell someone else reading your template what you are doing and why without rendering the text in the file output.
* {% raw %}```{% if configuration.vlans.vlan is not mapping and configuration.vlans.vlan is not string %}```{% endraw %} - This is looking to make sure our VLANs are actually a string of numbers and not text or some other character as anything other than a number would not be accepted by the cisco CLI.
* {% raw %}```{% if configuration.vlans is defined %}```{% endraw %} - Any 'IF' statement will always need to be followed with an {% raw %}```{% endif %}```{% endraw %}. In our case we will only render the below text 'if configuration.vlans exists or is defined' in our host_vars files otherwise move on to the next task. 
* {% raw %}```% for vlan in configuration.vlans.vlan %}```{% endraw %} - This line will always need to be followed with an {% raw %}```{% endfor %}```{% endraw %}. The 'FOR LOOP' is a loop and it will continue printing the text between {% raw %}```{% for vlan in configuration.vlans.vlan %}```{% endraw %} and {% raw %}```{% endfor %}```{% endraw %} until the entire list has been iterated through. This allows us to create an easy to read lists of things we want to configure in our host_vars files. In this case we created a list of vlans and its names in the '/host_vars/podxsw3/vlans.yml' file.
* {% raw %}```{% if vlan.name is defined %}```{% endraw %} - This line will print the name of the vlan if it has been included in our '/host_vars/podxsw3/vlans.yml' file. If it has not been defined then we just skip that portion of text in the rendering and move on to the next task.

{% include section4-part2.html %}
Create a new file under 'inventory/host_vars/podxsw3/' called 'access_interface.yml'. In this file we will create a list of access interfaces that we need to configure on our access switch.
Place the following text in your file:
```
---
configuration:
  interfaces:
    access:
      - name: Gi0/3
        description: "USERS"
        interface_mode: access
        vlan:
          members: "300"

      - name: Gi1/0
        description: "SERVERS"
        interface_mode: access
        vlan:
          members: "350"

      - name: Gi1/1
        description: "GUEST"
        interface_mode: access
        vlan:
          members: "400"
```

Create a new file under 'add_access_interface/meta/' called 'main.yml'. This file will pull the collection we are using to parse out from for our validation plays. This simply replaces the Collection section inside a standard playbook and assigns it to this task. Inside the meta.yml file place the following text:
```
collections:
  - clay584.parse_genie
```
Create a new file under 'add_access_interface/tasks/' called 'main.yml'. In this play we will again point to a Jinja2 template to configure our interfaces for the 3 user groups (Users, Servers, Guests).

In the main.yml file we will use the playbook tasks structure. Roles simply replace tasks of a playbook.

```
---
- name: configuring layer2 access interfaces on {{ inventory_hostname }}
  cisco.ios.ios_config:
    src: add_access_interface.j2

- name: Saving the running config on {{ inventory_hostname }}
  ios_config:
    save_when: always  
```
You will notice this play looks very similar to the add_vlan play. This is because we will reuse this method in each play and rely on the jinja templates to render our configuration that will be pushed each time with the cisco.ios.ios_config module.

Create a new file under 'add_access_interface/templates/ called 'add_access_interface.j2'. this will store our Jinja2 template that will utilize the host_vars we created above.

In the 'add_access_interface.j2' file place the following text:
{% raw %}
```
#jinja2: lstrip_blocks: "True (or False)", trim_blocks: "True (or False)"
{#- ---------------------------------------------------------------------------------- #}
{# configuration.interfaces.access                                                     #}
{# ---------------------------------------------------------------------------------- -#}
{% if configuration.interfaces.access is defined %}
{% for interface in configuration.interfaces.access %}
interface {{ interface.name }}
    {% if interface.description is defined %}
    description {{ interface.description }}
    {% endif %}
    switchport mode {{ interface.interface_mode }}
    switchport access vlan {{ interface.vlan.members }}
    no cdp enable
    no shut
{% endfor %}
{% endif %}
```
{% endraw %}

Lets go over what we are doing:
* {% raw %}```#jinja2: lstrip_blocks: "True (or False)", trim_blocks: "True (or False)"```{% endraw %} - This line tells the Jinja template to remove any white space that is added before or after our IF statements or FOR statements. 
* {% raw %}```{# #}```{% endraw %} - These characters tell the jinja template not to render the text between the characters. This is what we call commenting and allows you to tell someone else reading your template what you are doing and why without rendering the text in the file output.
* {% raw %}```{% if configuration.interfaces.access is defined %}```{% endraw %} - If configuration.interfaces.access is defined or exists continue with the enclosed rendering otherwise just skip this task and move on to the next task.
* {% raw %}```{% for interface in configuration.interfaces.access %}```{% endraw %} - This line starts our looping through the list we created in '/host_vars/podxsw3/access_interface.yml' file. The YAML indentation is important,each tab indicates that access is nested under interfaces, and name is nested under access. So when we are defining our loops we can rename the lists to whatever suits our needs best. Our example {% raw %}```{% for interface in configuration.interfaces.access %}```{% endraw %} names the nested list from configuration.interfaces.access to interfaces. This also tells Jinja that anything in a list under configuration.interfaces.access should continue to be kept as a separate list.  The '-' is how YAML shows that this is the start of a list.
* {% raw %}```interface {{ interface.name }}```{% endraw %} - This line calls for a variable from our list of interfaces. If you look at the '/host_vars/podxsw3/access_interface.yml' you will notice that under access we created 3 different lists with 4 variables. name, description, interface_mode, and vlan. As we progress down you should see that the tests looks similar to the IOS configuration output of a 'show run interface'. As stated above anything between a double bracket is a variable. 
* We will follow a similar format to our add_vlan jinja template and call out each variable that is necessary to configure an interface to our required standards. 
* {% raw %}```{% endfor %}```{% endraw %} tells Jinja that it can end the looping of the lists and the {% raw %}```{% endif %}```{% endraw %} tells Jinja that the lines between the if and the endif should only be rendered if the condition has been met. 

Create a new file under 'inventory/host_vars/podxsw3/' called 'trunk_interface.yml'. In this file we will create a list of trunk interfaces that we need to configure on our access switch.
Place the following text in your file:
```
---
configuration:
  interfaces:
    trunk:
      - name: Gi0/1
        description: "TRUNK TO POD1SW1"
        interface_mode: trunk
        native_vlan:
          members: "666"
        allowed_vlans:
            members: "300,350,400"

      - name: Gi0/2
        description: "TRUNK TO POD1SW2"
        interface_mode: trunk
        native_vlan:
          members: "666"
        allowed_vlans:
            members: "300,350,400"
```

Create a new file under 'add_trunk_interface/meta/' called 'main.yml'. This file will pull the collection we are using to parse out from for our validation plays. This simply replaces the Collection section inside a standard playbook and assigns it to this task. Inside the meta.yml file place the following text:
```
collections:
  - clay584.parse_genie
```
Create a new file under 'add_trunk_interface/tasks/' called 'main.yml'. In this play we will again point to a Jinja2 template to configure our interfaces for the 3 user groups (Users, Servers, Guests).

In the main.yml file we will use the playbook tasks structure. Roles simply replace tasks of a playbook.

```
---
- name: configuring layer2 trunk interfaces on {{ inventory_hostname }}
  cisco.ios.ios_config:
    src: add_trunk_interface.j2

- name: Saving the running config on {{ inventory_hostname }}
  ios_config:
    save_when: always  
```

Create a new file under 'add_trunk_interface/templates/ called 'add_trunk_interface.j2'. this will store our Jinja2 template that will utlize the host_vars we created above.

In the 'add_trunk_interface.j2' file place the following text:
{% raw %}
```
#jinja2: lstrip_blocks: "True (or False)", trim_blocks: "True (or False)"
{#- ---------------------------------------------------------------------------------- #}
{# configuration.interfaces.trunk                                                      #}
{# ---------------------------------------------------------------------------------- -#}
{% if configuration.interfaces.trunk is defined %}
{% for interface in configuration.interfaces.trunk %}
interface {{ interface.name }}
    {% if interface.description is defined %}
    description {{ interface.description }}
    {% endif %}
    {% if interface.native_vlan is defined %}
    switchport trunk native vlan {{ interface.native_vlan.members }}
    {% endif %}
    {% if interface.allowed_vlans.members is defined %}
    switchport trunk allowed vlan {{ interface.allowed_vlans.members }}
    {% endif %}
    {% if interface.allowed_vlans.add is defined %}
    switchport trunk allowed vlan add {{ interface.allowed_vlans.add }}
    {% endif %}
    switchport trunk encapsulation dot1q
    switchport mode trunk
    {% if interface.port_channel is defined %}
    channel-group {{ interface.port_channel }} mode active
    {% endif %}
    no shut
{% endfor %}
{% endif %}
```
{% endraw %}
You will notice a pattern here and that we are utilizing IF statements to perform tasks only if the variable is defined and loops to iterate through lists that we are creating in our host_vars. 

[Installing Ansible - Section 1](installing_ansible.md)

[Creating an Inventory File - Section 2](inventory_file.md)

[Creating a playbook - Section 3](first_play.md)