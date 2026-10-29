import re
from typing import List, Dict, Any, Optional

class TemplateParser:
    """
    Universal parser that uses vendor-specific YAML templates 
    to normalize CLI output into a standard data model.
    """

    @staticmethod
    def _normalize_status(status: str, mapping: Dict[str, str]) -> str:
        return mapping.get(status, status).lower()

    @staticmethod
    def parse_ports(output: str, template: Dict[str, Any]) -> List[Dict[str, Any]]:
        pattern = template["parsers"]["ports_status"]
        mapping = template.get("status_mapping", {})
        results = []
        
        for line in output.splitlines():
            match = re.search(pattern, line)
            if match:
                data = match.groupdict()
                results.append({
                    "port": data.get("port"),
                    "description": data.get("description", "").strip(),
                    "status": TemplateParser._normalize_status(data.get("status", ""), mapping),
                    "vlan": data.get("vlan", "1")
                })
        return results

    @staticmethod
    def parse_macs(output: str, template: Dict[str, Any]) -> List[Dict[str, Any]]:
        pattern = template["parsers"]["mac_table"]
        results = []
        
        for line in output.splitlines():
            match = re.search(pattern, line)
            if match:
                data = match.groupdict()
                results.append({
                    "vlan": int(data.get("vlan", 0)),
                    "mac": data.get("mac"),
                    "port": data.get("port")
                })
        return results

    @staticmethod
    def parse_vlans(output: str, template: Dict[str, Any]) -> List[Dict[str, Any]]:
        pattern = template["parsers"]["vlan_brief"]
        results = []
        
        # Multi-line handling depends on vendor; here we use basic iteration
        for line in output.splitlines():
            match = re.search(pattern, line)
            if match:
                data = match.groupdict()
                results.append({
                    "id": int(data.get("vlan_id", 0)),
                    "name": data.get("vlan_name", "Unknown"),
                    "status": data.get("status", "active"),
                    "ports": [] # Port list usually requires vendor-specific sub-parsing
                })
        return results

    @staticmethod
    def parse_counters(output: str, template: Dict[str, Any]) -> Dict[str, int]:
        pattern = template["parsers"]["counters"]
        crc_report = {}
        
        # Some outputs are multi-line blocks per port, some are single line
        # Regex search handles both if the pattern is robust
        matches = re.finditer(pattern, output, re.MULTILINE | re.DOTALL)
        for match in matches:
            data = match.groupdict()
            port = data.get("port")
            crc = int(data.get("crc", 0))
            if port:
                crc_report[port] = crc
                
        return crc_report

IOSParser = TemplateParser