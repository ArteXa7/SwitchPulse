import os
import threading
from typing import List, Optional
import customtkinter as ctk

from .sidebar import Sidebar
from .tabs.ports_tab import PortsTab
from .tabs.vlans_tab import VlansTab
from .tabs.provision_tab import ProvisionTab
from .settings_overlay import SettingsOverlay
from core.connector import SwitchConnector
from core.profiles import DeviceProfile, ProfileManager, AppSettings
from core.parsers import TemplateParser
from core.template_manager import TemplateManager
from core.auditor import NetworkAuditor


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.settings_manager = AppSettings()
        self.profile_manager = ProfileManager()
        self.template_manager = TemplateManager()

        saved_theme = getattr(self.settings_manager, "theme", "Dark")
        ctk.set_appearance_mode(saved_theme)

        self.title("SwitchPulse - Multi-Vendor Network Automation")
        self.geometry("1150x720")
        self.minsize(950, 600)

        icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception as e:
                print(f"[Warning] Failed to load icon: {e}")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = Sidebar(
            self,
            template_manager=self.template_manager,
            profile_manager=self.profile_manager,
            on_connect=self.initiate_connection,
            on_open_settings=self.open_settings
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        tab_ports = self.tabview.add("Ports")
        self.ports_tab = PortsTab(tab_ports)
        self.ports_tab.pack(fill="both", expand=True)

        tab_vlans = self.tabview.add("VLAN Audit")
        self.vlans_tab = VlansTab(tab_vlans)
        self.vlans_tab.pack(fill="both", expand=True)

        tab_provision = self.tabview.add("Provision")
        self.provision_tab = ProvisionTab(tab_provision, on_push=self.push_config)
        self.provision_tab.pack(fill="both", expand=True)

        self.settings_overlay = SettingsOverlay(
            self,
            pm=self.profile_manager,
            tm=self.template_manager,
            on_refresh=self.on_settings_saved
        )

        self.connector: Optional[SwitchConnector] = None

    def open_settings(self):
        self.settings_overlay.show()
        self.settings_overlay.lift()

    def on_settings_saved(self):
        if hasattr(self.sidebar, "reload_profiles_and_templates"):
            self.sidebar.reload_profiles_and_templates()

    def initiate_connection(self, profile: DeviceProfile, template_name: str):
        self.sidebar.connect_btn.configure(state="disabled", text="Connecting...")
        mock_mode = getattr(self.settings_manager, "mock_mode", False)
        
        threading.Thread(
            target=self._run_connection,
            args=(profile, template_name, mock_mode),
            daemon=True
        ).start()

    def _run_connection(self, profile: DeviceProfile, template_name: str, mock_mode: bool):
        template = self.template_manager.load_template(template_name)
        self.connector = SwitchConnector(profile, mock_mode=mock_mode, template=template)

        if not self.connector.connect():
            self.after(0, lambda: self.sidebar.connect_btn.configure(state="normal", text="Failed!"))
            return

        try:
            commands = template.get("commands", {})
            cmd_status = commands.get("ports_status", "show interfaces status")
            cmd_vlan = commands.get("vlan_brief", "show vlan brief")
            cmd_mac = commands.get("mac_table", "show mac address-table")
            cmd_int = commands.get("counters", "show interfaces")

            status_raw = self.connector.send_command(cmd_status)
            vlan_raw = self.connector.send_command(cmd_vlan)
            mac_raw = self.connector.send_command(cmd_mac)
            int_raw = self.connector.send_command(cmd_int)

            status = TemplateParser.parse_interfaces_status(status_raw, template)
            vlans = TemplateParser.parse_vlan_brief(vlan_raw, template)
            macs = TemplateParser.parse_mac_address_table(mac_raw, template)
            counters = TemplateParser.parse_interface_counters(int_raw, template)
            orphaned = NetworkAuditor.find_orphaned_vlans(vlans, macs)

            self.after(0, lambda: self._update_ui_data(status, vlans, orphaned, counters))
        except Exception as e:
            print(f"[Error] Failed to poll device: {e}")
            self.after(0, lambda: self.sidebar.connect_btn.configure(state="normal", text="Error!"))

    def _update_ui_data(self, status, vlans, orphaned, counters):
        crc_map = {k: v.get("crc", 0) for k, v in counters.items()} if isinstance(counters, dict) else {}
        self.ports_tab.update_data(status, crc_map)
        self.vlans_tab.update_data(vlans, orphaned)
        self.sidebar.connect_btn.configure(state="normal", text="Connected")

    def push_config(self, commands: List[str]):
        if not self.connector:
            return
        self.provision_tab.push_btn.configure(state="disabled", text="Pushing...")
        threading.Thread(target=self._run_push, args=(commands,), daemon=True).start()

    def _run_push(self, commands: List[str]):
        try:
            self.connector.send_config_set(commands)
            self.after(0, lambda: self.provision_tab.push_btn.configure(state="normal", text="Success!"))
        except Exception as e:
            print(f"[Error] Config push failed: {e}")
            self.after(0, lambda: self.provision_tab.push_btn.configure(state="normal", text="Failed!"))