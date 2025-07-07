# src/main.py
import os
import sys
import threading
import customtkinter as ctk
from customtkinter import CTkImage, filedialog
from PIL import Image

# --- Configuration de l'Environnement ---
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, "ComfyUI"))
sys.path.insert(0, os.path.join(script_dir, "custom_nodes"))
sys.path.insert(0, os.path.join(script_dir, 'utils'))
sys.path.insert(0, os.path.join(script_dir, 'ui'))

from i18n import LanguageManager, LANGUAGES
from settings import SettingsManager
from logic_gen import ImageGenerator, GenerationCancelledError
from logic_edit import ImageEditor
from logic_co import ImageCorrector
from settings_frame import SettingsFrame

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.settings = SettingsManager()
        self.lm = LanguageManager(self.settings.get('accessibility.language'))
        
        ctk.set_appearance_mode(self.settings.get('accessibility.theme'))
        ctk.set_default_color_theme(self.settings.get('accessibility.color'))

        self.backend_modules = None
        self.generator, self.editor, self.corrector = None, None, None
        self.is_initialized, self.is_generating = False, False
        self.current_pil_image, self.image_history, self.history_index = None, [], -1
        self.cancel_event, self.current_task_button = threading.Event(), None
        self.reopening_settings = False

        self.setup_window()
        self._create_widgets()
        self._update_ui_text()
        self.update_status("status_loading_libs")
        threading.Thread(target=self._initialize_backend, daemon=True).start()

    def setup_window(self):
        self.title(self.lm.get("window_title")); self.geometry("1400x900")
        try: self.iconbitmap(os.path.join(script_dir, '../docs/flux.ico'))
        except: pass
        self.grid_columnconfigure(1, weight=1); self.grid_rowconfigure(0, weight=1)

    def _initialize_backend(self):
        print("Initialisation du backend ComfyUI...")
        import comfy.utils, folder_paths, comfy.model_management, comfy.sample, nodes as comfy_nodes_main
        try:
            from ComfyUInunchaku.nodes.models.flux import NunchakuFluxDiTLoader
            from ComfyUInunchaku.nodes.lora.flux import NunchakuFluxLoraLoader
            from comfy_extras.nodes_flux import FluxGuidance, FluxKontextImageScale
            from comfy_extras.nodes_edit_model import ReferenceLatent
            from comfy_extras.nodes_sd3 import EmptySD3LatentImage
            comfy_nodes_main.NODE_CLASS_MAPPINGS.update({'NunchakuFluxDiTLoader': NunchakuFluxDiTLoader, 'NunchakuFluxLoraLoader': NunchakuFluxLoraLoader, 'FluxGuidance': FluxGuidance, 'FluxKontextImageScale': FluxKontextImageScale, 'ReferenceLatent': ReferenceLatent, 'EmptySD3LatentImage': EmptySD3LatentImage})
        except Exception as e: raise RuntimeError(f"Échec du chargement d'un noeud custom: {e}") from e
        project_root = os.path.abspath(os.path.join(script_dir, '..')); models_base_path = os.path.join(project_root, 'models'); output_dir = os.path.join(project_root, 'output'); os.makedirs(output_dir, exist_ok=True)
        folder_paths.add_model_folder_path("checkpoints", models_base_path); folder_paths.add_model_folder_path("diffusion_models", models_base_path); folder_paths.add_model_folder_path("vae", models_base_path); folder_paths.add_model_folder_path("clip", models_base_path); folder_paths.add_model_folder_path("loras", models_base_path); folder_paths.set_output_directory(output_dir)
        self.backend_modules = {"comfy_utils": comfy.utils, "folder_paths": folder_paths, "model_management": comfy.model_management, "nodes": comfy_nodes_main, "comfy_sample": comfy.sample}
        self.generator = ImageGenerator(self.backend_modules, self.update_status_from_thread, self.lm)
        self.editor = ImageEditor(self.backend_modules, self.update_status_from_thread, self.lm)
        self.corrector = ImageCorrector(self.backend_modules, self.update_status_from_thread, self.lm)
        self.is_initialized = True; self.after(0, self.update_state)

    def _create_widgets(self):
        self.controls_frame = ctk.CTkFrame(self, width=380, corner_radius=0)
        self.controls_frame.grid(row=0, column=0, rowspan=2, sticky="nsw")
        self.controls_frame.grid_rowconfigure(4, weight=1) # Ajustement de l'index pour la rangée qui s'étend
        self.settings_button = ctk.CTkButton(self.controls_frame, anchor="w", command=self._open_settings_panel)
        self.settings_button.pack(padx=20, pady=10, fill="x")
        ctk.CTkFrame(self.controls_frame, height=2, fg_color="gray").pack(padx=20, pady=5, fill="x")
        self.app_mode_label = ctk.CTkLabel(self.controls_frame, anchor="w"); self.app_mode_label.pack(padx=20, pady=(10, 0), fill="x")
        self.app_mode_var = ctk.StringVar(value=self.lm.get("mode_generate"))
        self.app_mode_selector = ctk.CTkSegmentedButton(self.controls_frame, variable=self.app_mode_var, command=self._on_app_mode_change); self.app_mode_selector.pack(padx=20, pady=5, fill="x")
        self.size_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        self.size_label = ctk.CTkLabel(self.size_frame, anchor="w"); self.size_label.pack(padx=0, pady=(5,0), anchor="w")
        self.size_selector = ctk.CTkOptionMenu(self.size_frame, command=lambda v: self.settings.set('generation.size', v)); self.size_selector.pack(padx=0, pady=5, fill="x")
        self.guidance_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        self.guidance_slider = self._create_local_slider(self.guidance_frame, "guidance_label", "edition.guidance", 0.0, 5.0, is_float=True)
        self.prompt_label = ctk.CTkLabel(self.controls_frame, anchor="w"); self.prompt_label.pack(padx=20, pady=(10, 0), fill="x")
        self.prompt_entry = ctk.CTkTextbox(self.controls_frame, height=120); self.prompt_entry.pack(padx=20, pady=5, fill="x")
        ctk.CTkFrame(self.controls_frame, fg_color="transparent").pack(pady=0, expand=True, fill="both")
        self.action_button_frame = ctk.CTkFrame(self.controls_frame, fg_color="transparent"); self.action_button_frame.pack(padx=20, pady=10, fill="x"); self.action_button_frame.grid_columnconfigure((0,1), weight=1)
        self.import_button = ctk.CTkButton(self.action_button_frame, command=self._import_image); self.import_button.grid(row=0, column=0, padx=(0,5), sticky="ew")
        self.correct_button = ctk.CTkButton(self.action_button_frame, command=self._start_correction_task); self.correct_button.grid(row=0, column=1, padx=(5,0), sticky="ew")
        self.action_button = ctk.CTkButton(self.controls_frame, height=40, command=self._start_task); self.action_button.pack(padx=20, pady=10, fill="x")
        self.status_label = ctk.CTkLabel(self.controls_frame, text="", wraplength=340); self.status_label.pack(padx=20, pady=5)
        self.progress_bar = ctk.CTkProgressBar(self.controls_frame); self.progress_bar.set(0); self.progress_bar.pack(padx=20, pady=(0, 20), fill="x")
        self.image_frame = ctk.CTkFrame(self); self.image_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew"); self.image_frame.grid_rowconfigure(0, weight=1); self.image_frame.grid_columnconfigure(0, weight=1)
        self.image_label = ctk.CTkLabel(self.image_frame, text=""); self.image_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.nav_frame = ctk.CTkFrame(self, fg_color="transparent"); self.nav_frame.grid(row=1, column=1, padx=20, pady=(0, 20), sticky="ew"); self.nav_frame.grid_columnconfigure(1, weight=1)
        self.prev_button = ctk.CTkButton(self.nav_frame, text="◀", width=50, command=self._nav_history_prev); self.prev_button.grid(row=0, column=0, padx=10)
        self.save_button = ctk.CTkButton(self.nav_frame, command=self._save_image); self.save_button.grid(row=0, column=1, sticky="ew")
        self.next_button = ctk.CTkButton(self.nav_frame, text="▶", width=50, command=self._nav_history_next); self.next_button.grid(row=0, column=2, padx=10)
        self.overlay_frame = ctk.CTkFrame(self, fg_color="gray25", corner_radius=0)
        self.overlay_frame.bind("<Button-1>", lambda e: self._close_settings_panel())
        self.settings_panel = SettingsFrame(self, self.settings, self.lm, self._update_ui_text, self._close_settings_panel, width=600)

    def _create_local_slider(self, parent, label_key, settings_key, from_, to, is_float=False):
        parent.grid_columnconfigure(1, weight=1)
        label = ctk.CTkLabel(parent, text=self.lm.get(label_key)); label.grid(row=0, column=0, padx=5, sticky="w")
        value_label = ctk.CTkLabel(parent); value_label.grid(row=0, column=2, padx=5)
        def on_change(value):
            val = float(value) if is_float else int(value)
            value_label.configure(text=f"{val:.1f}" if is_float else f"{val}")
            self.settings.set(settings_key, val)
        slider = ctk.CTkSlider(parent, from_=from_, to=to, command=on_change); slider.grid(row=0, column=1, sticky="ew")
        current_val = self.settings.get(settings_key)
        slider.set(current_val); value_label.configure(text=f"{current_val:.1f}" if is_float else f"{current_val}")
        return {"slider": slider, "label": label, "value_label": value_label}

    def _update_ui_text(self, recreate=False):
        if recreate:
            ctk.set_appearance_mode(self.settings.get('accessibility.theme'))
            ctk.set_default_color_theme(self.settings.get('accessibility.color'))
            if self.settings_panel.winfo_viewable(): self.reopening_settings = True
            self._close_settings_panel()
            for widget in self.winfo_children(): widget.destroy()
            self._create_widgets()
        
        self.title(self.lm.get("window_title"))
        self.settings_button.configure(text="⚙️ " + self.lm.get("settings_button"))
        self.app_mode_label.configure(text=self.lm.get("app_mode_label"))
        self.app_mode_selector.configure(values=[self.lm.get("mode_generate"), self.lm.get("mode_edit")])
        self.size_label.configure(text=self.lm.get("size_label"))
        self.size_selector.configure(values=[
            "672x1568", "688x1504", "720x1456", "752x1392", "800x1328",
            "832x1248", "880x1184", "944x1104", "1024x1024", "1104x944",
            "1184x880", "1248x832", "1328x800", "1392x752", "1456x720",
            "1504x688", "1568x672"
        ])
        self.prompt_label.configure(text=self.lm.get("positive_prompt_label"))
        self.guidance_slider['label'].configure(text=self.lm.get("guidance_label"))
        self.import_button.configure(text="📥 " + self.lm.get("import_button"))
        self.correct_button.configure(text="✨ " + self.lm.get("correct_button"))
        self.save_button.configure(text="💾 " + self.lm.get("save_button"))
        self.update_state()
        if self.reopening_settings: self._open_settings_panel()

    def _open_settings_panel(self):
        self.overlay_frame.place(relwidth=1, relheight=1)
        self.settings_panel.place(relx=0.5, rely=0.5, anchor="center")
        self.overlay_frame.tkraise(); self.settings_panel.tkraise()

    def _close_settings_panel(self):
        self.settings_panel.place_forget(); self.overlay_frame.place_forget()

    def update_state(self):
        if self.is_generating: return
        is_ready = self.is_initialized
        current_app_mode = self.app_mode_var.get()
        
        if current_app_mode == self.lm.get("mode_edit"):
            self.action_button.configure(text=self.lm.get("modify_button"), state="disabled" if not self.current_pil_image else ("normal" if is_ready else "disabled"))
            self.update_status("status_ready_to_modify")
            self.guidance_frame.pack(padx=20, pady=5, fill="x", before=self.prompt_label)
            self.size_frame.pack_forget()
        else:
            self.action_button.configure(text=self.lm.get("generate_button"), state="normal" if is_ready else "disabled")
            self.update_status("status_ready")
            self.guidance_frame.pack_forget()
            self.size_frame.pack(padx=20, pady=5, fill="x", before=self.prompt_label)
            self.size_selector.set(self.settings.get('generation.size'))
            
        image_present = self.current_pil_image is not None
        self.import_button.configure(state="normal" if is_ready else "disabled")
        
        self.correct_button.configure(
            text="✨ " + self.lm.get("correct_button"), 
            state="normal" if image_present and is_ready else "disabled"
        )
        
        self.save_button.configure(state="normal" if image_present else "disabled")
        self.prev_button.configure(state="normal" if self.history_index > 0 else "disabled")
        self.next_button.configure(state="normal" if self.history_index < len(self.image_history) - 1 else "disabled")
        
        if not image_present: 
            self.image_label.configure(text=self.lm.get("image_placeholder"), image=None)
    
    def run_task(self):
        image_path = None
        try:
            params = {"progress_callback": self.update_progress_from_thread, "cancel_event": self.cancel_event}
            if self.app_mode_var.get() == self.lm.get("mode_edit"):
                if not self.current_pil_image: raise ValueError("No image loaded for editing.")
                temp_path = os.path.join(self.editor.output_dir, "_temp_input.png"); self.current_pil_image.save(temp_path)
                edit_settings = self.settings.get('edition'); params.update({"input_image_path": temp_path, "positive_prompt": self.prompt_entry.get("1.0", "end-1c"), **edit_settings})
                image_path = self.editor.edit(**params)
            else:
                gen_settings = self.settings.get('generation'); width, height = map(int, gen_settings['size'].split('x'))
                params.update({"positive_prompt": self.prompt_entry.get("1.0", "end-1c"), "width": width, "height": height, **gen_settings}); 
                if 'size' in params: del params['size']
                image_path = self.generator.generate(**params)
        except GenerationCancelledError: self.after(0, self.update_status, "status_generation_cancelled")
        except Exception as e: import traceback; traceback.print_exc(); self.after(0, self.update_status, "status_error", str(e))
        finally: self.after(0, self.task_complete, image_path)

    def run_correction_task(self):
        image_path = None
        try:
            if not self.current_pil_image: raise ValueError("No image loaded for correction.")
            temp_path = os.path.join(self.corrector.output_dir, "_temp_input_correct.png"); self.current_pil_image.save(temp_path)
            co_settings = self.settings.get('correction')
            params = {"input_image_path": temp_path, "progress_callback": self.update_progress_from_thread, "cancel_event": self.cancel_event, **co_settings}
            image_path = self.corrector.correct(**params)
        except GenerationCancelledError: self.after(0, self.update_status, "status_generation_cancelled")
        except Exception as e: import traceback; traceback.print_exc(); self.after(0, self.update_status, "status_error", str(e))
        finally: self.after(0, self.task_complete, image_path)

    def _on_app_mode_change(self, mode_text):
        self.update_state()
    
    def _import_image(self):
        if self.is_generating: return
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.webp")]);
        if not path: return
        self.current_pil_image = Image.open(path).convert("RGB"); self.image_history = self.image_history[:self.history_index + 1]; self.image_history.append({"path": path, "pil": self.current_pil_image}); self.history_index = len(self.image_history) - 1
        self.app_mode_var.set(self.lm.get("mode_edit")); self.display_image(self.current_pil_image)
        self.update_state()

    def display_image(self, pil_image):
        self.current_pil_image = pil_image; self.image_label.update_idletasks(); frame_w, frame_h = self.image_label.winfo_width(), self.image_label.winfo_height()
        if frame_w < 100 or frame_h < 100: frame_w, frame_h = 800, 800
        ratio = min(frame_w / pil_image.width, frame_h / pil_image.height); new_size = (int(pil_image.width * ratio), int(pil_image.height * ratio))
        ctk_img = CTkImage(light_image=pil_image, dark_image=pil_image, size=new_size); self.image_label.configure(image=ctk_img, text="")
    
    def _nav_history(self, direction):
        if not (0 <= self.history_index + direction < len(self.image_history)): return
        self.history_index += direction; item = self.image_history[self.history_index]; self.display_image(item['pil']); self.update_state()
    
    def _nav_history_prev(self): self._nav_history(-1)
    def _nav_history_next(self): self._nav_history(1)
    
    def _start_task(self):
        """Fonction de démarrage pour 'Générer' et 'Éditer'."""
        if self.is_generating: return
        self._start_generic_task(self.run_task, self.action_button)
        
    def _start_correction_task(self):
        """Fonction de démarrage pour 'Corriger'."""
        if self.is_generating: return
        self._start_generic_task(self.run_correction_task, self.correct_button)
        
    def _start_generic_task(self, task_function, button):
        self.is_generating = True; self.cancel_event.clear(); self.progress_bar.set(0); self.current_task_button = button
        self.action_button.configure(state="disabled"); self.correct_button.configure(state="disabled")
        self.current_task_button.configure(text=self.lm.get("cancel_button"), command=self.cancel_task, state="normal")
        threading.Thread(target=task_function, daemon=True).start()
        
    def cancel_task(self):
        if self.current_task_button: self.current_task_button.configure(state="disabled")
        self.cancel_event.set()
        
    def task_complete(self, image_path):
        # Réassigne la bonne commande de démarrage au bouton qui a été utilisé
        if self.current_task_button == self.action_button:
            self.action_button.configure(command=self._start_task)
        elif self.current_task_button == self.correct_button:
            self.correct_button.configure(command=self._start_correction_task)

        self.is_generating = False
        self.current_task_button = None

        if image_path:
            try:
                new_image = Image.open(image_path).convert("RGB")
                self.image_history = self.image_history[:self.history_index + 1]
                self.image_history.append({"path": image_path, "pil": new_image})
                self.history_index = len(self.image_history) - 1
                self.display_image(new_image)
                
                # Passer automatiquement en mode édition après une génération réussie.
                if self.app_mode_var.get() == self.lm.get("mode_generate"):
                    self.app_mode_var.set(self.lm.get("mode_edit"))
                    self._on_app_mode_change(None) # Appeler manuellement pour MAJ UI

            except Exception as e:
                print(f"Error displaying new image: {e}")
                self.update_status("status_error", f"Image display failed: {e}")
        
        self.update_state()
        
    def _save_image(self):
        if not self.current_pil_image: return
        filepath = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", "*.png")])
        if filepath:
            try: self.current_pil_image.save(filepath); self.update_status("image_saved_success", os.path.basename(filepath))
            except Exception as e: self.update_status("image_saved_error", str(e))
            
    def update_status_from_thread(self, message_key, *args): self.after(0, self.update_status, message_key, *args)
    def update_status(self, key, *args): self.status_label.configure(text=self.lm.get(key, *args))
    def update_progress_from_thread(self, step, denoised, x, total_steps):
        self.after(0, lambda: self.progress_bar.set((step + 1) / total_steps)); self.update_status_from_thread("status_diffusion", step + 1, total_steps)

if __name__ == "__main__":
    app = App()
    app.mainloop()