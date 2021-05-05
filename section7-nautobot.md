## Section 7: Introducing a source of truth to our Ansible workflow 
<!-- {% include section5.html %} -->

We have built out our roles to deploy our pod. Now lets take a look at how we can replace all of the group_vars, host_vars, and inventory folders and files with a database. To do this we will take a look at a tool called [Nautobot](https://www.networktocode.com/nautobot/)

### What is Nautobot?
*At its core, Nautobot is a Source of Truth that defines the intended state of the network. Throw away those spreadsheets and deploy a trusted source of data that enables good data hygiene. Nautobot enables strict adherence to data standards allowing users to define business rules on the network data that is stored within Nautobot. Nautobot also allows organizations to define custom fields and their own unique relationships between data stored in Nautobot showcasing its flexibility.*

I hope that helps, the basics are its a web app on top of a database that allows us to visualize the placement and locations of our hardware along with the ability to trace out and document the connections between them. The reason we will be working with it:
1. It's open source
2. Network to code (NTC) actively develops this project
3. There is robust support for Ansible and Python to query for data stored in Nautobot

### Setup Nautbot
NTC provides a couple of  ways for us to set this tool up. We can use a [docker](https://hub.docker.com/r/networktocode/nautobot-lab) container, or follow the [docs](https://nautobot.readthedocs.io/en/latest/) and install it on a Linux VM. 

For our demonstration purposes we will be using the docker container. Following these [instruction](https://github.com/nautobot/nautobot-lab) get it up and running. We will not need to load the mock data as we will be creating our own data to match our pod deployment. Create a super user from within the docker container, once that is done we should be good to start using Nautobot. Assuming you are running the container on your local machine navigate your browser to localhost:8000

### Building the data into Nautobot
Now that we have Nautobot running, we want to start filling it with the relevant data we created during our previous sections deploying the pod from Ansible.  Nautobot provides multiple options for importing data into the tool. You can import via CSV structure, you can use the Ansible module, or you can use pynautobot. We will continue to use Ansible for our demonstration and push the required data into Nautobot with its Ansible module.

Let's talk about the data requirements are in Nautobot:
1. Token that is used for the API calls 
2. Site for our pod.
3. Rack that will reside at our site.
4. Manufacturer of the equipment installed at this site.
5. Device Type of the equipment associated to the manufacturer
6. Platform (OS) that the device type will be using (ios, iosxr, junos, etc)
7. Device roles that will group the devices together (router, l3 switch, l2 switch, etc)
After all of this has been created we can start adding the specific devices to our site and installed into our rack. You will need to generate a token, to do that you will want to navigate to https://localhost:8000 and login with your super user account created when you setup the container. On the top right you will see your super user name. When you click the name you are presented with a dropdown menu that contains profile, admin, and log out.
<img src="/assets/images/nautobot_admin_panel.png" alt="">
<img src="/assets/images/nautobot_admin_panel2.png" alt="">
Click the admin button. This will take you to a new admin page and you will see under USERS there is a button to add Tokens.
<img src="/assets/images/nautobot_admin_panel3.png" alt=""> 
This token will be used in our Ansible playbooks to interact with the Nautobot API.



#### Creating the Ansible playbooks for data creation in Nautobot
The Ansible module for Nautobot is detailed here and provides examples for how to construct the playbooks that will interact with Nautobot.

Our first playbook will focus on generating the site. We will be building six different sites to represent 6 different PODs. This will illustrate how easy it is to setup playbooks and do large batch imports in the future.

Create a playbook, I called mine nb.create.sites.yaml. We will be using this single playbook to perform all of the tasks above.

```
---
- name: Load Nautobot
  connection: local
  hosts: localhost
  gather_facts: False

  vars:
    nb_url: "https://localhost:8000"
    nb_token: "YOUR GENERATED TOKEN HERE"

  tasks:
#############################################################
# Create Site in Nautobot
#############################################################
    - include_vars: "nb_vars/sites.yaml"
    - name: Create site with all parameters
      networktocode.nautobot.site:
        url: "{{ nb_url }}"
        token: "{{ nb_token }}"
        validate_certs: no
        data:
          name: "{{ item.name }}"
          status: "{{ item.status }}"
          asn: "{{ item.asn }}"
          time_zone: "{{ item.time_zone }}"
          description: "{{ item.description }}"
          physical_address: "{{ item.physical_address }}"
          shipping_address: "{{ item.shipping_address }}"
          latitude: "{{ item.latitude }}"
          longitude: "{{ item.longitude }}"
          contact_name: "{{ item.contact_name }}"
          contact_phone: "{{ item.contact_phone }}"
          contact_email: "{{ item.contact_email }}"
          slug: "{{ item.slug }}"
          comments: "{{ item.comments }}"
        state: present
      loop: "{{ sites }}"
```








[Installing Ansible - Section 1](installing_ansible.md)

[Creating an Inventory File - Section 2](inventory_file.md)

[Creating a playbook - Section 3](first_play.md)

[Building Roles - Section 4](building_roles.md)

[Building the core switch Roles - Section 5](section5-coreswitch.md)

[Building the router Roles - Section 6](section6-router.md)



