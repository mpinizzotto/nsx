
#!/usr/bin/env python
#coding=utf-8


def get_ftp_config(session):
    if session.read('applianceMgrBackupSettings')['body'] is not None:
        response = session.read('applianceMgrBackupSettings')
        response = response['body']['backupRestoreSettings']['ftpSettings']
        return response
    else:
        return None

def get_schedule_config(session):
    if session.read('applianceMgrBackupSettings')['body'] is not None:
        response = session.read('applianceMgrBackupSettings')
        response = response['body']['backupRestoreSettings']['backupFrequency']
        return response
    else:
        return None

def update_ftp_config(session, module):
    ftp_create_body = {'ftpSettings':
	                      {'userName': module.params['name'],
						   'passiveMode': 'true',
						   'useEPSV': 'true',
						   'password': module.params['password'],
						   'passPhrase': module.params['pass_phrase'],
						   'transferProtocol': module.params['transfer_protocol'],
						   'hostNameIPAddress': module.params['ip_addr'],
						   'backupDirectory': module.params['backup_directory'],
						   'filenamePrefix': module.params['file_name_prefix'],
						   'useEPRT': 'false',
						   'port': module.params['port']}
                      }
    return session.update('applianceMgrBackupSettingsFtp',
                           request_body_dict=ftp_create_body)['status']


def update_schedule_config(session, schedule):
    schedule_create_body = {'backupFrequency': schedule }
    return session.update('applianceMgrBackupSettingsSchedule',
                           request_body_dict=schedule_create_body)['status']


def normalize_schedule(schedule_list): #pass in module params

    schedule = {}
    if schedule_list:
        for item in schedule_list:
            if not isinstance(item, dict):
                print 'schedule List {} is not a valid dictionary'.format(item)

            if item.get('frequency') == None:
                print  'Schedule List Entry {} in your list is missing the'\
                'mandatory \"frequency\" parameter'.format(item.get('frequency', None))

            else:
                item['frequency'] = str(item['frequency'])

            if item['frequency'] != item['frequency'].isupper():
                item['frequency'] = item['frequency'].upper()

            if item['frequency'] == 'HOURLY':
                if item.get('minuteOfHour', 'missing') == 'missing':
                        item['minuteOfHour'] = '0'
                else:
                    item['minuteOfHour'] = str(item['minuteOfHour'])

                schedule = { 'frequency': item['frequency'],
    		           'minuteOfHour': item['minuteOfHour'] }

            if item['frequency'] == 'DAILY':
                if item.get('hourOfDay', 'missing') == 'missing':
                    item['hourOfDay'] = '0'
                else:
                    item['hourOfDay'] = str(item['hourOfDay'])

                if item.get('minuteOfHour', 'missing') == 'missing':
                    item['minuteOfHour'] = '0'
                else:
                    item['minuteOfHour'] = str(item['minuteOfHour'])

                schedule = { 'frequency': item['frequency'],
    		           'minuteOfHour': item['minuteOfHour'],
    			 'hourOfDay': item['hourOfDay'] }

            if item['frequency'] == 'WEEKLY':
                if item.get('dayOfWeek', 'missing') == 'missing':
                    item['dayOfWeek'] = 'SUNDAY'
                else:
                    if item.get('dayOfWeek') != item.get('dayOfWeek').isupper():
                        item['dayOfWeek'] = str(item['dayOfWeek']).upper()

                if item.get('hourOfDay', 'missing') == 'missing':
                    item['hourOfDay'] = '0'
                else:
                    item['hourOfDay'] = str(item['hourOfDay'])

                if item.get('minuteOfHour', 'missing') == 'missing':
                    item['minuteOfHour'] = '0'
                else:
                    item['minuteOfHour'] = str(item['minuteOfHour'])

                schedule = { 'frequency': item['frequency'],
    		           'minuteOfHour': item['minuteOfHour'],
    			 'hourOfDay': item['hourOfDay'],
    			 'dayOfWeek': item['dayOfWeek'] }

        return schedule


