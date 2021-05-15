# All credit to https://github.com/hpreston/nxos-netbox-sync and a lot of help from NetworkToCode who are always available to answer questions in slack

from pynautobot import api
import yaml 
import os 

data_file = "nb_initial_load.yaml"

with open(data_file) as f: 
    data = yaml.safe_load(f.read())

nb = api(url="http://192.168.130.2:8000", token="c7fdc6be609a244bb1e851c5e47b3ccd9d990b58")
nb.http_session.verify = False

# sites: 
for site in data["sites"]: 
    print(f"Creating or Updating Site {site['name']}")
    nb_data = nb.dcim.sites.get(slug=site["slug"])
    if not nb_data: 
        nb_data = nb.dcim.sites.create(name=site["name"], slug=site["slug"])

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

# vrfs 
for vrf in data["vrfs"]: 
    print(f"Creating or Updating vrf {vrf['name']}")
    nb_data = nb.ipam.vrfs.get(name=vrf["name"])
    if not nb_data: 
        nb_data = nb.ipam.vrfs.create(name=vrf["name"])
        if "rd" in vrf.keys():
            print(f"Configuring vrf {vrf['rd']}")
            vrf_rd = nb.ipam.vrfs.create(name=vrf["name"], rd=vrf["rd"])  

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

# Site Prefixes
for pfx in data["prefixes"]:
    print(f"Creating or Updating prefix {pfx['prefix']}")
    nb_prefix = nb.ipam.prefixes.get(
        site=pfx["site"],
        prefix=pfx["prefix"],
    )
    if not nb_prefix:
        nb_prefix = nb.ipam.prefixes.create(
            prefix=pfx["prefix"],
            site={"slug": pfx["site"]},
            description=pfx["description"],
            status="active",
        )

# devices
for device in data["devices"]: 
    print(f"Creating or Updating device {device['name']}")
    nb_device = nb.dcim.devices.get(name=device["name"])
    if not nb_device: 
        nb_device = nb.dcim.devices.create(
            name=device["name"], 
            manufacturer=nb.dcim.manufacturers.get(slug=device["manufacturer_slug"]).id, 
            site=nb.dcim.sites.get(slug=device["site_slug"]).id,
            device_role=nb.dcim.device_roles.get(slug=device["device_role_slug"]).id, 
            device_type=nb.dcim.device_types.get(slug=device["device_types_slug"]).id, 
            )
    for interface in device["interfaces"]: 
        print(f"  Creating or updating interface {interface['name']}")
        nb_interface = nb.dcim.interfaces.get(
            device_id=nb_device.id, 
            name=interface["name"]
        )
        if not nb_interface: 
            nb_interface = nb.dcim.interfaces.create(
                device=nb_device.id, 
                name=interface["name"], 
            )
        if "description" in interface.keys():
            nb_interface.description = interface["description"]
        if "type" in interface.keys():
            nb_interface.type = interface["type"]
        if "label" in interface.keys():
            nb_interface.label = interface["label"]
        if "mtu" in interface.keys():
            nb_interface.mtu = interface["mtu"]    
        if "mgmt_only" in interface.keys():
            nb_interface.mgmt_only = interface["mgmt_only"]
        if "enabled" in interface.keys():
            nb_interface.enabled = interface["enabled"]
        if "mode" in interface.keys():
            nb_interface.mode = interface["mode"]
        if "dhcp_helper" in interface.keys():
            nb_interface.custom_fields["dhcp_helper"] = interface["dhcp_helper"]    
        if "vrrp_group" in interface.keys():
            nb_interface.custom_fields["vrrp_group"] = interface["vrrp_group"]
        if "vrrp_description" in interface.keys():
            nb_interface.custom_fields["vrrp_description"] = interface["vrrp_description"]
        if "vrrp_priority" in interface.keys():
            nb_interface.custom_fields["vrrp_priority"] = interface["vrrp_priority"]
        if "vrrp_primary_ip" in interface.keys():
            nb_interface.custom_fields["vrrp_primary_ip"] = interface["vrrp_primary_ip"]
            if "untagged_vlan" in interface.keys():
                nb_interface.untagged_vlan = nb.ipam.vlans.get(site=device["site_slug"],
                    name=interface["untagged_vlan"]
                ).id
            if "tagged_vlans" in interface.keys():
                vl = [ nb.ipam.vlans.get(site=device["site_slug"], name=vlan_name).id for vlan_name in interface["tagged_vlans"] ]
                # print("VLAN LIST")
                # print(vl)
                nb_interface.tagged_vlans = vl
        if "ip_addresses" in interface.keys(): 
            for ip in interface["ip_addresses"]: 
                print(f"  Adding IP {ip['address']}")
                nb_ipadd = nb.ipam.ip_addresses.get(
                    address = ip["address"]
                )
                if not nb_ipadd: 
                    nb_ipadd = nb.ipam.ip_addresses.create(
                        address = ip["address"],
                        status = ip["status"],

                        assigned_object_type = "dcim.interface",
                        assigned_object_id = nb.dcim.interfaces.get(
                            device=device["name"],
                            name=interface["name"]).id
                    )
                if "vrf" in ip.keys():
                    nb_ipadd.vrf = nb.ipam.vrfs.get(name=ip["vrf"]).id
                if "tags" in ip.keys():
                    tgs = [ nb.extras.tags.get(name=tag).id for tag in ip["tags"] ]
                    nb_ipadd.tags = tgs
                nb_ipadd.interface = nb_interface.id
                nb_ipadd.save()
                if "primary" in ip.keys(): 
                    nb_device.primary_ip4 = nb_ipadd.id
                    nb_device.save()
        nb_interface.save()
        
# adding interface connections after they have all been created
for device in data["devices"]:
    nb_device = nb.dcim.devices.get(name=device["name"])
    for interface in device["interfaces"]:
        nb_interface = nb.dcim.interfaces.get(device_id=nb_device.id, name=interface["name"])
        if nb_interface["cable"] is None:
            if "bside_device" in interface.keys():
                print(f"  Creating or updating interface connections {device['name']}")
                int_a = nb.dcim.interfaces.get(name=interface["name"], device=nb.dcim.devices.get(name=device["name"])).id
                int_b = nb.dcim.interfaces.get(name=interface["bside_interface"], device=nb.dcim.devices.get(name=interface["bside_device"])).id
                nb.dcim.cables.create(
                    termination_a_type="dcim.interface",
                    termination_a_id=int_a,
                    termination_b_type="dcim.interface",
                    termination_b_id=int_b,
                    type="cat5e",
                    status="connected"
                )