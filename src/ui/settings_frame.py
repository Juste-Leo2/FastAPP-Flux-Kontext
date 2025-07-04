# src/ui/settings_frame.py
import customtkinter as ctk
from i18n import LANGUAGES

class SettingsFrame(ctk.CTkFrame):
    def __init__(self, master, settings, lm, visual_update_callback, close_callback, **kwargs):
        super().__init__(master, corner_radius=10, border_width=2, **kwargs)
        
        self.settings = settings
        self.lm = lm
        self.visual_update_callback = visual_update_callback
        self.close_callback = close_callback

        self.grid_columnconfigure(0, weight=1)

        self._create_widgets()
        self._update_ui_text()

    def _create_widgets(self):
        title_label = ctk.CTkLabel(self, text=self.lm.get("settings_window_title"), font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(padx=20, pady=(20, 10))
        self.accessibility_frame = self._create_section_frame("section_accessibility")
        self.lang_selector = self._create_option_menu(self.accessibility_frame, "language_label", list(LANGUAGES.values()), self._on_language_change)
        self.theme_selector = self._create_option_menu(self.accessibility_frame, "theme_label", ["Dark", "Light"], self._on_theme_change)
        self.color_selector = self._create_option_menu(self.accessibility_frame, "color_label", ["blue", "green", "dark-blue"], self._on_color_change)
        self.generation_frame = self._create_section_frame("section_generation")
        self._create_slider(self.generation_frame, "steps_label", "generation.steps", 1, 50)
        self._create_slider(self.generation_frame, "cfg_label", "generation.cfg", 0.0, 10.0, is_float=True)
        self.edition_frame = self._create_section_frame("section_edition")
        self._create_slider(self.edition_frame, "steps_label", "edition.steps", 1, 50)
        self._create_slider(self.edition_frame, "cfg_label", "edition.cfg", 0.0, 10.0, is_float=True)
        self._create_slider(self.edition_frame, "denoise_label", "edition.denoise", 0.0, 1.0, is_float=True)
        self.correction_frame = self._create_section_frame("section_correction")
        self._create_slider(self.correction_frame, "steps_label", "correction.steps", 1, 20)
        self._create_slider(self.correction_frame, "cfg_label", "correction.cfg", 0.0, 5.0, is_float=True)
        self._create_slider(self.correction_frame, "denoise_label", "correction.denoise", 0.0, 1.0, is_float=True)
        self.save_button = ctk.CTkButton(self, command=self.close_callback)
        self.save_button.pack(padx=20, pady=20, side="bottom", fill="x")

    def _create_section_frame(self, label_key):
        frame = ctk.CTkFrame(self)
        frame.pack(padx=20, pady=(10, 5), fill="x")
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
        label = ctk.CTkLabel(frame, anchor="w"); label.grid(row=0, column=0, padx=5, sticky="w")
        value_label = ctk.CTkLabel(frame); value_label.grid(row=0, column=2, padx=5)
        def on_change(value):
            val = float(value) if is_float else int(value)
            value_label.configure(text=f"{val:.1f}" if is_float else f"{val}")
            self.settings.set(settings_key, val)
        slider = ctk.CTkSlider(frame, from_=from_, to=to, command=on_change)
        slider.grid(row=0, column=1, sticky="ew")
        setattr(self, f"{settings_key.replace('.', '_')}_widgets", (slider, value_label, label))
        return slider, value_label

    def _update_ui_text(self):
        self.save_button.configure(text=self.lm.get("save_and_close_button"))
        self.winfo_children()[0].configure(text=self.lm.get("settings_window_title"))
        self.section_accessibility_label.configure(text=self.lm.get("section_accessibility"))
        self.section_generation_label.configure(text=self.lm.get("section_generation"))
        self.section_edition_label.configure(text=self.lm.get("section_edition"))
        self.section_correction_label.configure(text=self.lm.get("section_correction"))
        self.language_label_selector_label.configure(text=self.lm.get("language_label"))
        self.lang_selector.set(LANGUAGES.get(self.settings.get('accessibility.language'), "English"))
        theme_map = {"dark": self.lm.get("theme_dark"), "light": self.lm.get("theme_light")}
        self.theme_label_selector_label.configure(text=self.lm.get("theme_label"))
        self.theme_selector.configure(values=list(theme_map.values()))
        self.theme_selector.set(theme_map[self.settings.get('accessibility.theme')])
        self.color_label_selector_label.configure(text=self.lm.get("color_label"))
        self.color_selector.set(self.settings.get('accessibility.color'))
        all_slider_keys = ["generation.steps", "generation.cfg", "edition.steps", "edition.cfg", "edition.denoise", "correction.steps", "correction.cfg", "correction.denoise"]
        for key in all_slider_keys:
            slider, value_label, label_widget = getattr(self, f"{key.replace('.', '_')}_widgets")
            label_widget.configure(text=self.lm.get(f"{key.split('.')[1]}_label"))
            current_val = self.settings.get(key)
            slider.set(current_val)
            is_float = isinstance(current_val, float)
            value_label.configure(text=f"{current_val:.1f}" if is_float else f"{current_val}")

    def _on_language_change(self, lang_name):
        code = next(c for c, n in LANGUAGES.items() if n == lang_name)
        if self.settings.get('accessibility.language') != code:
            self.settings.set('accessibility.language', code)
            self.lm.set_language(code)
            # ### CORRECTION : Un changement de langue DOIT recréer l'UI.
            self.visual_update_callback(recreate=True)

    def _on_theme_change(self, theme_name):
        theme_map = {self.lm.get("theme_dark"): "dark", self.lm.get("theme_light"): "light"}
        code = theme_map[theme_name]
        if self.settings.get('accessibility.theme') != code:
            self.settings.set('accessibility.theme', code)
            # ### CORRECTION : On demande à l'application principale de se reconstruire
            # pour appliquer le thème partout de manière cohérente.
            self.visual_update_callback(recreate=True)

    def _on_color_change(self, color_name):
        if self.settings.get('accessibility.color') != color_name:
            self.settings.set('accessibility.color', color_name)
            self.visual_update_callback(recreate=True)