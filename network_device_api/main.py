from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .connect_device import send_command, send_config
import scrapli, os

app = FastAPI()


@app.get("/")
async def api_version():
    return {"message": "Network Device API"}

@app.get("/{device_ip}/vlans/")
async def show_vlans(device_ip, vlan_id=None):
    if vlan_id:
        command = f'show vlan id {vlan_id}'
    else:
        command = 'show vlan'

    try:
        return {    
            "message": "Command executed sucessfully",
            "detail": send_command(device_ip, command, username=os.getenv("USERNAME"), password=os.getenv("PASSWORD"))
        }

    except scrapli.exceptions.ScrapliAuthenticationFailed:
        raise HTTPException(
            status_code=404,
            detail='Timed out connecting to host, does it exist?'
        )

@app.get("/{device_ip}/ip-interfaces/")
async def show_ip_interfaces(device_ip):
    command = "show ip interface brief"
    try:
        return {    
            "message": "Command executed sucessfully",
            "detail": send_command(device_ip, command, username=os.getenv("USERNAME"), password=os.getenv("PASSWORD"))      
        }
    except scrapli.exceptions.ScrapliAuthenticationFailed:
        raise HTTPException(
            status_code=404,
            detail='Timed out connecting to host, does it exist?'
        )

@app.get("/{device_ip}/interfaces/")
async def show_interfaces(device_ip, interface_name=None):
    if interface_name:
        command = f"show interface {interface_name}"
    else:
        command = "show interfaces"
    try:
        return {    
            "message": "Command executed sucessfully",
            "detail": send_command(device_ip, command, username=os.getenv("USERNAME"), password=os.getenv("PASSWORD"))             
        }
    except scrapli.exceptions.ScrapliAuthenticationFailed:
        raise HTTPException(
            status_code=404,
            detail='Timed out connecting to host, does it exist?'
        )

@app.get("/{device_ip}/interfaces-config/")
async def show_run_interface(device_ip, interface_name=None):
    if not interface_name:
        raise HTTPException(
            status_code=404,
            detail='No interface specified!'
        )
    else:
        command = f"show run interface {interface_name}"

    try:
        return {    
            "message": "Command executed sucessfully",
            "detail": send_command(device_ip, command, username=os.getenv("USERNAME"), password=os.getenv("PASSWORD"))             
        }
    except scrapli.exceptions.ScrapliAuthenticationFailed:
        raise HTTPException(
            status_code=404,
            detail='Timed out connecting to host, does it exist?'
        )


class Interface(BaseModel):
    name: str
    ip_address: str = ""
    description: str = ""
    enabled: bool | None = None

class ConfigCommands(BaseModel):
    interface: Interface | None

def config_templates(config_model: ConfigCommands):
    if isinstance(config_model, Interface):
        interface = config_model

        config = {
            'name': f'interface {interface.name}',
            'ip_address': f'ip address {interface.ip_address}',
            'description': f'description {interface.description}',
            'enabled': f'{"shutdown" if not interface.enabled else "no shutdown"}'
        }
        interface_exclude = interface.dict(exclude_defaults=True, exclude_none=True)
        return "\n".join([config[k] for k in interface_exclude.keys()])

@app.post("/{device_ip}/interfaces/", status_code=201)
async def configure_interface(device_ip, interface: Interface):
    try:
        send_config(device_ip, config_templates(interface), username=os.getenv("USERNAME"), password=os.getenv("PASSWORD"))

        return {
            "message": "Config changed sucessfully"
        }

    except scrapli.exceptions.ScrapliAuthenticationFailed:
        raise HTTPException(
            status_code=404,
            detail='Timed out connecting to host, does it exist?'
        )





# Possible future cache implementation

# def supported_command(command, check=False):
#     """Supported commands ensure that a relevant parser exists for the output"""
#     supported_commands = set([
#         "show vlan",
#         "show ip int brief"
#         ]
#     )
#     if check:
#         return supported_commands
    
#     return command in supported_commands


# @app.get("/supported-commands/")
# async def check_supported_show_commands():
#     return supported_command("", True)

# class SupportedShowCommands(str, Enum):
#     show_vlan = "show vlan",
#     show_ip_int_brief = "show ip interface brief",

# @app.get("/{device_ip}/{command}")
# async def send_show_command_to_device(device_ip, command: SupportedShowCommands):
#     if not supported_command(command):
#         raise HTTPException(status_code=400, detail=f"Command failed, command not supported {command}")
#     return {    
#         "message": "Command executed sucessfully",
#         "detail": cache.retrieve_from_cache(command, device_ip)
            
#     }

# class Cache():
#     def __init__(self, cache={}):
#         self.cache = cache

#     def clear(self):
#         self.cache = {}

#     def update(self, device_ip, command):
#         self.cache[device_ip] = send_command(device_ip, command, username=os.getenv("USERNAME"), password=os.getenv("PASSWORD"))

#     def retrieve_from_cache(self, device_ip, command):
#         if not device_ip in self.cache:
#             try:
#                 self.cache[device_ip] = {}
#                 self.update(device_ip, command)
#                 return self.cache[device_ip][command]
#             except scrapli.exceptions.ScrapliAuthenticationFailed:
#                 raise HTTPException(
#                     status_code=404,
#                     detail='Timed out connecting to host, does it exist?'
#                 )
#         elif not self.cache[device_ip].get(command):
#             try:
#                 self.update(device_ip, command)
#                 return self.cache[device_ip][command]
#             except scrapli.exceptions.ScrapliAuthenticationFailed:
#                 raise HTTPException(
#                     status_code=404,
#                     detail='Timed out connecting to host, does it exist?'
#                 )
#         else:
#             return self.cache[device_ip][command]


# cache = Cache()
