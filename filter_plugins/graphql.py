class FilterModule(object):

    def filters(self):
        return {
            'graphql': self.graphql,
        }

    def graphql(self, device):
        
        import json
        from pynautobot import api


        nautobot = api(url="http://192.168.130.202:8000", token="c7fdc6be609a244bb1e851c5e47b3ccd9d990b58")
        nautobot.http_session.verify = False

        variables = {"device": device}

        query = """
        query ($device: [String]) {
        devices(name: $device) {
            config_context
            name
            position
            serial
            primary_ip4 {
            address
            }
            tenant {
            name
            }
            tags {
            name
            slug
            }
            device_role {
            name
            }
            platform {
            name
            slug
            manufacturer {
                name
            }
            napalm_driver
            }
            site {
            name
            slug
            vlans {
                name
                vid
            }
            vlan_groups {
                name
            }
            }
            interfaces {
            description
            mac_address
            enabled
            label
            _custom_field_data
            lag {
                name
            }
            name
            ip_addresses {
                address
                tags {
                slug
                }
            }
            connected_circuit_termination {
                circuit {
                cid
                commit_rate
                provider {
                    name
                }
                }
            }
            tagged_vlans {
                vid
            }
            untagged_vlan {
                vid
            }
            cable {
                termination_a_type
                status {
                name
                }
                color
            }
            tagged_vlans {
                vid
            }
            tags {
                slug
            }
            }
        }
        }
        """
        graphql_response = nautobot.graphql.query(query=query, variables=variables)
        graphql_response.json

        return graphql_response