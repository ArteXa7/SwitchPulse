import customtkinter as ctk
from typing import List, Dict, Any

class VlansTab(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self, text="VLAN Audit", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, columnspan=2, padx=20, pady=10)

        # Active VLANs list
        self.active_frame = ctk.CTkScrollableFrame(self, label_text="Active (with MACs)")
        self.active_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Orphaned VLANs list
        self.orphaned_frame = ctk.CTkScrollableFrame(self, label_text="Orphaned (Unused)")
        self.orphaned_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

    def update_data(self, all_vlans: List[Dict[str, Any]], orphaned_ids: List[int]):
        for child in self.active_frame.winfo_children(): child.destroy()
        for child in self.orphaned_frame.winfo_children(): child.destroy()

        orphaned_set = set(orphaned_ids)
        
        for vlan in all_vlans:
            target_frame = self.orphaned_frame if vlan['id'] in orphaned_set else self.active_frame
            text = f"VLAN {vlan['id']}: {vlan['name']} ({len(vlan['ports'])} ports)"
            
            lbl = ctk.CTkLabel(target_frame, text=text, anchor="w")
            lbl.pack(fill="x", padx=10, pady=2)
            
            if vlan['id'] in orphaned_set:
                lbl.configure(text_color="#FFCC00") # Warning color for orphaned
