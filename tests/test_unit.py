from fastapi.testclient import TestClient
from network_device_api.main import app, Interface, config_templates
import mock, scrapli

client = TestClient(app)

def test_config_templates():
    interface = Interface(name="gi0/0")
    assert config_templates(interface) == "interface gi0/0"

    interface = Interface(name="gi0/0", enabled=False)
    assert config_templates(interface) == "interface gi0/0\nshutdown"

    interface = Interface(name="gi0/0", enabled=False, ip_address="1.2.3.4", description="stuff")
    assert config_templates(interface) == """\
interface gi0/0
ip address 1.2.3.4
description stuff
shutdown"""

def test_api_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Network Device API"}

def test_show_vlans():
    send_command = mock.MagicMock()

    with mock.patch('network_device_api.main.send_command', send_command):
        response = client.get("/1.1.1.1/vlans/")
        assert response.status_code == 200
        assert "1.1.1.1" in send_command.call_args.args
        assert "show vlan" in send_command.call_args.args
        assert response.json()["message"] == "Command executed sucessfully"
        assert "detail" in response.json()

    send_command.reset_mock()
    with mock.patch('network_device_api.main.send_command', send_command):
        response = client.get("/1.1.1.1/vlans/?vlan_id=666")
        assert response.status_code == 200        
        assert "1.1.1.1" in send_command.call_args.args
        assert "show vlan id 666" in send_command.call_args.args
        assert response.json()["message"] == "Command executed sucessfully"
        assert "detail" in response.json()
    
    send_command = mock.MagicMock(side_effect=scrapli.exceptions.ScrapliAuthenticationFailed)
    with mock.patch('network_device_api.main.send_command', send_command):
        response = client.get("/2.2.2.2/vlans/")
        assert response.status_code == 404
        assert "2.2.2.2" in send_command.call_args.args
        assert "show vlan" in send_command.call_args.args
        assert response.json() == {
            "detail": "Timed out connecting to host, does it exist?"
            }

def test_show_ip_interfaces():
    send_command = mock.MagicMock()

    with mock.patch('network_device_api.main.send_command', send_command):
        response = client.get("/1.1.1.1/ip-interfaces/")
        assert response.status_code == 200
        assert "1.1.1.1" in send_command.call_args.args
        assert "show ip interface brief" in send_command.call_args.args
        assert response.json()["message"] == "Command executed sucessfully"
        assert "detail" in response.json()

    send_command = mock.MagicMock(side_effect=scrapli.exceptions.ScrapliAuthenticationFailed)
    with mock.patch('network_device_api.main.send_command', send_command):
        response = client.get("/2.2.2.2/ip-interfaces/")
        assert response.status_code == 404
        assert "2.2.2.2" in send_command.call_args.args
        assert "show ip interface brief" in send_command.call_args.args
        assert response.json() == {
            "detail": "Timed out connecting to host, does it exist?"
            }

def test_show_interfaces():
    send_command = mock.MagicMock()

    with mock.patch('network_device_api.main.send_command', send_command):
        response = client.get("/1.1.1.1/interfaces/")
        assert response.status_code == 200
        assert "1.1.1.1" in send_command.call_args.args
        assert "show interfaces" in send_command.call_args.args
        assert response.json()["message"] == "Command executed sucessfully"
        assert "detail" in response.json()

    send_command.reset_mock()
    with mock.patch('network_device_api.main.send_command', send_command):
        response = client.get("/1.1.1.1/interfaces/?interface_name=loopback0")
        assert response.status_code == 200        
        assert "1.1.1.1" in send_command.call_args.args
        assert "show interface loopback0" in send_command.call_args.args
        assert response.json()["message"] == "Command executed sucessfully"
        assert "detail" in response.json()

    send_command = mock.MagicMock(side_effect=scrapli.exceptions.ScrapliAuthenticationFailed)
    with mock.patch('network_device_api.main.send_command', send_command):
        response = client.get("/2.2.2.2/interfaces/")
        assert response.status_code == 404
        assert "2.2.2.2" in send_command.call_args.args
        assert "show interfaces" in send_command.call_args.args
        assert response.json() == {
            "detail": "Timed out connecting to host, does it exist?"
            }

