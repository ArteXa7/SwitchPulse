import customtkinter as ctk
import yaml
from typing import Callable
from core.profiles import AppSettings, ProfileManager, DeviceProfile
from core.template_manager import TemplateManager

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, master, pm: ProfileManager, tm: TemplateManager, on_refresh: Callable, **kwargs):
        super().__init__(master, **kwargs)
        self.pm = pm
        self.tm = tm
        self.on_refresh = on_refresh
        self.settings = self.pm.load_settings()

        self.title("SwitchPulse Settings")
        self.geometry("800x650")
        self.transient(master)  # Modal behavior
        self.grab_set()
        self.focus()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nsew")

        self.setup_general_tab()
        self.setup_profiles_tab()
        self.setup_templates_tab()

        # Footer
        self.close_btn = ctk.CTkButton(self, text="Save & Close", command=self.save_and_close)
        self.close_btn.grid(row=1, column=0, padx=20, pady=20, sticky="e")

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
        
        self.del_btn = ctk.CTkButton(tab, text="Delete Selected Profile", fg_color="#AA3333", hover_color="#882222", command=self.delete_profile)
        self.del_btn.grid(row=1, column=1, padx=20, pady=10)

        ctk.CTkLabel(tab, text="To create a new profile, fill the sidebar and click 'Save Profile' (simulated context).", font=ctk.CTkFont(size=11, slant="italic")).grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="w")

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
        # Save App Settings
        self.settings.theme = self.theme_menu.get()
        self.settings.mock_mode = self.mock_var.get()
        self.settings.timeout = int(self.timeout_entry.get())
        self.pm.save_settings(self.settings)
        
        self.on_refresh()
        self.destroy()
