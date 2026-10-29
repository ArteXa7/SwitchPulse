import customtkinter as ctk
from typing import Callable, List
from core.profiles import DeviceProfile, ProfileManager
from core.template_manager import TemplateManager


class Sidebar(ctk.CTkFrame):
    def __init__(
        self,
        master,
        template_manager: TemplateManager,
        profile_manager: ProfileManager,
        on_connect: Callable,
        on_open_settings: Callable,
        **kwargs
    ):
        super().__init__(master, width=300, corner_radius=0, **kwargs)
        self.tm = template_manager
        self.pm = profile_manager
        self.on_connect = on_connect
        self.on_open_settings = on_open_settings

        self.grid_rowconfigure(11, weight=1)

        # Title
        self.label = ctk.CTkLabel(self, text="SwitchPulse", font=ctk.CTkFont(size=22, weight="bold"))
        self.label.grid(row=0, column=0, padx=20, pady=(20, 20))

        # 1. Profile Selector
        ctk.CTkLabel(self, text="Saved Profile", font=ctk.CTkFont(size=11)).grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        self.profile_menu = ctk.CTkOptionMenu(self, values=self._get_profile_names(), command=self._load_profile)
        self.profile_menu.grid(row=2, column=0, padx=20, pady=(5, 15), sticky="ew")

        # 2. IP Address
        self.host_entry = ctk.CTkEntry(self, placeholder_text="Device IP Address")
        self.host_entry.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        # 3. Vendor Template
        ctk.CTkLabel(self, text="Vendor Template", font=ctk.CTkFont(size=11)).grid(row=4, column=0, padx=20, pady=(5, 0), sticky="w")
        templates = self.tm.list_templates()
        self.vendor_menu = ctk.CTkOptionMenu(self, values=templates if templates else ["None"])
        self.vendor_menu.grid(row=5, column=0, padx=20, pady=(5, 15), sticky="ew")

        # 4. Protocol & Port
        self.protocol_var = ctk.StringVar(value="ssh")
        self.protocol_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.protocol_frame.grid(row=6, column=0, padx=20, pady=5, sticky="ew")

        self.ssh_radio = ctk.CTkRadioButton(
            self.protocol_frame,
            text="SSH",
            variable=self.protocol_var,
            value="ssh",
            command=self._update_default_port
        )
        self.ssh_radio.pack(side="left", expand=True)

        self.telnet_radio = ctk.CTkRadioButton(
            self.protocol_frame,
            text="Telnet",
            variable=self.protocol_var,
            value="telnet",
            command=self._update_default_port
        )
        self.telnet_radio.pack(side="left", expand=True)

        self.port_entry = ctk.CTkEntry(self, placeholder_text="Port")
        self.port_entry.insert(0, "22")
        self.port_entry.grid(row=7, column=0, padx=20, pady=10, sticky="ew")

        # 5. Credentials
        self.user_entry = ctk.CTkEntry(self, placeholder_text="Username")
        self.user_entry.grid(row=8, column=0, padx=20, pady=10, sticky="ew")
        self.pass_entry = ctk.CTkEntry(self, placeholder_text="Password", show="*")
        self.pass_entry.grid(row=9, column=0, padx=20, pady=10, sticky="ew")

        # 6. Action
        self.connect_btn = ctk.CTkButton(
            self,
            text="Connect Device",
            font=ctk.CTkFont(weight="bold"),
            command=self._connect_clicked
        )
        self.connect_btn.grid(row=10, column=0, padx=20, pady=25, sticky="ew")

        # 7. Settings (Pinned to bottom)
        self.settings_btn = ctk.CTkButton(
            self,
            text="⚙ Settings",
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            command=self.on_open_settings
        )
        self.settings_btn.grid(row=12, column=0, padx=20, pady=20, sticky="sw")

    def reload_profiles_and_templates(self):
        templates = self.tm.list_templates()
        self.vendor_menu.configure(values=templates if templates else ["None"])
        self.profile_menu.configure(values=self._get_profile_names())

    refresh_data = reload_profiles_and_templates

    def _get_profile_names(self) -> List[str]:
        return [p.name for p in self.pm.list_profiles()] + ["None"]

    def _update_default_port(self):
        port = "22" if self.protocol_var.get() == "ssh" else "23"
        self.port_entry.delete(0, "end")
        self.port_entry.insert(0, port)

    def _load_profile(self, name: str):
        if name == "None":
            return
        profiles = self.pm.list_profiles()
        p = next((x for x in profiles if x.name == name), None)
        if p:
            self.host_entry.delete(0, "end")
            self.host_entry.insert(0, p.host)
            self.user_entry.delete(0, "end")
            self.user_entry.insert(0, p.username)
            self.pass_entry.delete(0, "end")
            self.pass_entry.insert(0, p.password)
            self.protocol_var.set(p.protocol)
            self.port_entry.delete(0, "end")
            self.port_entry.insert(0, str(p.port))
            if hasattr(p, "vendor_template") and p.vendor_template:
                self.vendor_menu.set(p.vendor_template)

    def _connect_clicked(self):
        template_name = self.vendor_menu.get()
        profile = DeviceProfile(
            name="Session",
            host=self.host_entry.get().strip(),
            username=self.user_entry.get().strip(),
            password=self.pass_entry.get(),
            protocol=self.protocol_var.get(),
            port=int(self.port_entry.get() or 22),
            vendor_template=template_name
        )
        self.on_connect(profile, template_name)