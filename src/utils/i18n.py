# src/utils/i18n.py
TRANSLATIONS = {
    "en": {
        # --- General ---
        "window_title": "Flux Kontext Image Studio",
        "app_mode_label": "Application Mode:",
        "mode_generate": "Generate",
        "mode_edit": "Edit",
        "positive_prompt_label": "Prompt:",
        "memory_management_label": "Memory Mode:",
        "mode_performant": "Performance",
        "mode_economical": "Economical",
        "size_label": "Dimensions:",
        
        # --- Buttons ---
        "settings_button": "Settings",
        "generate_button": "Generate",
        "modify_button": "Modify Image",
        "correct_button": "Correct Image",
        "cancel_button": "Cancel",
        "import_button": "Import Image",
        "save_button": "Save",

        # --- Settings Window ---
        "settings_window_title": "Application Settings",
        "save_and_close_button": "Save and Close",
        "section_accessibility": "Accessibility",
        "language_label": "Language:",
        "theme_label": "Theme:",
        "theme_dark": "Dark",
        "theme_light": "Light",
        "color_label": "Accent Color:",
        "section_generation": "Generation Settings",
        "section_edition": "Editing Settings",
        "section_correction": "Correction Settings",
        "steps_label": "Steps:",
        "cfg_label": "CFG:",
        "denoise_label": "Strength:",
        "guidance_label": "Guidance Strength:",
        
        # --- History & Status ---
        "history_prev_tooltip": "Previous Image",
        "history_next_tooltip": "Next Image",
        "status_ready": "Ready. Enter a prompt to generate.",
        "status_ready_to_modify": "Ready. Adjust prompt and modify the image.",
        "status_initializing": "Initializing...",
        "status_loading_libs": "Loading backend libraries...",
        "status_init_done": "Backend ready.",
        "status_unloading": "Unloading models...",
        "status_unloaded": "Models unloaded.",
        "status_generating": "Generating...",
        "status_modifying": "Modifying image...",
        "status_correcting": "Correcting image...",
        "status_diffusion": "Diffusion: Step {0} / {1}...",
        "status_generation_done": "Done!",
        "status_generation_cancelled": "Operation cancelled.",
        "status_error": "Error: {0}",
        "image_placeholder": "Import an image or write a prompt to generate.",
        "image_saved_success": "Image saved: {0}",
        "image_saved_error": "Save error: {0}",

        # --- Backend Messages ---
        "eco_loading_clip": "Eco: Loading CLIP/T5...", "eco_unloading_clip": "Eco: Unloading CLIP/T5...",
        "eco_loading_dit": "Eco: Loading DiT model...", "eco_unloading_dit": "Eco: Unloading DiT model...",
        "eco_loading_vae": "Eco: Loading VAE...", "eco_unloading_vae": "Eco: Unloading VAE...",
        "eco_loading_vae_clip": "Eco: Loading VAE & CLIP...", "eco_unloading_vae_clip": "Eco: Unloading VAE & CLIP...",
        "perf_loading_models": "Loading all models...", "perf_preparing_nodes": "Preparing workflow...",
        "perf_generating": "Generating...", "perf_done": "Finished (models kept in memory).",
        
        # --- Nouveaux messages pour le mode Eco ---
        "eco_status_encode_vae": "Eco: Encoding initial image...",
        "eco_status_encode_clip": "Eco: Encoding prompt...",
        "eco_status_sampling": "Eco: Generating with DiT model...",
        "eco_status_decode_vae": "Eco: Decoding final image..."
    },
    "fr": {
        # --- General ---
        "window_title": "Flux Kontext Image Studio",
        "app_mode_label": "Mode de l'application :",
        "mode_generate": "Générer",
        "mode_edit": "Éditer",
        "positive_prompt_label": "Prompt :",
        "memory_management_label": "Mode Mémoire :",
        "mode_performant": "Performant",
        "mode_economical": "Économique",
        "size_label": "Dimensions :",
        
        # --- Buttons ---
        "settings_button": "Paramètres",
        "generate_button": "Générer",
        "modify_button": "Modifier l'image",
        "correct_button": "Corriger l'Image",
        "cancel_button": "Annuler",
        "import_button": "Importer une Image",
        "save_button": "Sauvegarder",
        
        # --- Settings Window ---
        "settings_window_title": "Paramètres de l'application",
        "save_and_close_button": "Sauvegarder et Fermer",
        "section_accessibility": "Accessibilité",
        "language_label": "Langue :",
        "theme_label": "Thème :",
        "theme_dark": "Sombre",
        "theme_light": "Clair",
        "color_label": "Couleur d'accent :",
        "section_generation": "Paramètres de Génération",
        "section_edition": "Paramètres d'Édition",
        "section_correction": "Paramètres de Correction",
        "steps_label": "Étapes :",
        "cfg_label": "CFG :",
        "denoise_label": "Force :",
        "guidance_label": "Force de Guidage :",

        # --- History & Status ---
        "history_prev_tooltip": "Image précédente", "history_next_tooltip": "Image suivante",
        "status_ready": "Prêt. Entrez un prompt pour générer.",
        "status_ready_to_modify": "Prêt. Ajustez le prompt et modifiez l'image.",
        "status_initializing": "Initialisation...", "status_loading_libs": "Chargement des librairies...",
        "status_init_done": "Moteur prêt.", "status_unloading": "Déchargement des modèles...",
        "status_unloaded": "Modèles déchargés.", "status_generating": "Génération...",
        "status_modifying": "Modification de l'image...", "status_correcting": "Correction de l'image...",
        "status_diffusion": "Diffusion : Étape {0} / {1}...", "status_generation_done": "Terminé !",
        "status_generation_cancelled": "Opération annulée.", "status_error": "Erreur : {0}",
        "image_placeholder": "Importez une image ou écrivez un prompt pour générer.",
        "image_saved_success": "Image sauvegardée : {0}", "image_saved_error": "Erreur de sauvegarde : {0}",
        
        # --- Backend Messages ---
        "eco_loading_clip": "Éco : Chargement CLIP/T5...", "eco_unloading_clip": "Éco : Déchargement CLIP/T5...",
        "eco_loading_dit": "Éco : Chargement du modèle DiT...", "eco_unloading_dit": "Éco : Déchargement du modèle DiT...",
        "eco_loading_vae": "Éco : Chargement du VAE...", "eco_unloading_vae": "Éco : Déchargement du VAE...",
        "eco_loading_vae_clip": "Éco : Chargement VAE & CLIP...", "eco_unloading_vae_clip": "Éco : Déchargement VAE & CLIP...",
        "perf_loading_models": "Chargement de tous les modèles...", "perf_preparing_nodes": "Préparation du workflow...",
        "perf_generating": "Génération...", "perf_done": "Terminé (modèles gardés en mémoire).",

        # --- Nouveaux messages pour le mode Eco ---
        "eco_status_encode_vae": "Éco : Encodage de l'image initiale...",
        "eco_status_encode_clip": "Éco : Encodage du prompt...",
        "eco_status_sampling": "Éco : Génération avec le modèle DiT...",
        "eco_status_decode_vae": "Éco : Décodage de l'image finale..."
    },
    "es": {
        # --- General ---
        "window_title": "Flux Kontext Image Studio",
        "app_mode_label": "Modo de aplicación:",
        "mode_generate": "Generar",
        "mode_edit": "Editar",
        "positive_prompt_label": "Prompt:",
        "memory_management_label": "Modo de memoria:",
        "mode_performant": "Rendimiento",
        "mode_economical": "Económico",
        "size_label": "Dimensiones:",
        
        # --- Buttons ---
        "settings_button": "Ajustes",
        "generate_button": "Generar",
        "modify_button": "Modificar imagen",
        "correct_button": "Corregir imagen",
        "cancel_button": "Cancelar",
        "import_button": "Importar imagen",
        "save_button": "Guardar",

        # --- Settings Window ---
        "settings_window_title": "Ajustes de la aplicación",
        "save_and_close_button": "Guardar y Cerrar",
        "section_accessibility": "Accesibilidad",
        "language_label": "Idioma:",
        "theme_label": "Tema:",
        "theme_dark": "Oscuro",
        "theme_light": "Claro",
        "color_label": "Color de acento:",
        "section_generation": "Ajustes de generación",
        "section_edition": "Ajustes de edición",
        "section_correction": "Ajustes de corrección",
        "steps_label": "Pasos:",
        "cfg_label": "CFG:",
        "denoise_label": "Fuerza:",
        "guidance_label": "Fuerza de guía:",
        
        # --- History & Status ---
        "history_prev_tooltip": "Imagen anterior",
        "history_next_tooltip": "Imagen siguiente",
        "status_ready": "Listo. Introduce un prompt para generar.",
        "status_ready_to_modify": "Listo. Ajusta el prompt y modifica la imagen.",
        "status_initializing": "Inicializando...",
        "status_loading_libs": "Cargando bibliotecas de backend...",
        "status_init_done": "Backend listo.",
        "status_unloading": "Descargando modelos...",
        "status_unloaded": "Modelos descargados.",
        "status_generating": "Generando...",
        "status_modifying": "Modificando imagen...",
        "status_correcting": "Corrigiendo imagen...",
        "status_diffusion": "Difusión: Paso {0} / {1}...",
        "status_generation_done": "¡Hecho!",
        "status_generation_cancelled": "Operación cancelada.",
        "status_error": "Error: {0}",
        "image_placeholder": "Importa una imagen o escribe un prompt para generar.",
        "image_saved_success": "Imagen guardada: {0}",
        "image_saved_error": "Error al guardar: {0}",

        # --- Backend Messages ---
        "eco_loading_clip": "Eco: Cargando CLIP/T5...", "eco_unloading_clip": "Eco: Descargando CLIP/T5...",
        "eco_loading_dit": "Eco: Cargando modelo DiT...", "eco_unloading_dit": "Eco: Descargando modelo DiT...",
        "eco_loading_vae": "Eco: Cargando VAE...", "eco_unloading_vae": "Eco: Descargando VAE...",
        "eco_loading_vae_clip": "Eco: Cargando VAE & CLIP...", "eco_unloading_vae_clip": "Eco: Descargando VAE & CLIP...",
        "perf_loading_models": "Cargando todos los modelos...", "perf_preparing_nodes": "Preparando flujo de trabajo...",
        "perf_generating": "Generando...", "perf_done": "Finalizado (modelos mantenidos en memoria).",
        
        # --- Nouveaux messages pour le mode Eco ---
        "eco_status_encode_vae": "Eco: Codificando imagen inicial...",
        "eco_status_encode_clip": "Eco: Codificando prompt...",
        "eco_status_sampling": "Eco: Generando con modelo DiT...",
        "eco_status_decode_vae": "Eco: Decodificando imagen final..."
    },
    "de": {
        # --- General ---
        "window_title": "Flux Kontext Image Studio",
        "app_mode_label": "Anwendungsmodus:",
        "mode_generate": "Generieren",
        "mode_edit": "Bearbeiten",
        "positive_prompt_label": "Prompt:",
        "memory_management_label": "Speichermodus:",
        "mode_performant": "Leistung",
        "mode_economical": "Sparsam",
        "size_label": "Abmessungen:",
        
        # --- Buttons ---
        "settings_button": "Einstellungen",
        "generate_button": "Generieren",
        "modify_button": "Bild ändern",
        "correct_button": "Bild korrigieren",
        "cancel_button": "Abbrechen",
        "import_button": "Bild importieren",
        "save_button": "Speichern",

        # --- Settings Window ---
        "settings_window_title": "Anwendungseinstellungen",
        "save_and_close_button": "Speichern und Schließen",
        "section_accessibility": "Barrierefreiheit",
        "language_label": "Sprache:",
        "theme_label": "Thema:",
        "theme_dark": "Dunkel",
        "theme_light": "Hell",
        "color_label": "Akzentfarbe:",
        "section_generation": "Generierungseinstellungen",
        "section_edition": "Bearbeitungseinstellungen",
        "section_correction": "Korrektureinstellungen",
        "steps_label": "Schritte:",
        "cfg_label": "CFG:",
        "denoise_label": "Stärke:",
        "guidance_label": "Führungsstärke:",
        
        # --- History & Status ---
        "history_prev_tooltip": "Vorheriges Bild",
        "history_next_tooltip": "Nächstes Bild",
        "status_ready": "Bereit. Geben Sie einen Prompt zum Generieren ein.",
        "status_ready_to_modify": "Bereit. Passen Sie den Prompt an und ändern Sie das Bild.",
        "status_initializing": "Initialisiere...",
        "status_loading_libs": "Lade Backend-Bibliotheken...",
        "status_init_done": "Backend bereit.",
        "status_unloading": "Entlade Modelle...",
        "status_unloaded": "Modelle entladen.",
        "status_generating": "Generiere...",
        "status_modifying": "Ändere Bild...",
        "status_correcting": "Korrigiere Bild...",
        "status_diffusion": "Diffusion: Schritt {0} / {1}...",
        "status_generation_done": "Fertig!",
        "status_generation_cancelled": "Vorgang abgebrochen.",
        "status_error": "Fehler: {0}",
        "image_placeholder": "Importieren Sie ein Bild oder schreiben Sie einen Prompt zum Generieren.",
        "image_saved_success": "Bild gespeichert: {0}",
        "image_saved_error": "Speicherfehler: {0}",

        # --- Backend Messages ---
        "eco_loading_clip": "Öko: Lade CLIP/T5...", "eco_unloading_clip": "Öko: Entlade CLIP/T5...",
        "eco_loading_dit": "Öko: Lade DiT-Modell...", "eco_unloading_dit": "Öko: Entlade DiT-Modell...",
        "eco_loading_vae": "Öko: Lade VAE...", "eco_unloading_vae": "Öko: Entlade VAE...",
        "eco_loading_vae_clip": "Öko: Lade VAE & CLIP...", "eco_unloading_vae_clip": "Öko: Entlade VAE & CLIP...",
        "perf_loading_models": "Lade alle Modelle...", "perf_preparing_nodes": "Bereite Workflow vor...",
        "perf_generating": "Generiere...", "perf_done": "Fertig (Modelle im Speicher behalten).",
        
        # --- Nouveaux messages pour le mode Eco ---
        "eco_status_encode_vae": "Öko: Kodiere Ausgangsbild...",
        "eco_status_encode_clip": "Öko: Kodiere Prompt...",
        "eco_status_sampling": "Öko: Generiere mit DiT-Modell...",
        "eco_status_decode_vae": "Öko: Dekodiere Endbild..."
    },
    "zh": {
        # --- General ---
        "window_title": "Flux Kontext 图像工作室",
        "app_mode_label": "应用模式：",
        "mode_generate": "生成",
        "mode_edit": "编辑",
        "positive_prompt_label": "提示词：",
        "memory_management_label": "内存模式：",
        "mode_performant": "性能模式",
        "mode_economical": "经济模式",
        "size_label": "尺寸：",
        
        # --- Buttons ---
        "settings_button": "设置",
        "generate_button": "生成",
        "modify_button": "修改图像",
        "correct_button": "校正图像",
        "cancel_button": "取消",
        "import_button": "导入图像",
        "save_button": "保存",

        # --- Settings Window ---
        "settings_window_title": "应用设置",
        "save_and_close_button": "保存并关闭",
        "section_accessibility": "辅助功能",
        "language_label": "语言：",
        "theme_label": "主题：",
        "theme_dark": "深色",
        "theme_light": "浅色",
        "color_label": "强调色：",
        "section_generation": "生成设置",
        "section_edition": "编辑设置",
        "section_correction": "校正设置",
        "steps_label": "步数：",
        "cfg_label": "CFG：",
        "denoise_label": "强度：",
        "guidance_label": "引导强度：",
        
        # --- History & Status ---
        "history_prev_tooltip": "上一张图片",
        "history_next_tooltip": "下一张图片",
        "status_ready": "准备就绪。请输入提示词以生成。",
        "status_ready_to_modify": "准备就绪。请调整提示词并修改图像。",
        "status_initializing": "正在初始化...",
        "status_loading_libs": "正在加载后端库...",
        "status_init_done": "后端准备就绪。",
        "status_unloading": "正在卸载模型...",
        "status_unloaded": "模型已卸载。",
        "status_generating": "正在生成...",
        "status_modifying": "正在修改图像...",
        "status_correcting": "正在校正图像...",
        "status_diffusion": "扩散：第 {0} / {1} 步...",
        "status_generation_done": "完成！",
        "status_generation_cancelled": "操作已取消。",
        "status_error": "错误：{0}",
        "image_placeholder": "导入图像或输入提示词以生成。",
        "image_saved_success": "图像已保存：{0}",
        "image_saved_error": "保存错误：{0}",

        # --- Backend Messages ---
        "eco_loading_clip": "经济：正在加载 CLIP/T5...", "eco_unloading_clip": "经济：正在卸载 CLIP/T5...",
        "eco_loading_dit": "经济：正在加载 DiT 模型...", "eco_unloading_dit": "经济：正在卸载 DiT 模型...",
        "eco_loading_vae": "经济：正在加载 VAE...", "eco_unloading_vae": "经济：正在卸载 VAE...",
        "eco_loading_vae_clip": "经济：正在加载 VAE 和 CLIP...", "eco_unloading_vae_clip": "经济：正在卸载 VAE 和 CLIP...",
        "perf_loading_models": "正在加载所有模型...", "perf_preparing_nodes": "正在准备工作流...",
        "perf_generating": "正在生成...", "perf_done": "已完成（模型保留在内存中）。",
        
        # --- Nouveaux messages pour le mode Eco ---
        "eco_status_encode_vae": "经济：正在编码初始图像...",
        "eco_status_encode_clip": "经济：正在编码提示词...",
        "eco_status_sampling": "经济：正在使用 DiT 模型生成...",
        "eco_status_decode_vae": "经济：正在解码最终图像..."
    }
}

LANGUAGES = {"en": "English", "fr": "Français", "es": "Español", "de": "Deutsch", "zh": "中文"}

class LanguageManager:
    # ... (le reste de la classe est inchangé) ...
    def __init__(self, default_language='en'):
        self.language = default_language
        self.translations = TRANSLATIONS
    def set_language(self, lang_code):
        if lang_code in self.translations: self.language = lang_code
    def get(self, key, *args):
        text = self.translations.get(self.language, self.translations['en']).get(key, key)
        return text.format(*args) if args else text