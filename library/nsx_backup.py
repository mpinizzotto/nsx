#!/usr/bin/env python
#coding=utf-8


def check_ftp(current_config, module):

    current_ftp_cfg = current_config['backupRestoreSettings']['ftpSettings']

    if current_ftp_cfg.get('userName') == module.params['name']:
        return False, current_config
    else:
        current_config['backupRestoreSettings']['ftpSettings']['userName'] = module.params['name']
        return True, current_config

    if current_ftp_cfg.get('transferProtocol') == module.params['transfer_protocol']:
        return False, current_config
    else:
        current_config['backupRestoreSettings']['ftpSettings']['transferProtocol'] = module.params['transfer_protocol']
        return True, current_config

    if current_ftp_cfg.get('hostNameIPAddress') == module.params['ip_addr']:
        return False, current_config
    else:
        current_config['backupRestoreSettings']['ftpSettings']['hostNameIPAddress'] = module.params['ip_addr']
        return True, current_config

    if current_ftp_cfg.get('backupDirectory') == module.params['backup_directory']:
        return False, current_config
    else:
        current_config['backupRestoreSettings']['ftpSettings']['backupDirectory'] = module.params['backup_directory']
        return True, current_config

    if current_ftp_cfg.get('filenamePrefix') == module.params['file_name_prefix']:
        return False, current_config
    else:
        current_config['backupRestoreSettings']['ftpSettings']['filenamePrefix'] = module.params['file_name_prefix']
        return True, current_config

    if module.params['password']:
        current_config['backupRestoreSettings']['ftpSettings']['password'] = module.params['password']
        return True, current_config

    if module.params['pass_phrase']:
    current_config['backupRestoreSettings']['ftpSettings']['passPhrase'] = module.params['pass_phrase']
        return True, current_config


def get_current_config(client_session):
    response = client_session.read('applianceMgrBackupSettings')
    return response['body']


def update_config(client_session, current_config):
    client_session.update('applianceMgrBackupSettings',
                          request_body_dict=current_config)

def reset_config(client_session):
    client_session.delete('applianceMgrBackupSettings')

def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='present', choices=['present', 'absent']),
            nsxmanager_spec=dict(required=True, no_log=True, type='dict'),
            name=dict(reguired=True, type='str'),
            password=dict(reguired=True, type='str')
            transfer_protocol=dict(reguired=True, default='FTP', choices=['FTP', 'SFTP']),
            ip_addr=dict(reguired=True, type='str'),
            backup_directory=dict(reguired=True, type='str'),
            file_name_prefix=dict(type='str'),
            pass_phrase=dict(required=True, type='str')
            #backup_frequency=dict(required=True, type='dict'),
        ),
        supports_check_mode=False
    )

    from nsxramlclient.client import NsxClient

    client_session = NsxClient(module.params['nsxmanager_spec']['raml_file'], module.params['nsxmanager_spec']['host'],
                               module.params['nsxmanager_spec']['user'], module.params['nsxmanager_spec']['password'])


    current_config = get_current_config(client_session)

    if current_config and module.params['state'] == 'absent':
        reset_config(client_session)
        module.exit_json(changed=True, current_config=None)

    if not current_config and module.params['state'] == 'absent':
        module.exit_json(changed=False, current_config=None)

    changed_ftp, current_config = check_ftp(current_config, module)

    if (changed_ftp):
        update_config(client_session, current_config)
        module.exit_json(changed=True, current_config=current_config)
    else:
        module.exit_json(changed=False, current_config=current_config)


from ansible.module_utils.basic import *

if __name__ == '__main__':
    main()
