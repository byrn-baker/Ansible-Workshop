## Section 7: Introducing a source of truth to our Ansible workflow 
<!-- {% include section5.html %} -->

We have built out our roles to deploy our pod. Now lets take a look at how we can replace all of the group_vars, host_vars, and inventory folders and files with a database. To do this we will take a look at a tool called [Nautobot](https://www.networktocode.com/nautobot/)

### What is Nautobot?
*At its core, Nautobot is a Source of Truth that defines the intended state of the network. Throw away those spreadsheets and deploy a trusted source of data that enables good data hygiene. Nautobot enables strict adherence to data standards allowing users to define business rules on the network data that is stored within Nautobot. Nautobot also allows organizations to define custom fields and their own unique relationships between data stored in Nautobot showcasing its flexibility.*

I hope that helps, the basics are its a web app on top of a database that allows us to visualize the placement and locations of our hardware along with the ability to trace out and document the connections between them. The reason we will be working with it:
1. It's open source
2. Network to code (NTC) actively develops this project
3. There is robust support for Ansible and Python to query for data stored in Nautobot

NTC provides a couple of  ways for us to set this tool up. We can use a docker container, or follow the [docs](https://nautobot.readthedocs.io/en/latest/) and install it on a Linux VM. 









[Installing Ansible - Section 1](installing_ansible.md)

[Creating an Inventory File - Section 2](inventory_file.md)

[Creating a playbook - Section 3](first_play.md)

[Building Roles - Section 4](building_roles.md)

[Building the core switch Roles - Section 5](section5-coreswitch.md)

[Building the router Roles - Section 6](section6-router.md)



