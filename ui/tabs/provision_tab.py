import customtkinter as ctk
from typing import Callable

class ProvisionTab(ctk.CTkFrame):
    def __init__(self, master, on_push: Callable, **kwargs):
        super().__init__(master, **kwargs)
        self.on_push = on_push
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(self, text="Port Provisioning", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=2, padx=20, pady=10)

        # Input fields
        ctk.CTkLabel(self, text="Interface:").grid(row=1, column=0, padx=20, pady=5, sticky="e")
        self.int_entry = ctk.CTkEntry(self, placeholder_text="e.g. Gi1/0/10")
        self.int_entry.grid(row=1, column=1, padx=20, pady=5, sticky="w")

        ctk.CTkLabel(self, text="VLAN ID:").grid(row=2, column=0, padx=20, pady=5, sticky="e")
        self.vlan_entry = ctk.CTkEntry(self, placeholder_text="e.g. 100")
        self.vlan_entry.grid(row=2, column=1, padx=20, pady=5, sticky="w")

        self.gen_btn = ctk.CTkButton(self, text="Generate Preview", command=self._generate_config)
        self.gen_btn.grid(row=3, column=0, columnspan=2, padx=20, pady=10)

        # Preview area
        self.preview_text = ctk.CTkTextbox(self, height=200)
        self.preview_text.grid(row=4, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")

        self.push_btn = ctk.CTkButton(self, text="Push Configuration", fg_color="green", hover_color="darkgreen", command=self._push_config)
        self.push_btn.grid(row=5, column=0, columnspan=2, padx=20, pady=10)

    def _generate_config(self):
        interface = self.int_entry.get()
        vlan = self.vlan_entry.get()
        
        config = [
            f"interface {interface}",
            " switchport mode access",
            f" switchport access vlan {vlan}",
            " spanning-tree portfast",
            " no shutdown",
            "exit"
        ]
        
        self.preview_text.delete("1.0", "end")
        self.preview_text.insert("1.0", "\n".join(config))

    def _push_config(self):
        commands = self.preview_text.get("1.0", "end-1c").splitlines()
        if commands:
            self.on_push(commands)
