import customtkinter as ctk
from typing import List, Dict, Any

class PortsTab(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.label = ctk.CTkLabel(self, text="Interface Status", font=ctk.CTkFont(size=16, weight="bold"))
        self.label.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        # Scrollable area for the "table"
        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure((0,1,2,3,4), weight=1)

        self._draw_headers()

    def _draw_headers(self):
        headers = ["Port", "Description", "Status", "VLAN", "CRC Errors"]
        for i, h in enumerate(headers):
            lbl = ctk.CTkLabel(self.scrollable_frame, text=h, font=ctk.CTkFont(weight="bold"))
            lbl.grid(row=0, column=i, padx=10, pady=5, sticky="w")

    def update_data(self, status_data: List[Dict[str, Any]], crc_data: Dict[str, int]):
        # Clear previous rows (except headers)
        for child in self.scrollable_frame.winfo_children():
            if int(child.grid_info()["row"]) > 0:
                child.destroy()

        for i, port in enumerate(status_data, start=1):
            crc = crc_data.get(port['port'], 0)
            
            # Row coloring/highlighting for errors
            fg_color = "transparent"
            text_color = None
            if crc > 0:
                text_color = "#FF5555" # Red for CRC errors

            ctk.CTkLabel(self.scrollable_frame, text=port['port'], text_color=text_color).grid(row=i, column=0, padx=10, pady=2, sticky="w")
            ctk.CTkLabel(self.scrollable_frame, text=port['description'], text_color=text_color).grid(row=i, column=1, padx=10, pady=2, sticky="w")
            
            # Status badge
            status_color = "#55FF55" if port['status'] == "connected" else "#AAAAAA"
            ctk.CTkLabel(self.scrollable_frame, text=port['status'], text_color=status_color).grid(row=i, column=2, padx=10, pady=2, sticky="w")
            
            ctk.CTkLabel(self.scrollable_frame, text=port['vlan'], text_color=text_color).grid(row=i, column=3, padx=10, pady=2, sticky="w")
            ctk.CTkLabel(self.scrollable_frame, text=str(crc), text_color=text_color).grid(row=i, column=4, padx=10, pady=2, sticky="w")
