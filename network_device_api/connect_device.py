from scrapli.driver.core import IOSXEDriver
from scrapli import response as sresponse
import os

default_user = os.getenv("IOS_USERNAME")
default_pass = os.getenv("IOS_PASSWORD")
# import logging

# # set the name for the logfile and the logging level... thats about it for bare minimum!
# logging.basicConfig(filename="scrapli.log", level=logging.DEBUG)


def _test_command(command_output="", host='1.1.1.1', channel_input='show cdp neigh',
                  textfsm_platform="cisco_iosxe", genie_platform="iosxe",
                  failed_when_contains=['% Ambiguous command', '% Incomplete command',
                                        '% Invalid input detected', '% Unknown command'],
                  template=None):
    """Create Scrapli response from text input without SSH to device."""

    response = sresponse.Response(
        host, channel_input, textfsm_platform, genie_platform, failed_when_contains)
    response.result = command_output

    if template:
        structured_result = response.ttp_parse_output(template)
        return structured_result[0]

    return response.genie_parse_output()


def send_command(host, command, username=default_user, password=default_pass, template=None, interactive=False):
    my_device = {
        "host": host,
        "auth_username": username,
        "auth_password": password,
        "auth_strict_key": False,
        "ssh_config_file": "ssh_config",
    }

    with IOSXEDriver(**my_device) as conn:
        # Enter interactive mode
        if interactive:
            response = conn.send_interactive(command)
        # example interactive list with command and expected response. "True indicates input is hidden"
        #  [
        #         ("copy flash: scp:", "Source filename []?", False),
        #         ("somefile.txt", "Address or name of remote host []?", False),
        #         ("172.31.254.100", "Destination username [carl]?", False),
        #         ("scrapli", "Password:", False),
        #         ("super_secure_password", "csr1000v#", True),
        #   ]

        else:
            response = conn.send_command(command)

        if template:
            structured_result = response.ttp_parse_output(template)
            return structured_result

        else:
            structured_result = response.genie_parse_output()
            if len(structured_result) == 0:
                return response.result

            else:
                return structured_result


def send_config(host, config, username=default_user, password=default_pass, interactive=False):
    my_device = {
        "host": host,
        "auth_username": username,
        "auth_password": password,
        "auth_strict_key": False,
        "ssh_config_file": "ssh_config",
    }

    with IOSXEDriver(**my_device) as conn:
        if interactive:
            response = conn.send_interactive(
                config, privilege_level="configuration")
        # example interactive list with command and expected response. "True indicates input is hidden"
        #  [
        #         ("copy flash: scp:", "Source filename []?", False),
        #         ("somefile.txt", "Address or name of remote host []?", False),
        #         ("172.31.254.100", "Destination username [carl]?", False),
        #         ("scrapli", "Password:", False),
        #         ("super_secure_password", "csr1000v#", True),
        #   ]
        else:
            response = conn.send_config(config)

        if response.failed:
            return response.result
        return response


if __name__ == "__main__":
    # print(send_config("10.3.120.138", ""))
    # print(len(send_command("10.3.120.138", "show switch").get("switch").get("stack").keys()))

    output1 = """
Capability Codes: R - Router, T - Trans Bridge, B - Source Route Bridge
                  S - Switch, H - Host, I - IGMP, r - Repeater, P - Phone,
                  D - Remote, C - CVTA, M - Two-port Mac Relay

Device ID        Local Intrfce     Holdtme    Capability  Platform  Port ID
DUS-9300-FE01-B2-F04.freshfieldsbruckhaus.com
                 For 1/0/15        172             R S I  C9300-48U For 1/1/1
DUS-9300-FE01-B1-F06.freshfieldsbruckhaus.com
                 For 1/0/11        159             R S I  C9300-48U For 1/1/1
DUS-9300-FE01-B1-F05.freshfieldsbruckhaus.com
                 For 1/0/10        158             R S I  C9300-48U For 1/1/1
DUS-9300-FE01-B1-F04.freshfieldsbruckhaus.com
                 For 1/0/9         131             R S I  C9300-48U For 1/1/1
DUS-9300-FE01-B2-F01.freshfieldsbruckhaus.com
                 For 1/0/12        135             R S I  C9300-48U For 1/1/1
DUS-9300-FE01-B2-F02.freshfieldsbruckhaus.com
                 For 1/0/13        168             R S I  C9300-48U For 1/1/1
DUS-9300-FE01-B1-F01.freshfieldsbruckhaus.com
                 For 1/0/6         161             R S I  C9300-48U For 1/1/1
DUS-9300-FE01-B2-F03.freshfieldsbruckhaus.com
                 For 1/0/14        129             R S I  C9300-48U For 1/1/1
DUS-9300-FE01-B1-F00.freshfieldsbruckhaus.com
                 For 1/0/5         145             R S I  C9300-48U For 1/1/1
DUS-9500-CR02-B1-F00.freshfieldsbruckhaus.com
                 For 1/0/1         152             R S I  C9500-32Q For 1/0/1
DUS-9500-CR02-B1-F00.freshfieldsbruckhaus.com
                 For 1/0/2         148             R S I  C9500-32Q For 1/0/2
DUS-9500-FR01-B1-F00.freshfieldsbruckhaus.com
                 For 1/0/4         153             R S I  C9500-48Y Hun 2/0/51
DUS-9500-FR01-B1-F00.freshfieldsbruckhaus.com
                 For 1/0/3         178             R S I  C9500-48Y Hun 1/0/51
Switch           For 1/0/8         139              S I   C9300-48U For 1/1/1
Switch           For 1/0/7         131              S I   C9300-48U For 1/1/1

Total cdp entries displayed : 16"""

    print(_test_command(output1, "10.3.120.129"))