def check_ftp(ftp_config, module):

    #changed = False
    #if ftp_config is not None:
    if ftp_config['userName'] == module.params['name']:
        changed = False
        return changed
    else:
        changed = True
        return changed

    if ftp_config['transferProtocol'] == module.params['transfer_protocol']:
        changed = False
        return changed
    else:
        changed = True
        return changed

    if ftp_config['hostNameIPAddress'] == module.params['ip_addr']:
        changed = False
        return changed
    else:
        changed = True
        return changed

    if ftp_config['backupDirectory'] == module.params['backup_directory']:
        changed = False
        return changed
    else:
        changed = True
        return changed

    if ftp_config['filenamePrefix'] == module.params['file_name_prefix']:
        changed = False
        return changed
    else:
        changed = True
        return changed

    if ftp_config['password'] == module.params['password']:
        changed = False
        return changed
    else:
        changed = True
        return changed

    if ftp_config['passPhrase'] == module.params['pass_phrase']:
        changed = False
        return changed
    else:
        changed = True
        return changed

    #else:
    #    changed = True
    #   return changed


def delete_config(session):
    return session.delete('applianceMgrBackupSettings')['status']


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='present', choices=['present', 'absent']),
            nsxmanager_spec=dict(required=True, no_log=True, type='dict'),
            name=dict(required=True, type='str'),
            password=dict(required=True, no_log=True, type='str'),
            transfer_protocol=dict(default='FTP', choices=['FTP', 'SFTP']),
            ip_addr=dict(required=True, type='str'),
            port=dict(default='21', type='str'),
            backup_directory=dict(required=True, type='str'),
            file_name_prefix=dict(type='str'),
            pass_phrase=dict(required=True, no_log=True, type='str')
            #backup_frequency=dict(required=True, type='dict'),
        ),
        supports_check_mode=False
    )

    from nsxramlclient.client import NsxClient

    session = NsxClient(module.params['nsxmanager_spec']['raml_file'], module.params['nsxmanager_spec']['host'],
                  module.params['nsxmanager_spec']['user'], module.params['nsxmanager_spec']['password'])


    ftp_changed = False
    schedule_changed = False
    ftp_config = get_ftp_config(session)
    schedule_config = get_schedule_config(session)

    if module.params['state'] == 'absent' and ftp_config:
        delete_config(session)
        module.exit_json(changed=True, ftp_config=None)

    if module.params['state'] == 'absent' and not ftp_config:
        module.exit_json(changed=False, ftp_config=None)

    if module.params['state'] == 'present' and not ftp_config:
        update_ftp_config(session, module)
        module.exit_json(changed=True, ftp_config=ftp_config)
        ftp_changed = True

    changed_ftp = check_ftp(ftp_config, module)
    if (changed_ftp):
        delete_config(session)
        update_ftp_config(session, module)
        module.exit_json(changed=True, ftp_config=ftp_config)
    else:
        module.exit_json(changed=False, ftp_config=None)




##################################################################



    #if ftp_config and module.params['state'] == 'absent':
    #    delete_config(session)
    #    module.exit_json(changed=True, ftp_config=None)
    #
    #if not ftp_config and module.params['state'] == 'absent':
    #    module.exit_json(changed=False, ftp_config=None)
	#
	#if ftp_config and module.params['state'] == 'present':
    #    changed_ftp = check_ftp(ftp_config, module)
    #    if changed_ftp:
    #        update_ftp_config(session, module)
    #        module.exit_json(changed=True, ftp_config='1')
    #        ftp_changed = True
    #
    #if not ftp_config and module.params['state'] == 'present':
    #    update_ftp_config(session, module)
    #    ftp_changed = True
    #
    #
    #
    #
    #if ftp_changed:
    #    module.exit_json(changed=True, ftp_config=ftp_config)
    #else:
    #    module.exit_json(changed=False, ftp_config='2')
    #


from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
