# src/ui/settings_window.py
import customtkinter as ctk
from i18n import LANGUAGES

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, master, settings, lm, visual_update_callback):
        super().__init__(master)
        self.settings = settings
        self.lm = lm
        self.visual_update_callback = visual_update_callback

        self.title(lm.get("settings_window_title"))
        self.geometry("600x650")
        self.transient(master) # Garde la fenêtre au-dessus de la principale
        self.grab_set() # Rend la fenêtre modale

        self.grid_columnconfigure(0, weight=1)

        self._create_widgets()
        self._update_ui_text()

    def _create_widgets(self):
        # --- Section Accessibilité ---
        self.accessibility_frame = self._create_section_frame("section_accessibility")
        self.lang_selector = self._create_option_menu(self.accessibility_frame, "language_label", list(LANGUAGES.values()), self._on_language_change)
        self.theme_selector = self._create_option_menu(self.accessibility_frame, "theme_label", ["Dark", "Light"], self._on_theme_change)
        self.color_selector = self._create_option_menu(self.accessibility_frame, "color_label", ["blue", "green", "dark-blue"], self._on_color_change)

        # --- Section Génération ---
        self.generation_frame = self._create_section_frame("section_generation")
        self.gen_steps_slider = self._create_slider(self.generation_frame, "steps_label", "generation.steps", 1, 50)
        self.gen_cfg_slider = self._create_slider(self.generation_frame, "cfg_label", "generation.cfg", 0.0, 10.0, is_float=True)

        # --- Section Édition ---
        self.edition_frame = self._create_section_frame("section_edition")
        self.edit_steps_slider = self._create_slider(self.edition_frame, "steps_label", "edition.steps", 1, 50)
        self.edit_cfg_slider = self._create_slider(self.edition_frame, "cfg_label", "edition.cfg", 0.0, 10.0, is_float=True)
        self.edit_guidance_slider = self._create_slider(self.edition_frame, "guidance_label", "edition.guidance", 0.0, 5.0, is_float=True)

        # --- Section Correction ---
        self.correction_frame = self._create_section_frame("section_correction")
        self.correct_steps_slider = self._create_slider(self.correction_frame, "steps_label", "correction.steps", 1, 20)
        self.correct_cfg_slider = self._create_slider(self.correction_frame, "cfg_label", "correction.cfg", 0.0, 5.0, is_float=True)
        self.correct_denoise_slider = self._create_slider(self.correction_frame, "denoise_label", "correction.denoise", 0.0, 1.0, is_float=True)
        
        # --- Bouton de sauvegarde ---
        self.save_button = ctk.CTkButton(self, command=self.destroy)
        self.save_button.pack(padx=20, pady=20, side="bottom", fill="x")

    def _create_section_frame(self, label_key):
        frame = ctk.CTkFrame(self)
        frame.pack(padx=10, pady=(10, 5), fill="x")
        frame.grid_columnconfigure(1, weight=1)
        label = ctk.CTkLabel(frame, font=ctk.CTkFont(weight="bold"))
        label.pack(padx=10, pady=5, anchor="w")
        setattr(self, f"{label_key}_label", label)
        return frame

    def _create_option_menu(self, parent, label_key, values, command):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=5)
        frame.grid_columnconfigure(1, weight=1)
        label = ctk.CTkLabel(frame, anchor="w")
        label.grid(row=0, column=0, padx=5, sticky="w")
        selector = ctk.CTkOptionMenu(frame, values=values, command=command)
        selector.grid(row=0, column=1, padx=5, sticky="ew")
        setattr(self, f"{label_key}_selector_label", label)
        return selector
        
    def _create_slider(self, parent, label_key, settings_key, from_, to, is_float=False):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=10, pady=5)
        frame.grid_columnconfigure(1, weight=1)
        
        label = ctk.CTkLabel(frame, anchor="w")
        label.grid(row=0, column=0, padx=5, sticky="w")
        
        value_label = ctk.CTkLabel(frame)
        value_label.grid(row=0, column=2, padx=5)

        def on_change(value):
            val = float(value) if is_float else int(value)
            value_label.configure(text=f"{val:.1f}" if is_float else f"{val}")
            self.settings.set(settings_key, val)

        slider = ctk.CTkSlider(frame, from_=from_, to=to, command=on_change)
        slider.grid(row=0, column=1, sticky="ew")
        
        setattr(self, f"{settings_key.replace('.', '_')}_label", label)
        setattr(self, f"{settings_key.replace('.', '_')}_slider", slider)
        
        return slider, value_label

    def _update_ui_text(self):
        # Met à jour tous les textes en fonction de la langue
        self.title(self.lm.get("settings_window_title"))
        self.save_button.configure(text=self.lm.get("save_and_close_button"))
        
        # Sections
        self.section_accessibility_label.configure(text=self.lm.get("section_accessibility"))
        self.section_generation_label.configure(text=self.lm.get("section_generation"))
        self.section_edition_label.configure(text=self.lm.get("section_edition"))
        self.section_correction_label.configure(text=self.lm.get("section_correction"))
        
        # Accessibilité
        self.language_label_selector_label.configure(text=self.lm.get("language_label"))
        self.lang_selector.set(LANGUAGES.get(self.settings.get('accessibility.language'), "English"))
        self.theme_label_selector_label.configure(text=self.lm.get("theme_label"))
        theme_map = {"dark": self.lm.get("theme_dark"), "light": self.lm.get("theme_light")}
        self.theme_selector.configure(values=list(theme_map.values()))
        self.theme_selector.set(theme_map[self.settings.get('accessibility.theme')])
        self.color_label_selector_label.configure(text=self.lm.get("color_label"))
        self.color_selector.set(self.settings.get('accessibility.color'))
        
        # Sliders
        for key in ["generation.steps", "generation.cfg", "edition.steps", "edition.cfg", "edition.guidance", "correction.steps", "correction.cfg", "correction.denoise"]:
            label_widget = getattr(self, f"{key.replace('.', '_')}_label")
            label_key = key.split('.')[1] + "_label"
            if key == "edition.denoise": label_key = "denoise_label" # Cas spécial pour réutiliser la trad
            label_widget.configure(text=self.lm.get(label_key))
            
            slider, value_label = getattr(self, f"{key.replace('.', '_')}_slider")
            current_val = self.settings.get(key)
            slider.set(current_val)
            is_float = isinstance(current_val, float)
            value_label.configure(text=f"{current_val:.1f}" if is_float else f"{current_val}")

    def _on_language_change(self, lang_name):
        code = next(c for c, n in LANGUAGES.items() if n == lang_name)
        if self.settings.get('accessibility.language') != code:
            self.settings.set('accessibility.language', code)
            self.lm.set_language(code)
            self._update_ui_text()
            self.visual_update_callback()

    def _on_theme_change(self, theme_name):
        theme_map = {self.lm.get("theme_dark"): "dark", self.lm.get("theme_light"): "light"}
        code = theme_map[theme_name]
        if self.settings.get('accessibility.theme') != code:
            self.settings.set('accessibility.theme', code)
            ctk.set_appearance_mode(code)

    def _on_color_change(self, color_name):
        if self.settings.get('accessibility.color') != color_name:
            self.settings.set('accessibility.color', color_name)
            ctk.set_default_color_theme(color_name)
            self.visual_update_callback(recreate=True)
            self.destroy() # Fermer pour forcer la réouverture et voir les changements