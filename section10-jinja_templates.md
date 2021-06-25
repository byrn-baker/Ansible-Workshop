## Section 10: Building configuration Jinja templates
{% include section9.html %}

If you have been following along, we just finished building out the graphQL query that will pull the data we want back to Ansible. Now we will take that data and run it through Jinja templates that will create a complete device configuration. We will be using very similar approaches as sections 4, 5, and 6. The only difference is that a single playbook will be used to generate a complete configuration that should look as if you did a ```show run``` on your switch or router.

[Installing Ansible - Section 1](installing_ansible.md)

[Creating an Inventory File - Section 2](inventory_file.md)

[Creating a playbook - Section 3](first_play.md)

[Building Roles - Section 4](building_roles.md)

[Building the core switch Roles - Section 5](section5-coreswitch.md)

[Building the router Roles - Section 6](section6-router.md)

[Introducing Nautobot - Section 7](section7-nautobot.md)

[Introducing PyNautobot - Section 8](section8-pynautobot.md)

[Querying your device data from nautobot - Section 9](section9-querynautobot.md)