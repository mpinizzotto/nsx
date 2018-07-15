#nsxraml client nsx manager login

nsxmanager = '172.16.30.208'
password = 'P@ssw0rd'

from nsxramlclient.client import NsxClient
nsxraml_file = '/nsxraml/nsxvapi.raml'
nsxmanager = nsxmanager
nsx_username = 'admin'
nsx_password = password
client_session = NsxClient(nsxraml_file, nsxmanager, nsx_username, nsx_password, debug=False)

print client_session