def test_configure_interfaces():
    send_config = mock.MagicMock()

    with mock.patch('network_device_api.main.send_config', send_config):
        payload = {
            'name': 'gi0/0', 
            'description': 'testint', 
            'enabled': False
            }
        response = client.post("/1.1.1.1/interfaces/", json=payload)
        assert response.status_code == 201
        assert "1.1.1.1" in send_config.call_args.args
        assert 'interface gi0/0\ndescription testint\nshutdown' in send_config.call_args.args
        assert response.json()["message"] == "Config changed sucessfully"

    send_config = mock.MagicMock(side_effect=scrapli.exceptions.ScrapliAuthenticationFailed)
    with mock.patch('network_device_api.main.send_config', send_config):
        response = client.post("/2.2.2.2/interfaces/", json=payload)
        assert response.status_code == 404
        assert "2.2.2.2" in send_config.call_args.args
        assert response.json() == {
            "detail": "Timed out connecting to host, does it exist?"
            }


def test_show_run_interfaces():
    send_command = mock.MagicMock()

    with mock.patch('network_device_api.main.send_command', send_command):
        response = client.get("/1.1.1.1/interfaces-config/?interface_name=loopback0")
        assert response.status_code == 200
        assert "1.1.1.1" in send_command.call_args.args
        assert "show run interface loopback0" in send_command.call_args.args
        assert response.json()["message"] == "Command executed sucessfully"
        assert "detail" in response.json()

    send_command = mock.MagicMock(side_effect=scrapli.exceptions.ScrapliAuthenticationFailed)
    with mock.patch('network_device_api.main.send_command', send_command):
        response = client.get("/2.2.2.2/interfaces-config/?interface_name=loopback0")
        assert response.status_code == 404
        assert "2.2.2.2" in send_command.call_args.args
        assert "show run interface loopback0" in send_command.call_args.args
        assert response.json() == {
            "detail": "Timed out connecting to host, does it exist?"
            }

    response = client.get("/1.1.1.1/interfaces-config/")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "No interface specified!"
        }
    

# Tests for possible cache implementation

# def test_supported_command():
#     allowed_commands = ["show vlan"]
#     not_allowed_commands = ["show ipx 123"]
#     for command in allowed_commands:
#         assert supported_command(command) == True
#     for command in not_allowed_commands:
#         assert supported_command(command) == False
   
# def test_show_command():
#     command = "show vlan"
#     device_ip = "10.2.32.33"
#     with mock.patch('network_device_api.main.send_command', lambda device_ip, command, **kwargs:  {"device_ip":device_ip, "command": command}):
#         response = client.get(f"/{device_ip}/{command}")
#         assert response.status_code == 200
#         assert response.json() == {"message": "Command executed sucessfully", "detail": {"device_ip":device_ip, "command": command}}
    
    # command = "show ip bgp"
    # device_ip = "10.2.32.33"
    # response = client.get(f"/show/{device_ip}/{command}")
    # assert response.status_code == 400
    # assert response.json() == {"detail": f"Command failed, command not supported {command}"}

# def test_cache():
#     cache = Cache({"foo": 1, "bar":["foo", 2]})
#     assert isinstance(cache, Cache)
#     assert cache.cache == {"foo": 1, "bar":["foo", 2]}

#     cache.clear()
#     assert cache.cache == {}

#     send_command = mock.MagicMock()
#     send_command.return_value = {'interface': {
#                                         'GigabitEthernet0/0': {
#                                             'interface_is_ok': 'YES',
#                                             'ip_address': 'unassigned',
#                                             'method': 'unset',
#                                             'protocol': 'down',
#                                             'status': 'down'
#                                                 }}}
#     with mock.patch('network_device_api.main.send_command', send_command):
#         cache.update("1.1.1.1", "show ip interface brief")
#         assert "1.1.1.1" in cache.cache
#         assert cache.cache == {'1.1.1.1': {'interface': {'GigabitEthernet0/0': {'interface_is_ok': 'YES',
#                                                  'ip_address': 'unassigned',
#                                                  'method': 'unset',
#                                                  'protocol': 'down',
#                                                  'status': 'down'}}}}

