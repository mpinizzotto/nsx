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


def check_logging(current_config, logging, log_level):
    current_logging_cfg = current_config['routingGlobalConfig']['logging']
    current_logging_state = current_logging_cfg.get('enable')
    current_log_level_state = current_logging_cfg.get('logLevel')

    if current_logging_state == logging and current_log_level_state == log_level:
        return False, current_config

    elif current_logging_state != logging and current_log_level_state == log_level:
        current_config['routingGlobalConfig']['logging']['enable'] = logging
        return True, current_config

    elif current_logging_state == logging and current_log_level_state != log_level:
        current_config['routingGlobalConfig']['logging']['logLevel'] = log_level
        return True, current_config

    else:
        current_config['routingGlobalConfig']['logging']['enable'] = logging
        current_config['routingGlobalConfig']['logging']['logLevel'] = log_level
        return True, current_config


def get_current_config(client_session, edge_id):
    response = client_session.read('routingGlobalConfig', uri_parameters={'edgeId': edge_id})
    return response['body']
    

def update_config(client_session, current_config, edge_id):
    client_session.update('routingGlobalConfig', uri_parameters={'edgeId': edge_id},
                          request_body_dict=current_config)


def reset_default_config(client_session, current_config, edge_id):
    current_config['routingGlobalConfig']['logging']['enable'] = "false"
    current_config['routingGlobalConfig']['logging']['logLevel'] = "info"
    client_session.update('routingGlobalConfig', uri_parameters={'edgeId': edge_id},
                           request_body_dict=current_config)
    

def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='present', choices=['present', 'absent']),
            nsxmanager_spec=dict(required=True, no_log=True, type='dict'),
            edge_name=dict(required=True, type='str'),
            logging=dict(default='false', choices=['true', 'false']),
            log_level=dict(default='info', choices=['debug', 'info', 'notice', 'warning', 'error', 'critical',
                                                    'alert', 'emergency'], type='str'),
        ),
        supports_check_mode=False
    )

    from nsxramlclient.client import NsxClient

    client_session = NsxClient(module.params['nsxmanager_spec']['raml_file'], module.params['nsxmanager_spec']['host'],
                               module.params['nsxmanager_spec']['user'], module.params['nsxmanager_spec']['password'])

    edge_id, edge_params = get_edge(client_session, module.params['edge_name'])
    if not edge_id:
        module.fail_json(msg='could not find Edge with name {}'.format(module.params['edge_name']))

    if module.params['state'] == 'absent':
        current_config = get_current_config(client_session, edge_id)
        reset_default_config(client_session, current_config, edge_id)  
        module.exit_json(changed=True, current_config=current_config['routingGlobalConfig']['logging'])
    
    elif module.params['state'] == 'present':    
        current_config = get_current_config(client_session, edge_id)
        changed_logging, current_config = check_logging(current_config, module.params['logging'], module.params['log_level'])

        if changed_logging == True:
            update_config(client_session, current_config, edge_id)
            module.exit_json(changed=True, current_config=current_config['routingGlobalConfig']['logging'])        
        else:
            module.exit_json(changed=False, current_config=current_config['routingGlobalConfig']['logging'])


from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()