from typing import Any, Dict, Optional
from netmiko import ConnectHandler, NetmikoBaseException
from .profiles import DeviceProfile

class SwitchConnector:
    """
    Vendor-aware Netmiko wrapper supporting dynamic template resolution 
    and multi-vendor mock data generation.
    """

    def __init__(self, profile: DeviceProfile, template: Dict[str, Any], mock_mode: bool = False):
        self.profile = profile
        self.template = template
        self.mock_mode = mock_mode
        self._connection: Any = None

    def _resolve_device_type(self) -> str:
        base_type = self.template.get("netmiko_driver", "cisco_ios")
        if self.profile.protocol == "telnet":
            # Netmiko convention: base_type + _telnet
            return f"{base_type}_telnet"
        return base_type

    def connect(self) -> bool:
        if self.mock_mode:
            return True

        device_params = {
            "device_type": self._resolve_device_type(),
            "host": self.profile.host,
            "username": self.profile.username,
            "password": self.profile.password,
            "port": self.profile.port,
            "conn_timeout": 15,
        }

        try:
            self._connection = ConnectHandler(**device_params)
            return True
        except NetmikoBaseException as e:
            print(f"Vendor {self.template['vendor_name']} Connection Failed: {e}")
            return False

    def send_command(self, command_key: str) -> str:
        """
        Executes a command mapped in the vendor template.
        command_key: 'ports_status', 'vlan_brief', 'mac_table', or 'counters'
        """
        cli_command = self.template["commands"].get(command_key)
        if not cli_command:
            return f"Error: Command for {command_key} not defined for vendor."

        if self.mock_mode:
            return self._get_vendor_mock_response(command_key)

        if not self._connection:
            raise ConnectionError("No active session.")
        
        return self._connection.send_command(cli_command)

    def disconnect(self) -> None:
        if self._connection:
            self._connection.disconnect()
            self._connection = None

    def _get_vendor_mock_response(self, command_key: str) -> str:
        """Generates realistic synthetic data based on the selected vendor."""
        vendor = self.template["vendor_name"]
        
        mocks = {
            "Cisco IOS": {
                "ports_status": "Gi1/0/1  Uplink  connected  trunk  a-full  a-1000\nGi1/0/2  User_1  notconnect  10  auto  auto",
                "vlan_brief": "1  default  active\n10  Data  active",
                "mac_table": "10  0011.2233.4455  DYNAMIC  Gi1/0/2",
                "counters": "GigabitEthernet1/0/1 is up...\n  0 input errors, 0 CRC\nGigabitEthernet1/0/2 is down...\n  15 input errors, 12 CRC"
            },
            "Raisecom ISCOM": {
                "ports_status": "1/1/1  SFP  Up  1  Full  Trunk\n1/1/2  Copper  Down  10  Auto  Access",
                "vlan_brief": "1  default  Enable\n10  Data  Enable",
                "mac_table": "0011.2233.4455  10  Learned  1/1/2",
                "counters": "Port 1/1/1 Statistics:\n CRC Errors: 0\nPort 1/1/2 Statistics:\n CRC Errors: 5"
            },
            "D-Link DES/DGS": {
                "ports_status": " 1  1000M  LinkUp  Full\n 2  100M  LinkDown  Auto",
                "vlan_brief": "VID : 1  VLAN Name : default\nVID : 10  VLAN Name : Data",
                "mac_table": "10  Learned  00-11-22-33-44-55  2",
                "counters": " 1  0  0  0\n 2  10  5  8"
            }
        }
        
        vendor_mocks = mocks.get(vendor, mocks["Cisco IOS"])
        return vendor_mocks.get(command_key, f"Mock output for {command_key}")
