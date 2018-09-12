#!/usr/bin/env python
#coding=utf-8


__author__  = "mpinizzotto"



def get_sync_config_role(session):
    response = session.read('universalSyncConfigurationRole')
    response = response['body']['universalSyncRole']
    return response


def create_sync_config_role(session, action):
    return session.create('universalSyncConfigurationRole',
                           query_parameters_dict={'action': action })

                           
def check_sync_config_role(current_config, module):
    changed = False
    
    if current_config['role'] != module.params['role'].upper():
        changed = True    
        return changed           
    else:
        return changed

        
def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='present', choices=['present', 'absent']),
            nsxmanager_spec=dict(required=True, no_log=True, type='dict'),
            role=dict(required=True, choices=['standalone', 'primary']),
        ),
        supports_check_mode=False
    )

    from nsxramlclient.client import NsxClient
    import time

    session = NsxClient(module.params['nsxmanager_spec']['raml_file'], module.params['nsxmanager_spec']['host'],
                  module.params['nsxmanager_spec']['user'], module.params['nsxmanager_spec']['password'])
	
    current_config = get_sync_config_role(session)
    
    if module.params['state'] == 'absent':
        module.exit_json(changed=False, current_config=current_config)

    if module.params['state'] == 'present':
        changed_role = check_sync_config_role(current_config, module)
        
    if changed_role:
        if module.params['role'] == 'primary':
            action = 'set-as-primary'
        elif module.params['role'] == 'standalone':
            action = 'set-as-standalone'
        create_sync_config_role(session, action)
        module.exit_json(changed=True, current_config=current_config, action=action)
    else:
        module.exit_json(changed=False, current_config=current_config)

        
from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()



