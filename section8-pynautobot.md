## Section 8: Introducing pynautobot
So we just walked through building out a couple of yaml files to use with the Ansible Nautobot module. Now we are going to look at using the python nautobot module to import not just one pod, but all six pods created for this workshop originally. The benefit to using python is we can structure the yaml file using a more nested approach. 


Check out the files [here](https://github.com/byrn-baker/Ansible-Workshop/tree/main/Python_Scripts)

I have several files created under vars that I used to track all of the things I needed inside Nautobot. My pb.transform.data.yaml playbook quickly combines everything into a single file for python to consume. 
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
      dest: "nb_initial_load.yaml"
```
This new file is called [nb_initial_load.yaml](https://github.com/byrn-baker/Ansible-Workshop/blob/main/Python_Scripts/nb_initial_load.yaml)

I would like to give a call out to [hpreston](https://github.com/hpreston/nxos-netbox-sync) and everyone who has been willing to answer my dumb questions in the nautobot slack channel.

The next piece of the puzzle is actually creating the python that will take all of this information and send it to Nautobot. Lets breakdown the [nautobot_load.py](https://github.com/byrn-baker/Ansible-Workshop/blob/main/Python_Scripts/nautobot_load.py) key sections. You will need to install pynautobot of course so lets start off by creating a virtualenv for our project. 


In your a new folder

```
pip3 install virtualenv
virtualenv .pynautobot_stuff
source .pynautobot_stuff/bin/activate
pip3 install pynautobot
```
You should have a prompt that is pre-pended with .pynautobot_stuff. Create a new file and lets call it nautobot_load.py
```
from pynautobot import api
import yaml 
```
Check out the readme [here](https://pynautobot.readthedocs.io/en/latest/). We need to import pynautobots API module and yaml. We are using YAML to format the data that this will be using.

```
data_file = "nb_initial_load.yaml"

with open(data_file) as f: 
    data = yaml.safe_load(f.read())
```
Next we open the file and read it into memory. 

```
nb = api(url="http://localhost:8000", token="YOUTOKEN")
nb.http_session.verify = False
```
Next we need to create a variable for our api url and token. We should already have one of these created from our previous section so we can use that here as well. The nb.http_session.verify = False will ensure that the API calls can be done without ssl. 

```
# sites: 
for site in data["sites"]: 
    print(f"Creating or Updating Site {site['name']}")
    nb_data = nb.dcim.sites.get(slug=site["slug"])
    if not nb_data: 
        nb_data = nb.dcim.sites.create(name=site["name"], slug=site["slug"])
```
Let do this in order again the same way we did with the Ansible playbooks. We need the sites first so that we can associate things like vlans, prefixes, and relay racks. Notice this is sort of similar to how we make for loops in Jinja. The concepts are similar and so hopefully there is a little bridge created between the two languages and helps us read what is happening. We will loop through anything inside of the hash of ```data["sites"]``` Print simply prints to the terminal, so in our case we will let the person behind the terminal know what task is being performed. Next we create a variable called nb_data, this variable will be the output of the ```nb.dcim.sites.get(slug=site["slug"])```. So if you curious what the heck that is doing, we can jump to the python interpreter and see what is does.

In your terminal type ```python3``` and you should see something like this

```
Python 3.8.5 (default, Jan 27 2021, 15:41:15) 
[GCC 9.3.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> 
```

Next we need to import pynautobot and create the variables for the api call.

```
>>> from pynautobot import api
>>> nb = api(url="http://localhost:8000", token="YOURTOKEN")
>>> nb.http_session.verify = False
```

Now lets see what ```nb.dcim.sites.get(slug=site["slug"])``` does inside of python. Something to note, most of the calls we will make will require the slug if you want to get the information by name. All of the data inside the database uses a UUID and so in a lot of cases we will need that UUID of the data base entry to get the data we want.

```
>>> nb.dcim.sites.get(slug="pod1")
POD1
>>> nb.dcim.sites.get(slug="pod1").id
'c9fd1612-4031-477e-a185-5d2e231e616b'
```

So we get a response from nautobot and because it returns a result we have a site that already exists. Lets look at a site we don't have

```
>>> nb.dcim.sites.get(slug="pod26")
>>> 
```

No results are returned so that tells us we don't have an object with that slug. Lets create a site now and see what that looks like, if we look up the API call that will be used to create the site we will be able to see what items are required along with what else can be sent through the API to Nautobot. Navigate to http://localhost:8000/api/docs/
<img src="/assets/images/nautobot_api_1.PNG" alt="">

What you are seeing here is a list of the different Nautobot Apps that the API can access or add data to. We will be doing most of our work inside the DCIM App and dealing with different models with that App like sites, manufacturers, and device_types as you can see below. We will spend a lot of time here browsing through the API docs understanding what is required and what else we can add to each model that we are interested in. Lets look at creating a site. Scroll down to the /dcim/sites and look at the POST section.
<img src="/assets/images/nautobot_api_2.PNG" alt="">
The data that is required to create a site is the name and slug. Everything else is optional and not a requirement. So lets have a look at creating a site via pynautobot.

```
>>> nb.dcim.sites.create(name='POD26', slug='pod26', status='active')
POD26
>>> nb.dcim.sites.get(slug="pod26").id
'80ea0c8e-57bf-4b6a-b507-be4afa475d03'
>>>
```

We know have a site called POD26. Lets check the Webapp and see what it looks like as well.
<img src="/assets/images/nautobot_api_3.PNG" alt="">
We see that on the right side a record of the change we just made. 
<img src="/assets/images/nautobot_api_4.PNG" alt="">
We also see that we know have a page for the site created. So perfect we can see how easy it is to add items to Nautobot via pynautobot.

```
if not nb_data: 
        nb_data = nb.dcim.sites.create(name=site["name"], slug=site["slug"])
```

So ```nb_data = nb.dcim.sites.get(slug=site["slug"])``` is looking at our ```nb_initial_load.yaml``` looping through all the sites and asking if the site slug exists in nautobot, those results are then checked by an if statement and if nothing is returned for the site in our ```nb_initial_load.yaml``` it will create that site with just the basic data required (name, slug, and the status). What if we wanted to add more than the required items? We want to make sure that the script doesn't fail if these are not "required", so pynautobot allows us to update an existing entry, and we will right some if statements to check of the fields are defined or not before attempting to update the site. Lets take a look at what an update requires. So models require the slug to update, and some models require the id. In the case of a site we need to have the slug to update fields in a specific site.

```
nb_site = nb.dcim.sites.get(slug='pod26')
>>> nb_site.asn = '65026'
>>> nb_site.save()
True
>>>
```

We will create a new variable called nb_site and call for the sites slug, which will be stored now as nb_site. Then we can take this variable and access or add to any field available. Here we simply update the BGP ASN and then save this update. 
<img src="/assets/images/nautobot_api_5.PNG" alt="">

Notice the change log has POD26 modified and we can see that the ASN is now populated.
<img src="/assets/images/nautobot_api_6.PNG" alt="">

```
# manufacturers 
for manufacturer in data["manufacturers"]: 
    print(f"Creating or Updating Manufacture {manufacturer['name']}")
    nb_data = nb.dcim.manufacturers.get(slug=manufacturer["slug"])
    if not nb_data: 
        nb_data = nb.dcim.manufacturers.create(name=manufacturer["name"], slug=manufacturer["slug"])

# device_types
for device_type in data["device_types"]: 
    print(f"Creating or Updating device_type {device_type['model']}")
    nb_data = nb.dcim.device_types.get(slug=device_type["slug"])
    if not nb_data: 
        nb_data = nb.dcim.device_types.create(
            model=device_type["model"], 
            slug=device_type["slug"], 
            manufacturer=nb.dcim.manufacturers.get(slug=device_type["manufacturer_slug"]).id, 
            height=device_type["height"]
            )

# device_roles
for device_role in data["device_roles"]: 
    print(f"Creating or Updating device_role {device_role['name']}")
    nb_data = nb.dcim.device_roles.get(slug=device_role["slug"])
    if not nb_data: 
        nb_data = nb.dcim.device_roles.create(
            name=device_role["name"], 
            slug=device_role["slug"], 
            color=device_role["color"]
            )

# platforms
for platform in data["platforms"]: 
    print(f"Creating or Updating platform {platform['name']}")
    nb_data = nb.dcim.platforms.get(slug=platform["slug"])
    if not nb_data: 
        nb_data = nb.dcim.platforms.create(
            name=platform["name"], 
            slug=platform["slug"], 
            manufacturer=nb.dcim.manufacturers.get(slug=platform["manufacturer_slug"]).id 
            )

# tags
for tag in data["tags"]:
    print(f"Creating or Updating tag {tag['name']}")
    nb_data = nb.extras.tags.get(slug=tag["slug"])
    if not nb_data:
        nb_data = nb.extras.tags.create(
            name=tag["name"],
            slug=tag["slug"],
            description=tag["description"]
        )
```

We will repeat this process throughout adding manufacturers, device types, device roles and platforms.

```
# custom fields
for cf in data["custom_fields"]:
    print(f"Creating or Updating Custom Fields {cf['name']}")
    nb_data = nb.extras.custom_fields.get(name=cf["name"])
    if not nb_data:
        nb_data = nb.extras.custom_fields.create(
            name=cf["name"],
            type=cf["type"],
            content_types=cf["content_types"],
            description=cf["description"]
        )
```        
Here is something new we did not cover before. Custom Fields are pretty handy for data that is not modeled in nautobot already. We are going to use it to store a dhcp helper and vrrp configuration items. We again look to make sure there is not already a custom field created and if not we create the custom field from our ```nb_initial_load.yaml```

```
custom_fields:
  - name: dhcp_helper
    description: Used to assign helper address to an interface
    type: text
    content_types:
      - dcim.interface
  - name: vrrp_group
    description:  Used to assign vrrp items to an interface
    type: integer
    content_types:
      - dcim.interface
  - name: vrrp_description
    description:  Used to assign vrrp items to an interface
    type: text
    content_types:
      - dcim.interface
  - name: vrrp_primary_ip
    description:  Used to assign vrrp items to an interface
    type: text
    content_types:
      - dcim.interface
  - name: vrrp_priority
    description:  Used to assign vrrp items to an interface
    type: integer
    content_types:
      - dcim.interface
```

Custom fields can be attached to several different tables in nautobot. For our use case we will attach these fields to interfaces only, we could attach them to multiple content types if you needed it. Nautobot also has an API explorer we can use to figure out what is needed to create the entries. Check out the demo [here](https://demo.nautobot.com/api/docs/)
<img src="/assets/images/nautobot_api.PNG" alt="">
Reviewing the API documentation here is crucial to figuring out what fields need to be filled out and what fields can be filled out. We will reference this often as we construct the rest of this script.

```
# vrfs 
for vrf in data["vrfs"]: 
    print(f"Creating or Updating vrf {vrf['name']}")
    nb_data = nb.ipam.vrfs.get(name=vrf["name"])
    if not nb_data: 
        nb_data = nb.ipam.vrfs.create(name=vrf["name"])
        if "rd" in vrf.keys():
            print(f"Configuring vrf {vrf['rd']}")
            vrf_rd = nb.ipam.vrfs.create(name=vrf["name"], rd=vrf["rd"])  
```
Notice here that inside the loop we have two IF statements. The first looks for just the VRF name, the second is looking for does the VRF have an route Route Distinguisher? This is done so that if we do not have an RD defined the script does not fail and simply creates the vrf name only.

```
# vlans
for vlan in data["vlans"]: 
    print(f"Creating or updating vlan {vlan['name']}")
    nb_vlan = nb.ipam.vlans.get(
        site=vlan["site"],
        vid=vlan["vid"],
    )
    if not nb_vlan: 
        nb_vlan = nb.ipam.vlans.create(
            site=vlan["site"], 
            name=vlan["name"], 
            vid=vlan["vid"],  
        )
    if "prefix" in vlan.keys(): 
        print(f"Configuring prefix {vlan['prefix']}")
        nb_prefix = nb.ipam.prefixes.get(
            site_id=nb_vlan.site.id, 
            vlan_vid=nb_vlan.vid, 
        )
        if not nb_prefix: 
            # print("  Creating new prefix")
            nb_prefix = nb.ipam.prefixes.create(
                prefix=vlan["prefix"], 
                status=vlan["status"],
                site=nb_vlan.site.id, 
                vlan=nb_vlan.id,
            )
```
If you recall from the last section we had prefixes assigned to vlans, which were assigned to sites. Notice that when we perform the get call that we need to specify the site and the vid. Because we will have multiple vlans potentially and in multiple sites we have to narrow down the search, otherwise pynatobot will complain about there being to many results.
```
>>> nb.ipam.vlans.get()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/Nautobot_Ansible_Workshop/python_scripts/.pynautobot_stuff/lib/python3.8/site-packages/pynautobot/core/endpoint.py", line 136, in get
    filter_lookup = self.filter(**kwargs)
  File "/home/Nautobot_Ansible_Workshop/python_scripts/.pynautobot_stuff/lib/python3.8/site-packages/pynautobot/core/endpoint.py", line 206, in filter
    raise ValueError("filter must be passed kwargs. Perhaps use all() instead.")
ValueError: filter must be passed kwargs. Perhaps use all() instead.
```
Instead if we want to see everything we need to use the all function. For our use case we want to validate that the specific site and vid does not already exist before attempting to create it. 
```
>>> nb.ipam.vlans.all()
[USERS, SERVERS, GUEST, GUESTS, NATIVE_VLAN]
>>>
```
 