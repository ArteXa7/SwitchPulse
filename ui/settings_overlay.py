import customtkinter as ctk
import yaml
from typing import Callable
from core.profiles import AppSettings, ProfileManager, DeviceProfile
from core.template_manager import TemplateManager

class SettingsOverlay(ctk.CTkFrame):
    def __init__(self, master, pm: ProfileManager, tm: TemplateManager, on_refresh: Callable, **kwargs):
        # Use a contrasting border and background for the 'card' effect
        super().__init__(master, border_width=2, corner_radius=12, **kwargs)
        self.pm = pm
        self.tm = tm
        self.on_refresh = on_refresh
        self.settings = self.pm.load_settings()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header Bar
        self.header = ctk.CTkFrame(self, fg_color="transparent", height=40)
        self.header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))
        self.header.grid_columnconfigure(0, weight=1)
        
        self.title_label = ctk.CTkLabel(self.header, text="SwitchPulse Settings", font=ctk.CTkFont(size=18, weight="bold"))
        self.title_label.grid(row=0, column=0, sticky="w", padx=10)
        
        self.close_icon = ctk.CTkButton(self.header, text="✕", width=30, height=30, fg_color="transparent", 
                                        text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                        command=self.hide)
        self.close_icon.grid(row=0, column=1, padx=5)

        # Tabview
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        self.setup_general_tab()
        self.setup_profiles_tab()
        self.setup_templates_tab()

        # Footer Bar
        self.footer = ctk.CTkFrame(self, fg_color="transparent", height=50)
        self.footer.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        
        self.save_btn = ctk.CTkButton(self.footer, text="Save & Close", command=self.save_and_close)
        self.save_btn.pack(side="right", padx=10)

    def show(self):
        """Displays the overlay centered on the parent window."""
        self.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.85)
        self.lift() # Ensure it's on top of all other widgets

    def hide(self):
        """Hides the overlay."""
        self.place_forget()

    def setup_general_tab(self):
        tab = self.tabview.add("General & App")
        tab.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(tab, text="Appearance Theme:").grid(row=0, column=0, padx=20, pady=20, sticky="w")
        self.theme_menu = ctk.CTkOptionMenu(tab, values=["Dark", "Light", "System"], command=ctk.set_appearance_mode)
        self.theme_menu.set(self.settings.theme)
        self.theme_menu.grid(row=0, column=1, padx=20, pady=20, sticky="w")

        self.mock_var = ctk.BooleanVar(value=self.settings.mock_mode)
        self.mock_switch = ctk.CTkSwitch(tab, text="Mock / Demo Mode", variable=self.mock_var)
        self.mock_switch.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="w")

        ctk.CTkLabel(tab, text="SSH Timeout (sec):").grid(row=2, column=0, padx=20, pady=20, sticky="w")
        self.timeout_entry = ctk.CTkEntry(tab, width=100)
        self.timeout_entry.insert(0, str(self.settings.timeout))
        self.timeout_entry.grid(row=2, column=1, padx=20, pady=20, sticky="w")

    def setup_profiles_tab(self):
        tab = self.tabview.add("Saved Profiles")
        tab.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(tab, text="Manage Device Profiles", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        self.del_profile_menu = ctk.CTkOptionMenu(tab, values=[p.name for p in self.pm.list_profiles()])
        self.del_profile_menu.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.del_btn = ctk.CTkButton(tab, text="Delete Profile", fg_color="#AA3333", hover_color="#882222", command=self.delete_profile)
        self.del_btn.grid(row=1, column=1, padx=20, pady=10)

    def setup_templates_tab(self):
        tab = self.tabview.add("Vendor Templates")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(2, weight=1)

        self.temp_selector = ctk.CTkOptionMenu(tab, values=self.tm.list_templates(), command=self.load_template_text)
        self.temp_selector.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        self.yaml_text = ctk.CTkTextbox(tab, font=("Consolas", 12))
        self.yaml_text.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")

        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        self.save_t_btn = ctk.CTkButton(btn_frame, text="Update Template", command=self.save_template)
        self.save_t_btn.pack(side="left", padx=5)
        
        self.test_btn = ctk.CTkButton(btn_frame, text="Verify YAML", command=self.test_yaml)
        self.test_btn.pack(side="left", padx=5)

    def delete_profile(self):
        name = self.del_profile_menu.get()
        if self.pm.delete_profile(name):
            self.del_profile_menu.configure(values=[p.name for p in self.pm.list_profiles()])

    def load_template_text(self, name: str):
        with open(self.tm.TEMPLATE_DIR / name, "r") as f:
            self.yaml_text.delete("1.0", "end")
            self.yaml_text.insert("1.0", f.read())

    def save_template(self):
        name = self.temp_selector.get()
        raw = self.yaml_text.get("1.0", "end-1c")
        try:
            self.tm.save_template(name, raw)
            self.save_t_btn.configure(text="Updated!", fg_color="green")
            self.after(2000, lambda: self.save_t_btn.configure(text="Update Template", fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"]))
        except Exception as e:
            print(f"Template Error: {e}")

    def test_yaml(self):
        raw = self.yaml_text.get("1.0", "end-1c")
        try:
            yaml.safe_load(raw)
            self.test_btn.configure(fg_color="green", text="Syntax OK")
        except Exception:
            self.test_btn.configure(fg_color="red", text="Syntax Error")

    def save_and_close(self):
        self.settings.theme = self.theme_menu.get()
        self.settings.mock_mode = self.mock_var.get()
        self.settings.timeout = int(self.timeout_entry.get() or 10)
        self.pm.save_settings(self.settings)
        self.on_refresh()
        self.hide()