#     cache.clear()
#     assert cache.cache == {}

    
#     cache.cache = {'1.1.1.1': {'vlans': {'1': {
#                                             'interfaces': ['TwentyFiveGigE1/0/2'],
#                                             'mtu': 1500,
#                                             'name': 'default',
#                                             'said': 100001,
#                                             'shutdown': False,
#                                             'state': 'active',
#                                             'trans1': 0,
#                                             'trans2': 0,
#                                             'type': 'enet',
#                                             'vlan_id': '1' }}}}
#     device_ip = "1.1.1.1"
#     command = "show vlan"
#     send_command = mock.MagicMock()
#     send_command.return_value = {'vlans': {
#             '1': {
#                 'interfaces': [
#                     'TwentyFiveGigE1/0/2',
#                     ],
#                 'mtu': 1500,
#                 'name': 'default',
#                 'said': 100001,
#                 'shutdown': False,
#                 'state': 'active',
#                 'trans1': 0,
#                 'trans2': 0,
#                 'type': 'enet',
#                 'vlan_id': '1'
#                 }}}
#     with mock.patch('network_device_api.main.send_command', send_command):
#         assert cache.retrieve_from_cache(device_ip, command) == {'vlans': {
#             '1': {
#                 'interfaces': [
#                     'TwentyFiveGigE1/0/2',
#                     ],
#                 'mtu': 1500,
#                 'name': 'default',
#                 'said': 100001,
#                 'shutdown': False,
#                 'state': 'active',
#                 'trans1': 0,
#                 'trans2': 0,
#                 'type': 'enet',
#                 'vlan_id': '1'
#                 }}}
#         send_command.assert_not_called()

# def test_show_vlans():
#     cache = Cache()
#     cache.cache = {'1.1.1.1':{'vlans': {'1': {
#                                                 'interfaces': ['TwentyFiveGigE1/0/2'],
#                                                 'mtu': 1500,
#                                                 'name': 'default',
#                                                 'said': 100001,
#                                                 'shutdown': False,
#                                                 'state': 'active',
#                                                 'trans1': 0,
#                                                 'trans2': 0,
#                                                 'type': 'enet',
#                                                 'vlan_id': '1' },
#                                             '2': {
#                                                 'interfaces': ['TwentyFiveGigE1/0/2'],
#                                                 'mtu': 1500,
#                                                 'name': 'default',
#                                                 'said': 100001,
#                                                 'shutdown': False,
#                                                 'state': 'active',
#                                                 'trans1': 0,
#                                                 'trans2': 0,
#                                                 'type': 'enet',
#                                                 'vlan_id': '2' },
#                                             }}}
#     with mock.patch('network_device_api.main.cache', cache):
#         response = client.get("/1.1.1.1/vlans")
#         assert response.status_code == 200
#         assert response.json() == {    
#             "message": "Command executed sucessfully",
#             "detail": cache.cache['1.1.1.1']['show vlan']      
#             }

#     send_command = mock.MagicMock(side_effect=HTTPException(status_code=404, detail='Timed out connecting to host, does it exist?'))
#     with mock.patch('network_device_api.main.send_command', send_command):
#         response = client.get("/1.1.1.2/vlans")
#         assert response.status_code == 404
#         assert response.json() == {
#             "detail": "Timed out connecting to host, does it exist?"
#             }
        
#     with mock.patch('network_device_api.main.cache', cache):
#         response = client.get("/1.1.1.1/vlans/?vlan_id=2")
#         assert response.status_code == 200
#         assert response.json() == {    
#             "message": "Command executed sucessfully",
#             "detail": cache.cache['1.1.1.1']['show vlan']['vlans']['2']
#             }
    