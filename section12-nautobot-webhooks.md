# Nautobot Webhooks
To recap a little bit, we are using Nautobot as our network source of truth, Ansible no longer needs static host_vars or a static inventory. All of these details can be pulled dynamically from Nautobot, then that data is run through a Jinja template and pushed to the devices. So now that the initial configuration is managed in this way what about day to day operational changes? Can we keep the devices and Nautobot in sync? 

Like anything the answer is, it depends. Nautobot does provide the ability to create Webhooks that could be used with something like Ansible Tower to kick off jobs in the event that Nautobot detects a change in the database. You can checkout the documentation [here](https://nautobot.readthedocs.io/en/stable/models/extras/webhook/) and look at what is available for you with Webhooks.

We are going to look at integrating Nautobot and Tower to kick off a Job each time Nautobot sees an update to a device interface. Webhooks allows us to build an API request and insert stuff into the body of the request in a Jinja style format. In the body of the request we can building key:values in a Jinja2 format that can be used on Tower when starting a job.

## Things we need:
1. AWX/Tower running in a development environment (I will be using Version 17.1.0)
2. Authorization token from the AWX/Tower environment - These are in different places depending on your version. It will require some googling on your end.
3. Git to sync the playbooks to AWX/Tower
4. Ansible Playbooks that will be used on AWX/Tower to execute the device changes



## AWX/Tower
There are plenty of places to find easy guides to getting a AWX instances up and running [Here is one](https://www.linuxtechi.com/install-ansible-awx-on-ubuntu/). Once you have your AWX instance running we need to get a few things configured.

The first thing we want to grab is your users API token. You can find this by navigating in your browser to ```http://awx_host/api/v2/tokens``` this should display the users OAuth2 token which will be needed to launch plays via the API on AWX.
<img src="/assets/images/section12_awx_api.png" alt="">

Next we need to get an inventory and a Project setup. Inside of AWX/Tower the terms change as compared to Ansible. The Ansible working folder in AWX/Tower is called a Project, the Anisble playbooks in AWX/Tower are called Templates, and when the running the playbook is refered to in AWX/Tower as a Job.

Like Ansible we need to have several things built before we can create a Job that makes changes to our devices. So open up AWX on your browser and you should be presented with the Dashboard after login. On the Left side you have a nav bar the resources section is where we will be adding things like, Inventories, Credentials, Projects, and Templates. 
<img src="/assets/images/section12_dashboard.png" alt="">

### AWX/Tower Credentials
Lets add credentials into AWX/Tower:
<img src="/assets/images/section12_credentials.png" alt="">

1. Github
We will build the playbooks inside of VSCODE so that we can test that the task works correctly before launching from AWX/Tower we will sync that progress on github and AWX/Tower will sync the repo before it runs the Job that makes changes do our physical devices. So create a new folder and a new repo for this project. You will want to generate an SSH key pair to use between AWX/Tower and Github as well. The Public key gets added to Github and the Private key will be added into AWX/Tower. In the below screenshot I've selected the credential type as Source Control and pasted in the private key in the SCM Private Key section. Save it.
<img src="/assets/images/section12_github.png" alt="">

2. Physical Device Login
This will be used by AWX/Tower to login to your physical device to make the required changes. Add a new Credential and select 'Machine' from the Credential Type, and put your devices username and password in below that or you can also use an SSH key. Depending on how you setup your usernames on the device you can also include Privilege escalations passwords. Mine are blank because on Cisco the username I am using has Priv 15 at login.
<img src="/assets/images/section12_pod1creds.png" alt="">

### AWX/Tower Inventory
Now that we have Credentials lets build out our inventory. Click 'Add' and select 'Add Inventory', give it a nameand save it. Once created we can then add hosts.
<img src="/assets/images/section12_inventory.png" alt="">

Click on your new inventory and click the 'Hosts' menu on the top. Here is where you can add each of the hosts and its specific variables if you have any.
<img src="/assets/images/section12_inventory_hosts.png" alt="">

The Host details are pretty simply as it just requires a name, now if you are not using DNS resolution you will need to add some variables in the same fashion we used in our Ansible inventory YAML file. In this example I have 3 Variables, Hosts IP, Hosts Network, and the Hosts SSH args. The SSH args will allow AWX/Tower to connect to our lab Cisco VM which uses out dated SSH keys so this is required for AWX/Tower to connect via SSH to those Cisco VMs. Repeat that process for each host you would like to have in your inventory.
<img src="/assets/images/section12_hosts_podr1.png" alt="">

### AWX/Tower Projects
We need a Project to pull our playbooks that we will write in VSCODE and sync to github.
<img src="/assets/images/section12_projects.png" alt="">

Add a new project by clicking the add button, give your project a name and select under Source Control Credential Type and choose Git from the drop down list. In the 'Type Details' paste in your github ssh url of the repo for this project. In the Source Control Credential select your Github credentials that you created in the previous step and then click save. This will kick off a job to sync the repo and you can watch that under the Jobs menu at the top left.
<img src="/assets/images/section12_webhook_job.png" alt="">

This will kick off a job to sync the repo and you can watch that under the Jobs menu at the top left.
<img src="/assets/images/section12_jobs.png" alt="">
<img src="/assets/images/section12_job_output.png" alt="">

### Build a Nautobot Webhook
In your nautobot there is a top menu called Extensibility that has a webhooks selection.
<img src="/assets/images/section12_extensibility.png" alt="">

This is where you create webhooks, lets add our 'Update_interfaces' hook.
<img src="/assets/images/section12_webhook.png" alt="">

Inside the webhook creation interface we have several options that will be filled out. Firstly the content type, and you can select more than one, will be what alerts the webhook to run. In our example we will use ```dcim|interface```, check enable, and check Type Update. What this is doing is watching for database update changes on the ```dcim|interface``` table. Notice that when you edit objects in the web interface there is an update button at the bottom. 

The URL will be the location of the template we will create in AWX/Tower, we need to build a playbook before we can create the template.

The HTTP Method will be POST, this is the method that AWX/Tower uses to kick off a template job because we need to send information to AWX/Tower so it knows what device and what port to update.

HTTP Content Type will be ```application/json``` and the Additional headers will need to include your authorization token from AWX/Tower prepended with ```authorization: Bearer```.

The Body Template is where we will build the JSON data that will be sent inside the API POST from Nautobot to AWX/Tower. Nautobot allows you to use a Jinja2 format which is nice because throughout this entire workshop we have been using Jinja templates. With Ansible you can provide "extra_vars" when running a playbook (```ansible-playbook myplaybook.yaml --extra-vars "nodes=webgroup”``` read more [here](https://www.redhat.com/sysadmin/extra-variables-ansible-playbook)) we have that same ability to do this from inside a AWX/Tower job template. We are going to utilize this function in our webhook. We will build our JSON structure and indent everything that will be pulled from Nautobot below ```"extra_vars":```. The key/value pairs will need to be matched in our playbooks so use something that is easy to identify as your work out how to pull the data you need from Nautobot. There are helpful docs [here](https://nautobot.readthedocs.io/en/stable/models/extras/webhook/) that will assist in building and testing your webhook. The troubleshooting section will be a big help with understanding how the WebHook formats the API Post and allow you to see how the JSON is being structured and it is populating the data you want. 

I am going to pause here and show how you can use the troubleshooting section to understand what the body looks like in the API Post.

Make a Tshooting webhook and point the URL at http://localhost:9000/ and in the body put this 

{% raw %}
```
{
 "extra_vars":   {
    "device_id": "{{ data }}"
                }
}
```
{% endraw %}

<img src="/assets/images/section12_webhook_tshoot.png" alt="">

Open up an ssh session to your nautobot host and run ```nautobot-server webhook_receiver```

Now update an interface on one of your devices, change the description. Once you click update you should see in your ssh session to Nautobot data returned like this 

<img src="/assets/images/section12_terminal.png" alt="">

What we get back are all of the information that Nautobot has on the specific interface that was just updated. So we can use this JSON data to sort through and pick out the items that will be needed to update the interface on a device. 

So using this output as a guide lets build the Body Template to express the values we will need in our playbook.

{% raw %}
```
{
    "extra_vars": {
        "device_id": "{
            'id': 'e0a6a63f-bcd0-43ea-ad30-5f35b74096de', 
            'url': '/api/dcim/interfaces/e0a6a63f-bcd0-43ea-ad30-5f35b74096de/', 
            'device': OrderedDict([
                ('id', '3bc81e37-8d9b-441b-85a0-c68043e2fd72'), 
                ('url', '/api/dcim/devices/3bc81e37-8d9b-441b-85a0-c68043e2fd72/'), 
                ('name', 'pod1sw3'), 
                ('display', 'pod1sw3')]), 
        'name': 'GigabitEthernet1/1', 
        'label': 'access', 
        'type': OrderedDict([('value', '1000base-t'), ('label', '1000BASE-T (1GE)')]), 'enabled': True, 
        'lag': None, 'mtu': 1500, 
        'mac_address': None, 
        'mgmt_only': False, 
        'description': 'GUESTS', 
        'mode': OrderedDict([('value', 'access'), ('label', 'Access')]), 
        'untagged_vlan': OrderedDict([('id', '2718a3f6-87a4-40bc-9bf1-a1304445a3b7'), ('url', '/api/ipam/vlans/2718a3f6-87a4-40bc-9bf1-a1304445a3b7/'), ('vid', 400), ('name', 'GUESTS'), ('display', 'GUESTS (400)')]), 
        'tagged_vlans': [], 
        'cable': None, 
        'cable_peer': None, 
        'cable_peer_type': None, 
        'connected_endpoint': None, 
        'connected_endpoint_type': None, 
        'connected_endpoint_reachable': None, 
        'tags': [], 'count_ipaddresses': 0, 
        'custom_fields': {
            'dhcp_helper': '', 
            'isis': None, 
            'isis_metric': None,
            'isis_p2p': None, 
            'mpls': None, 
            'rsvp': None, 
            'rsvp_bw': None, 
            'vrrp_description': '', 
            'vrrp_group': None, 
            'vrrp_primary_ip': '', 
            'vrrp_priority': None}, 
            'display': 'GigabitEthernet1/1 (access)'}"
    }
}
```
{% endraw %}

We can see that the device name is located in ```data['device']['name']```, the interface name is located in ```data['name']```.  You can see a pattern emerging, we can just go through this dictionary and pull out the items we need. A few of the other things we can use will be 

* mode
* untagged_vlan
* tagged_vlans
* description
* enabled
* mtu
* dhcp_helper
* vrrp_description
* vrrp_group
* vrrp_primary_ip
* vrrp_priority

We don't have to use all of these in a single task and can break tasks down into smaller changes, like just the description, or just the mtu and so on. The finished Body Template will look like this in our interface_update webhook, you don't need anything in the secret box, and uncheck SSL verification, this is development and I do not have a authorized certificate on the AWX server.

{% raw %}
```
{
 "extra_vars":   {
    "device_id": "{{ data['device']['name'] }}",
    "interface_id": "{{ data['name'] }}",
    "label": "{{ data['label'] }}",
    "mode": "{{ data['mode']['value'] }}",
    "untagged_vlan": "{{ data['untagged_vlan']['vid'] }}",
    "tagged_vlans": "{{ data["tagged_vlans"] | join(',', attribute='vid') }}",
    "description": "{{ data['description'] }}",
    "enabled": "{{ data['enabled'] }}",
    "mtu": "{{ data['mtu'] }}",
    "dhcp_helper": "{{ data['custom_fields']['dhcp_helper'] }}",
    "vrrp_description": "{{ data['custom_fields']['vrrp_description'] }}",
    "vrrp_group": "{{ data['custom_fields']['vrrp_group'] }}",
    "vrrp_primary_ip": "{{ data['custom_fields']['vrrp_primary_ip'] }}",
    "vrrp_priority": "{{ data['custom_fields']['vrrp_priority'] }}"
                }
}
```
{% endraw %}

Now that we understand the data being provided from Nautobot lets start working on a playbook and tasks that will be able to use the data.

### Ansible Playbooks
So now that we have AWX mostly setup and we have messed around with webhooks lets focus on the playbooks we will need to change a device ports physical attributes. In this example we will focus on making changes to the following:

1. Update physical attributes like description, mtu, and shut or no shut.
2. Update the type of interface, access, trunk, and what vlan is assigned
3. adding or updating layer3 information like and ip address, dhcp helper, vrrp information.

#### Playbook and Tasks
Playbooks for AWX/Tower look the same for the most part, however because we are going to kicking these off from a Webhook in Nautobot we need to build into our Playbooks and tasks variables.

```
---
- name: Nautobot Webhook interface update
  hosts: "{{ device_id }}"
  gather_facts: no
  connection: network_cli
  
  roles:
  - { role: updates_from_nautobot/physical_port_update }
```

In the play above we use ``` {{ device_id }}``` because that is the name we chose for our device name variable. This should also match exactly to our inventory.  I will continue to use Roles, so our tasks will be under ```roles/updates_from_nautobot/physical_port_update```. 

Our first task lets do something simple and update the interface description, and the administrative status (enabled or not). Because I am working with Cisco devices I will also be using the cisco ios ansible module. These vendor specific modules are really handy when we are making small changes to specific items on the device. Have a look at the docs for [cisco.ios.interfaces](https://github.com/ansible-collections/cisco.ios/blob/main/docs/cisco.ios.ios_interface_module.rst) This describes what we can change on the interface with this module and provides several different examples. 

```
---
- name: update interface description and admin status
  cisco.ios.ios_interfaces:
    config:
    - name: "{{ interface_id }}"
      description: "{{ description }}"
      enabled: "{{ enabled }}"   
    state: replaced
```

In this first task if we update anything on the interface is will kick off the Webhook which will in turn kick off the job template. Above we will use ```{{ interface_id }}``` to indentify which interface to make changes to, ```{{ description }}```, and ```{{ enabled }}```. 

We need to present all of our variables as extra-vars of the play will fail as we are not checking if a variable exists before running the play, so these will required for this task to be run. Name and Description are self explanitory, enabled however is neither shut or no shut, however it performs that function when called in our ansible task. Enabled uses a yes or no, True or False boolean choice which is perfect because Nautobot uses the same boolean on its end.

You can also test this playbook directly from the command line by the following ```ansible-playbook -i inventory/pod1_inventory.yml pb.update_port_description.yaml --extra-vars "device_id=pod1sw3 interface_id=GigabitEthernet0/0 description=ANSIBLE_TEST enabled=yes"```. 

You should have an output similar to this:

```
(.venv) root@c1557e2bca38:/home/Ansible-AWX-Workshop# ansible-playbook -i inventory/pod1_inventory.yml pb.update_port_description.yaml --extra-vars "device_id=pod1sw3 interface_id=GigabitEthernet0/0 description=ANSIBLE_TEST enabled=no"

PLAY [Nautobot Webhook interface update] ***********************************************************************************************************************************************************************************************

TASK [updates_from_nautobot/physical_port_update : update interface description and admin status] **************************************************************************************************************************************
ok: [pod1sw3]

PLAY RECAP *****************************************************************************************************************************************************************************************************************************
pod1sw3                    : ok=1    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
```

Notice that nothing has been changed, the cisco module is looking at the current state of the interface and because it is already enabled and the description is already set to "ANSIBLE_TEST" on my device there is no change which ansible registers. 

```
pod1sw3#sh int description 
Interface                      Status         Protocol Description
Gi0/0                          admin down     down     ANSIBLE_TEST
Gi0/1                          up             up       TRUNK TO POD1SW1
Gi0/2                          up             up       TRUNK TO POD1SW2
Gi0/3                          up             up       USERS
Gi1/0                          down           down     SERVERS
Gi1/1                          down           down     GUESTS - Webhooks
Gi1/2                          down           down     NOT IN USE
Gi1/3                          up             up       MGMT-INTERFACE
```

Run the play again except this time lets change the description

```
(.venv) root@c1557e2bca38:/home/Ansible-AWX-Workshop# ansible-playbook -i inventory/pod1_inventory.yml pb.update_port_description.yaml --extra-vars "device_id=pod1sw3 interface_id=GigabitEthernet0/0 description=TEST enabled=no"

PLAY [Nautobot Webhook interface update] ***********************************************************************************************************************************************************************************************

TASK [updates_from_nautobot/physical_port_update : update interface description and admin status] **************************************************************************************************************************************
changed: [pod1sw3]

PLAY RECAP *****************************************************************************************************************************************************************************************************************************
pod1sw3                    : ok=1    changed=1    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0  
```

Here we register a change and below is the output from the switch show command

```
pod1sw3#
*Jul 29 18:15:42.346: %SYS-5-CONFIG_I: Configured from console by pod1 on vty0 (192.168.130.141)
pod1sw3#sh int description 
Interface                      Status         Protocol Description
Gi0/0                          admin down     down     TEST
Gi0/1                          up             up       TRUNK TO POD1SW1
Gi0/2                          up             up       TRUNK TO POD1SW2
Gi0/3                          up             up       USERS
Gi1/0                          down           down     SERVERS
Gi1/1                          down           down     GUESTS - Webhooks
Gi1/2                          down           down     NOT IN USE
Gi1/3                          up             up       MGMT-INTERFACE
pod1sw3#
```

