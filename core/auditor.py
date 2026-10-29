from typing import List, Dict, Set, Any
from .parsers import IOSParser

class NetworkAuditor:
    """
    Analyzes switch data to detect misconfigurations and physical layer issues.
    """

    @staticmethod
    def find_orphaned_vlans(vlan_list: List[Dict[str, Any]], mac_table: List[Dict[str, Any]]) -> List[int]:
        """
        Identifies VLANs defined on the switch that have no active MAC addresses.
        Ignores VLAN 1 (default) and typical reserved VLANs.
        """
        active_vlans = {entry['vlan'] for entry in mac_table}
        defined_vlans = {v['id'] for v in vlan_list if 1 < v['id'] < 1002}
        
        orphaned = defined_vlans - active_vlans
        return sorted(list(orphaned))

    @staticmethod
    def find_unused_ports(interface_status: List[Dict[str, Any]]) -> List[str]:
        """
        Returns ports that are currently 'notconnect'.
        """
        return [iface['port'] for iface in interface_status if iface['status'] == 'notconnect']

    @staticmethod
    def get_crc_error_report(detailed_stats: Dict[str, Dict[str, int]]) -> Dict[str, int]:
        """
        Filters and returns interfaces with non-zero CRC errors.
        """
        return {iface: data['crc'] for iface, data in detailed_stats.items() if data['crc'] > 0}

    @staticmethod
    def audit_summary(vlan_output: str, mac_output: str, int_stats_output: str) -> Dict[str, Any]:
        """
        Performs a full audit and returns a consolidated report.
        """
        vlans = IOSParser.parse_vlan_brief(vlan_output)
        macs = IOSParser.parse_mac_address_table(mac_output)
        counters = IOSParser.parse_interface_counters(int_stats_output)
        
        return {
            "orphaned_vlans": NetworkAuditor.find_orphaned_vlans(vlans, macs),
            "crc_errors": NetworkAuditor.get_crc_error_report(counters),
            "total_vlans": len(vlans),
            "active_mac_count": len(macs)
        }
