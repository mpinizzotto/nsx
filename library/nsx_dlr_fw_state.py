#!/usr/bin/env python
#coding=utf-8


__author__ = "mpinizzotto"


def get_edge(client_session, edge_name):
    all_edge = client_session.read_all_pages('nsxEdges', 'read')
    try:
        edge_params = [scope for scope in all_edge if scope['name'] == edge_name][0]
        edge_id = edge_params['objectId']
    except IndexError:
        return None, None

    return edge_id, edge_params

def get_firewall_state(client_session, edge_id):
    fw_state = client_session.read('nsxEdgeFirewallConfig', uri_parameters={'edgeId': edge_id})['body']

    if fw_state['firewall']['enabled'] == 'false':
        return False
    elif fw_state['firewall']['enabled'] == 'true':
        return True
    else:
        return None

def set_firewall(client_session, edge_id, state):
    firewall_body = client_session.read('nsxEdgeFirewallConfig', uri_parameters={'edgeId': edge_id})['body']
    if state:
        firewall_body['firewall']['enabled'] = 'true'
    elif not state:
        firewall_body['firewall']['enabled'] = 'false'

    return client_session.update('nsxEdgeFirewallConfig', uri_parameters={'edgeId': edge_id},
                                  request_body_dict=firewall_body)



def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='present', choices=['present', 'absent']),
            nsxmanager_spec=dict(required=True, no_log=True, type='dict'),
            name=dict(required=True),
            firewall=dict(default='true', choices=['true', 'false']),
        ),
        supports_check_mode=False
    )

    from nsxramlclient.client import NsxClient
    client_session = NsxClient(module.params['nsxmanager_spec']['raml_file'],
                               module.params['nsxmanager_spec']['host'],
                               module.params['nsxmanager_spec']['user'],
                               module.params['nsxmanager_spec']['password'])
	
    edge_id, edge_params = get_edge(client_session, module.params['name'])
    
    if module.params['state'] == 'present':
        if edge_id:
            fw_state = get_firewall_state(client_session, edge_id)
            if module.params['firewall'] == 'false' and fw_state:
                set_firewall(client_session, edge_id, False)
                changed = True
            elif module.params['firewall'] == 'true' and not fw_state:
                set_firewall(client_session, edge_id, True)
                changed = True
            else:
                changed = False
            
            if changed == True:
                module.exit_json(changed=True, fw_state=fw_state, edge_id=edge_id)
            else:
                module.exit_json(changed=False, fw_state=fw_state, edge_id=edge_id)
	    
        else:
            module.exit_json(changed=False, msg="Edge node not found, please verify hostname")
    
	
    elif module.params['state'] == 'absent':
        if edge_id:
            set_firewall(client_session, edge_id, False)
            module.exit_json(changed=True, msg="firewall state set to default")
        else:
            module.exit_json(changed=False, msg="Edge node not found, please verify hostname")


from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()



