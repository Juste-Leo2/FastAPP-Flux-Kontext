# src/utils/logic_co.py
import os
import gc
import time
import torch
import random

class GenerationCancelledError(Exception): pass

class ImageCorrector:
    def __init__(self, backend_modules, update_status_callback=None, lm=None):
        self.comfy_sample = backend_modules["comfy_sample"]
        self.model_management = backend_modules["model_management"]
        self.NODE_CLASS_MAPPINGS = backend_modules["nodes"].NODE_CLASS_MAPPINGS
        self.update_status_callback = update_status_callback
        self.lm = lm
        self.is_setup = False
        self.models = {}
        self.nodes = {} # Pour les instances de noeuds persistants
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        self.output_dir = os.path.join(project_root, 'output')
        self.vae_path = "ae.safetensors"
        self.clip_l_path = "clip_l.safetensors"
        self.t5_path = "t5xxl_fp8_e4m3fn_scaled.safetensors"
        self.dit_path = "svdq-int4_r32-flux.1-kontext-dev.safetensors"
        self.lora_path = "diffusion_pytorch_model.safetensors"

    def _update_status(self, message_key, *args):
        if self.update_status_callback:
            self.update_status_callback(message_key, *args)

    def _get_node(self, name):
        return self.NODE_CLASS_MAPPINGS[name]()

    def _ksampler_with_custom_callback(self, model, seed, steps, cfg, sampler_name, scheduler, positive, negative, latent, denoise=1.0, callback=None, cancel_event=None):
        latent_image = latent["samples"]
        def cancel_check_callback(step, x, x0, total_steps):
            if cancel_event and cancel_event.is_set():
                raise GenerationCancelledError("Generation cancelled.")
            if callback:
                callback(step, x0, x, total_steps)
        noise = self.comfy_sample.prepare_noise(latent_image, seed)
        samples = self.comfy_sample.sample(model, noise, steps, cfg, sampler_name, scheduler, positive, negative, latent_image, denoise=denoise, callback=cancel_check_callback, disable_pbar=True, seed=seed)
        return ({"samples": samples},)

    def setup_persistent_environment(self):
        if self.is_setup:
            return
        self._update_status("perf_loading_models")
        # Charger les modèles
        self.models['vae'] = self._get_node('VAELoader').load_vae(vae_name=self.vae_path)[0]
        self.models['clip'] = self._get_node('DualCLIPLoader').load_clip(clip_name1=self.t5_path, clip_name2=self.clip_l_path, type="flux")[0]
        dit_model_base = self._get_node('NunchakuFluxDiTLoader').load_model(model_path=self.dit_path, attention="nunchaku-fp16", cache_threshold=0, cpu_offload="auto", device_id=0, data_type="bfloat16", i2f_mode="enabled")[0]
        self.models['dit'] = self._get_node('NunchakuFluxLoraLoader').load_lora(lora_name=self.lora_path, lora_strength=1.0, model=dit_model_base)[0]
        del dit_model_base
        gc.collect()

        # Instancier les noeuds de workflow une seule fois
        self._update_status("perf_preparing_nodes")
        self.nodes['load_image'] = self._get_node('LoadImage')
        self.nodes['vae_encode'] = self._get_node('VAEEncode')
        self.nodes['clip_text_encode'] = self._get_node('CLIPTextEncode')
        self.nodes['vae_decode'] = self._get_node('VAEDecode')
        
        self.is_setup = True
        self._update_status("status_init_done")

    def unload_all_models(self):
        if not self.is_setup:
            return
        self._update_status("status_unloading")
        self.models.clear()
        self.nodes.clear() # Vider aussi les instances de noeuds
        self.is_setup = False
        self.model_management.unload_all_models()
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        self._update_status("status_unloaded")

    def correct(self, **kwargs):
        """Dispatcher vers la méthode de correction appropriée en fonction du mode mémoire."""
        if kwargs.get("management_mode") == self.lm.get("mode_performant"):
            return self._correct_performant(**kwargs)
        else:
            return self._correct_economique(**kwargs)

    def _correct_performant(self, **kwargs):
        """Correction en mode performance, utilise les modèles et noeuds pré-chargés."""
        try:
            self.setup_persistent_environment()
            
            # Utiliser les modèles et noeuds pré-chargés
            vae = self.models['vae']
            clip = self.models['clip']
            final_model = self.models['dit']
            load_image_node = self.nodes['load_image']
            vae_encode_node = self.nodes['vae_encode']
            clip_text_encode_node = self.nodes['clip_text_encode']
            vae_decode_node = self.nodes['vae_decode']

            image_tensor, _ = load_image_node.load_image(image=kwargs["input_image_path"])
            latent, = vae_encode_node.encode(pixels=image_tensor, vae=vae)
            pos_cond, = clip_text_encode_node.encode(clip=clip, text="best quality, sharp focus")
            neg_cond, = clip_text_encode_node.encode(clip=clip, text="blurry, low quality, noise, artifacts")
            
            self._update_status("status_correcting")
            sampled_latent, = self._ksampler_with_custom_callback(
                model=final_model, seed=random.randint(0, 2**32-1), 
                steps=kwargs.get("steps", 5), cfg=kwargs.get("cfg", 1.0), 
                sampler_name="euler", scheduler="simple", 
                positive=pos_cond, negative=neg_cond, latent=latent, 
                denoise=kwargs.get("denoise", 0.2),
                callback=kwargs["progress_callback"], 
                cancel_event=kwargs["cancel_event"])
            decoded_image, = vae_decode_node.decode(samples=sampled_latent, vae=vae)
            self._update_status("perf_done")
            return self._save_result_image(decoded_image, kwargs["cancel_event"])
        finally:
            self.model_management.soft_empty_cache()
            gc.collect()

    def _correct_economique(self, **kwargs):
        """Correction en mode économique, charge/décharge les modèles séquentiellement."""
        cancel_event = kwargs["cancel_event"]
        vae_model, latent, clip_model, pos_cond, neg_cond, dit_model, sampled_latent, decoded_image = [None] * 8

        # --- Étape 1: Charger VAE, encoder l'image initiale, décharger VAE ---
        try:
            self._update_status("eco_loading_vae");
            if cancel_event.is_set(): raise GenerationCancelledError()
            vae_model = self._get_node('VAELoader').load_vae(vae_name=self.vae_path)[0]
            self._update_status("eco_status_encode_vae")
            image_tensor, _ = self._get_node('LoadImage').load_image(image=kwargs["input_image_path"])
            latent, = self._get_node('VAEEncode').encode(pixels=image_tensor, vae=vae_model)
        finally:
            self._update_status("eco_unloading_vae")
            del vae_model; self.model_management.unload_all_models(); gc.collect()

        # --- Étape 2: Charger CLIP, créer les prompts, décharger CLIP ---
        try:
            self._update_status("eco_loading_clip");
            if cancel_event.is_set(): raise GenerationCancelledError()
            clip_model = self._get_node('DualCLIPLoader').load_clip(clip_name1=self.t5_path, clip_name2=self.clip_l_path, type="flux")[0]
            pos_cond, = self._get_node('CLIPTextEncode').encode(clip=clip_model, text="best quality, sharp focus")
            neg_cond, = self._get_node('CLIPTextEncode').encode(clip=clip_model, text="blurry, low quality, noise, artifacts")
        finally:
            self._update_status("eco_unloading_clip")
            del clip_model; self.model_management.unload_all_models(); gc.collect()

        # --- Étape 3: Charger DiT, effectuer le sampling, décharger DiT ---
        try:
            self._update_status("eco_loading_dit")
            if cancel_event.is_set(): raise GenerationCancelledError()
            dit_model_base = self._get_node('NunchakuFluxDiTLoader').load_model(model_path=self.dit_path, attention="nunchaku-fp16", cache_threshold=0, cpu_offload="auto", device_id=0, data_type="bfloat16", i2f_mode="enabled")[0]
            dit_model = self._get_node('NunchakuFluxLoraLoader').load_lora(lora_name=self.lora_path, lora_strength=1.0, model=dit_model_base)[0]
            del dit_model_base
            self._update_status("eco_status_sampling")
            sampled_latent, = self._ksampler_with_custom_callback(model=dit_model, seed=random.randint(0, 2**32-1), steps=kwargs.get("steps", 5), cfg=kwargs.get("cfg", 1.0), sampler_name="euler", scheduler="simple", positive=pos_cond, negative=neg_cond, latent=latent, denoise=kwargs.get("denoise", 0.2), callback=kwargs["progress_callback"], cancel_event=cancel_event)
        finally:
            self._update_status("eco_unloading_dit")
            del dit_model; self.model_management.unload_all_models(); gc.collect()

        # --- Étape 4: Charger VAE, décoder l'image finale, décharger VAE ---
        try:
            self._update_status("eco_loading_vae")
            if sampled_latent is None: raise GenerationCancelledError()
            vae_model = self._get_node('VAELoader').load_vae(vae_name=self.vae_path)[0]
            self._update_status("eco_status_decode_vae")
            decoded_image, = self._get_node('VAEDecode').decode(samples=sampled_latent, vae=vae_model)
        finally:
            self._update_status("eco_unloading_vae")
            del vae_model; self.model_management.unload_all_models(); gc.collect()

        return self._save_result_image(decoded_image, cancel_event) if decoded_image is not None else None

    def _save_result_image(self, decoded_image, cancel_event):
        timestamp = time.strftime('%Y%m%d-%H%M%S')
        image_to_save = decoded_image.detach()
        result = self._get_node('SaveImage').save_images(images=image_to_save, filename_prefix=f"flux_correct_{timestamp}")
        filepath = os.path.join(self.output_dir, result['ui']['images'][0]['filename'])
        if not cancel_event.is_set():
            self._update_status("status_generation_done")
        return filepath