## Section 7: Building a full device configuration
<!-- {% include section5.html %} -->

We have built out our roles to deploy our pod. Now lets take a look at how we could develop a playbook and Jinja templates to build out all of our device configurations. What if we would like to store our "golden configuration" and validate that the existing device configuration matches our "golden configuration"? There are lots of tools our there that help an organization track what is called "configuration drift". This is the difference of a device configurations from its intended configuration. One of the many things automation helps us do is keep devices contained to the intended configuration so that our network is performing as expected. This keeps our unexpected type outages at a minimum which it a lot of cases is due to a bad configuration, or a mistake or old configuration that was never removed.  

### Building a full device Jinja template
The first thing we will want to tackle is how do we building a full device configuration template in Jinja. There are a few different approaches. We could take all of the components we created for our POD deployment and just stick those into a single template. This will work, but could create issues if we wanted to also have a way to perform separate tasks like interface description changes or updating a network to be advertised in OSPF or BGP. We would not want to have two versions or 3 versions of a very similar tasks floating around out there.

We will take a modular approach to assembling a full configuration template with in Jinja. We will keep our Jinja templates separated and use an include statement to use the modular templates as needed. Lets break it down.







[Installing Ansible - Section 1](installing_ansible.md)

[Creating an Inventory File - Section 2](inventory_file.md)

[Creating a playbook - Section 3](first_play.md)

[Building Roles - Section 4](building_roles.md)

[Building the core switch Roles - Section 5](section5-coreswitch.md)

[Building the router Roles - Section 6](section6-router.md)



