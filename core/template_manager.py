import os
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional

class TemplateManager:
    """
    Manages multi-vendor YAML templates for CLI polling and parsing.
    Auto-generates default templates for Cisco, Raisecom, and D-Link on initialization.
    """
    
    TEMPLATE_DIR = Path("./vendors")

    def __init__(self):
        self.TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
        self._ensure_default_templates()

    def _ensure_default_templates(self) -> None:
        defaults = {
            "cisco_ios.yaml": {
                "vendor_name": "Cisco IOS",
                "netmiko_driver": "cisco_ios",
                "commands": {
                    "ports_status": "show interfaces status",
                    "vlan_brief": "show vlan brief",
                    "mac_table": "show mac address-table",
                    "counters": "show interfaces"
                },
                "parsers": {
                    "ports_status": r"^(?P<port>\S+)\s+(?P<description>.*?)\s+(?P<status>connected|notconnect|disabled|err-disabled)\s+(?P<vlan>\d+|trunk)\s+",
                    "mac_table": r"(?P<vlan>\d+)\s+(?P<mac>[0-9a-fA-F]{4}\.[0-9a-fA-F]{4}\.[0-9a-fA-F]{4})\s+\S+\s+(?P<port>\S+)",
                    "vlan_brief": r"^(?P<vlan_id>\d+)\s+(?P<vlan_name>[a-zA-Z0-9\-_]+)\s+(?P<status>active|act/lshut)",
                    "counters": r"(?P<port>\S+) is (?:up|down).*?(?P<crc>\d+) CRC"
                },
                "status_mapping": {
                    "connected": "connected",
                    "notconnect": "notconnect",
                    "disabled": "notconnect",
                    "err-disabled": "notconnect",
                    "active": "active"
                }
            },
            "raisecom_ros.yaml": {
                "vendor_name": "Raisecom ISCOM",
                "netmiko_driver": "raisecom_roap",
                "commands": {
                    "ports_status": "show port",
                    "vlan_brief": "show vlan",
                    "mac_table": "show mac-address-table",
                    "counters": "show interface statistics"
                },
                "parsers": {
                    "ports_status": r"^(?P<port>\d+/\d+/\d+)\s+\S+\s+(?P<status>Up|Down)\s+(?P<vlan>\d+)\s+\S+\s+(?P<description>.*)$",
                    "mac_table": r"(?P<mac>[0-9a-fA-F]{4}\.[0-9a-fA-F]{4}\.[0-9a-fA-F]{4})\s+(?P<vlan>\d+)\s+\S+\s+(?P<port>\S+)",
                    "vlan_brief": r"^(?P<vlan_id>\d+)\s+(?P<vlan_name>\S+)\s+\S+\s+(?P<status>Enable)",
                    "counters": r"Port (?P<port>\S+).*?CRC Errors:\s+(?P<crc>\d+)"
                },
                "status_mapping": {
                    "Up": "connected",
                    "Down": "notconnect",
                    "Enable": "active"
                }
            },
            "dlink_des.yaml": {
                "vendor_name": "D-Link DES/DGS",
                "netmiko_driver": "dlink_ds",
                "commands": {
                    "ports_status": "show ports",
                    "vlan_brief": "show vlan",
                    "mac_table": "show fdb",
                    "counters": "show error ports"
                },
                "parsers": {
                    "ports_status": r"^\s*(?P<port>\d+)\s+(?:.*?)\s+(?P<status>LinkUp|LinkDown)\s+(?:.*?)$",
                    "mac_table": r"(?P<vlan>\d+)\s+\S+\s+(?P<mac>[0-9a-fA-F\-]{17})\s+\S+\s+(?P<port>\d+)",
                    "vlan_brief": r"VID\s+:\s+(?P<vlan_id>\d+)\s+VLAN Name\s+:\s+(?P<vlan_name>\S+)",
                    "counters": r"^\s*(?P<port>\d+)\s+\d+\s+\d+\s+(?P<crc>\d+)"
                },
                "status_mapping": {
                    "LinkUp": "connected",
                    "LinkDown": "notconnect"
                }
            }
        }
        
        for filename, content in defaults.items():
            path = self.TEMPLATE_DIR / filename
            if not path.exists():
                with open(path, "w") as f:
                    yaml.dump(content, f, sort_keys=False)

    def list_templates(self) -> List[str]:
        return [f.name for f in self.TEMPLATE_DIR.glob("*.yaml")]

    def load_template(self, name: str) -> Dict[str, Any]:
        path = self.TEMPLATE_DIR / name
        if not path.exists():
            raise FileNotFoundError(f"Template {name} not found.")
        with open(path, "r") as f:
            return yaml.safe_load(f)

    def save_template(self, name: str, raw_yaml_str: str) -> None:
        # Validate YAML first
        yaml.safe_load(raw_yaml_str)
        path = self.TEMPLATE_DIR / name
        with open(path, "w") as f:
            f.write(raw_yaml_str)

    def delete_template(self, name: str) -> bool:
        path = self.TEMPLATE_DIR / name
        if path.exists():
            path.unlink()
            return True
        return False
