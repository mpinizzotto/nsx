#!/usr/bin/env python
#coding=utf-8



def get_edge(client_session, edge_name):

    all_edge = client_session.read_all_pages('nsxEdges', 'read')

    try:
        edge_params = [scope for scope in all_edge if scope['name'] == edge_name][0]
        edge_id = edge_params['objectId']
    except IndexError:
        return None, None

    return edge_id, edge_params


def check_bgp_state(current_config):
    
    try:
        if current_config['routing']['bgp']:
            if current_config['routing']['bgp']['enabled'] == 'true':
                return True
            else:
                return False
        else:
            return False
    
    except:
        return False

def set_bgp_state(current_config):
    
    try:
        if current_config['routing']['bgp']:
            if current_config['routing']['bgp']['enabled'] == 'false':
                current_config['routing']['bgp']['enabled'] = 'true'
                return True, current_config
            else:
                return False, current_config
        else:
            current_config['routing']['bgp']['enabled'] = 'true'
            return True, current_config
    
    except:
        return False, current_config


def check_router_id(current_config, router_id):
    current_routing_cfg = current_config['routing']['routingGlobalConfig']
    current_router_id = current_routing_cfg.get('routerId', None)
    if current_router_id == router_id:
        return False, current_config
    else:
        current_config['routing']['routingGlobalConfig']['routerId'] = router_id
        return True, current_config

def check_ecmp(current_config, ecmp):
    current_ecmp_cfg = current_config['routing']['routingGlobalConfig']
    current_ecmp_state = current_ecmp_cfg.get('ecmp', None)
    if current_ecmp_state == ecmp:
        return False, current_config
    else:
        current_config['routing']['routingGlobalConfig']['ecmp'] = ecmp
        return True, current_config


def check_bgp_options(current_config, graceful_restart, default_originate, localas):     
    changed = False
    current_bgp = current_config['routing']['bgp']
    c_grst_str = current_bgp.get('gracefulRestart', 'false')
    c_dio_str = current_bgp.get('defaultOriginate', 'false')

    if c_grst_str == 'true':
        c_grst = True
    else:
        c_grst = False

    if c_dio_str == 'true':
        c_dio = True
    else:
        c_dio = False

    if c_grst != graceful_restart and graceful_restart:
        current_config['routing']['bgp']['gracefulRestart'] = 'true'
        changed = True
    elif c_grst != graceful_restart and not graceful_restart:
        current_config['routing']['bgp']['gracefulRestart'] = 'false'
        changed = True

    if c_dio != default_originate and default_originate:
        current_config['routing']['bgp']['defaultOriginate'] = 'true'
        changed = True
    elif c_dio != default_originate and not default_originate:
        current_config['routing']['bgp']['defaultOriginate'] = 'false'
        changed = True

    #c_prot_addr = current_bgp.get('protocolAddress')
    #c_forwarding_addr = current_bgp.get('forwardingAddress')
    c_localas = current_bgp.get('localAS')

    if c_localas != localas:
        current_config['routing']['bgp']['localAS'] = localas
        changed = True
    
    return changed, current_config
	
	
def check_bgp_neighbours(client_session, current_config, bgp_neighbours): #module params
    
    changed = False
 
    if bgp_neighbours is not None:

        if current_config['routing']['bgp']['bgpNeighbours']:
            c_neighbour_list = client_session.normalize_list_return(current_config['routing']['bgp']['bgpNeighbours']['bgpNeighbour'])
        else:
            c_neighbour_list = []

        for new_neighbour in bgp_neighbours:
            c_neighbour_list.append(new_neighbour)

        current_config['routing']['bgp']['bgpNeighbours'] = {'bgpNeighbour': c_neighbour_list}
        
        if c_neighbour_list != bgp_neighbours:
            current_config['routing']['bgp']['bgpNeighbours']['bgpNeighbour'] = bgp_neighbours
            changed = True    
    
        return changed, current_config
    
    else:
        return changed

	

def get_current_config(client_session, edge_id):
    response = client_session.read('routingConfig', uri_parameters={'edgeId': edge_id})
    return response['body']

def update_config(client_session, current_config, edge_id):
    client_session.update('routingConfig', uri_parameters={'edgeId': edge_id},
                          request_body_dict=current_config)


def reset_config(client_session, edge_id):
    client_session.delete('routingBGP', uri_parameters={'edgeId': edge_id})


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='present', choices=['present', 'absent']),
            nsxmanager_spec=dict(required=True, no_log=True, type='dict'),
            edge_name=dict(required=True, type='str'),
            router_id=dict(required=True, type='str'),
            ecmp=dict(default='false', choices=['true', 'false']),
            graceful_restart=dict(default=True, type='bool'),
            default_originate=dict(default=False, type='bool'),
            #protocol_address=dict(type='str'),
            #forwarding_address=dict(type='str'),
            localas=dict(required=True, type='str'),
            logging=dict(default=False, type='bool'),
            log_level=dict(default='info', choices=['debug', 'info', 'notice', 'warning', 'error', 'critical',
                                                    'alert', 'emergency'], type='str'),
            bgp_neighbours=dict(type='list')
        ),
        supports_check_mode=False
    )

    from nsxramlclient.client import NsxClient

    client_session = NsxClient(module.params['nsxmanager_spec']['raml_file'], module.params['nsxmanager_spec']['host'],
                               module.params['nsxmanager_spec']['user'], module.params['nsxmanager_spec']['password'])

    edge_id, edge_params = get_edge(client_session, module.params['edge_name'])
    if not edge_id:
        module.fail_json(msg='could not find Edge with name {}'.format(module.params['edge_name']))

    current_config = get_current_config(client_session, edge_id)

    if module.params['state'] == 'absent' and check_bgp_state(current_config):
        reset_config(client_session, edge_id)
        module.exit_json(changed=True, current_config=None)
   
    elif module.params['state'] == 'absent' and not check_bgp_state(current_config):
        module.exit_json(changed=False, current_config=None)

    changed_state, current_config = set_bgp_state(current_config)
    changed_rtid, current_config = check_router_id(current_config, module.params['router_id'])
    changed_ecmp, current_config = check_ecmp(current_config, module.params['ecmp'])
    changed_opt, current_config = check_bgp_options(current_config, module.params['graceful_restart'],
                                                     module.params['default_originate'],module.params['localas'])     
  
    #############################
    changed_neighbour, current_config = check_bgp_neighbours(client_session, current_config, module.params['bgp_neighbours'])
   
    if (changed_state or changed_rtid or changed_ecmp or changed_opt or changed_neighbour): ##############
        update_config(client_session, current_config, edge_id)
        module.exit_json(changed=True, current_config=current_config)
    else:
        module.exit_json(changed=False, current_config=current_config)


from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
