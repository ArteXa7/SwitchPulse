import customtkinter as ctk
import yaml
from typing import Callable
from core.profiles import AppSettings, ProfileManager, DeviceProfile
from core.template_manager import TemplateManager

class SettingsTab(ctk.CTkFrame):
    def __init__(self, master, pm: ProfileManager, tm: TemplateManager, on_settings_changed: Callable, **kwargs):
        super().__init__(master, **kwargs)
        self.pm = pm
        self.tm = tm
        self.on_settings_changed = on_settings_changed
        self.settings = self.pm.load_settings()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.setup_general_tab()
        self.setup_profiles_tab()
        self.setup_templates_tab()

    def setup_general_tab(self):
        tab = self.tabview.add("General & App")
        
        ctk.CTkLabel(tab, text="Appearance Theme:").grid(row=0, column=0, padx=20, pady=10, sticky="w")
        self.theme_menu = ctk.CTkOptionMenu(tab, values=["Dark", "Light", "System"], command=self.change_theme)
        self.theme_menu.set(self.settings.theme)
        self.theme_menu.grid(row=0, column=1, padx=20, pady=10)

        self.mock_var = ctk.BooleanVar(value=self.settings.mock_mode)
        self.mock_switch = ctk.CTkSwitch(tab, text="Mock / Demo Mode", variable=self.mock_var)
        self.mock_switch.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="w")

        ctk.CTkLabel(tab, text="SSH Timeout (sec):").grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.timeout_entry = ctk.CTkEntry(tab)
        self.timeout_entry.insert(0, str(self.settings.timeout))
        self.timeout_entry.grid(row=2, column=1, padx=20, pady=10)

        self.save_btn = ctk.CTkButton(tab, text="Save App Settings", command=self.save_app_settings)
        self.save_btn.grid(row=3, column=0, columnspan=2, padx=20, pady=20)

    def setup_profiles_tab(self):
        tab = self.tabview.add("Credential Profiles")
        
        ctk.CTkLabel(tab, text="Save Current Sidebar as Profile:").grid(row=0, column=0, padx=20, pady=10, sticky="w")
        self.new_profile_name = ctk.CTkEntry(tab, placeholder_text="Profile Name")
        self.new_profile_name.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        self.save_p_btn = ctk.CTkButton(tab, text="Save Profile", command=self.save_current_profile)
        self.save_p_btn.grid(row=1, column=1, padx=20, pady=10)

        ctk.CTkLabel(tab, text="Delete Profile:").grid(row=2, column=0, padx=20, pady=(20, 5), sticky="w")
        self.del_profile_menu = ctk.CTkOptionMenu(tab, values=[p.name for p in self.pm.list_profiles()])
        self.del_profile_menu.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        self.del_btn = ctk.CTkButton(tab, text="Delete", fg_color="red", hover_color="darkred", command=self.delete_profile)
        self.del_btn.grid(row=3, column=1, padx=20, pady=10)

    def setup_templates_tab(self):
        tab = self.tabview.add("Vendor Polling Templates")
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(2, weight=1)

        self.temp_selector = ctk.CTkOptionMenu(tab, values=self.tm.list_templates(), command=self.load_template_text)
        self.temp_selector.grid(row=0, column=0, padx=20, pady=10, sticky="ew")

        self.yaml_text = ctk.CTkTextbox(tab, font=("Consolas", 12))
        self.yaml_text.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")

        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        self.save_t_btn = ctk.CTkButton(btn_frame, text="Save Template", command=self.save_template)
        self.save_t_btn.pack(side="left", padx=5)
        
        self.test_btn = ctk.CTkButton(btn_frame, text="Test YAML Syntax", command=self.test_yaml)
        self.test_btn.pack(side="left", padx=5)

    def change_theme(self, theme: str):
        ctk.set_appearance_mode(theme)

    def save_app_settings(self):
        self.settings.theme = self.theme_menu.get()
        self.settings.mock_mode = self.mock_var.get()
        self.settings.timeout = int(self.timeout_entry.get())
        self.pm.save_settings(self.settings)
        self.on_settings_changed()

    def save_current_profile(self):
        # This would ideally callback to app.py to get sidebar values
        # For simplicity, we trigger a refresh in app.py
        self.on_settings_changed("save_profile", self.new_profile_name.get())

    def delete_profile(self):
        name = self.del_profile_menu.get()
        if self.pm.delete_profile(name):
            self.del_profile_menu.configure(values=[p.name for p in self.pm.list_profiles()])
            self.on_settings_changed("refresh_sidebar")

    def load_template_text(self, name: str):
        with open(self.tm.TEMPLATE_DIR / name, "r") as f:
            self.yaml_text.delete("1.0", "end")
            self.yaml_text.insert("1.0", f.read())

    def save_template(self):
        name = self.temp_selector.get()
        raw = self.yaml_text.get("1.0", "end-1c")
        try:
            self.tm.save_template(name, raw)
            self.on_settings_changed("refresh_sidebar")
        except Exception as e:
            print(f"Template Error: {e}")

    def test_yaml(self):
        raw = self.yaml_text.get("1.0", "end-1c")
        try:
            yaml.safe_load(raw)
            self.test_btn.configure(fg_color="green", text="Syntax OK")
        except Exception as e:
            self.test_btn.configure(fg_color="red", text="Syntax Error")
