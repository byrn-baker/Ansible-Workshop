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

### Ansible Playbooks
So now that we have AWX mostly setup lets focus on the playbooks we will need to change a device ports physical attributes. In this example we will focus on making changes to the following:
1. 