# src/utils/logic_edit.py
import os
import gc
import time
import torch
import random

class GenerationCancelledError(Exception): pass

class ImageEditor:
    def __init__(self, backend_modules, update_status_callback=None, lm=None):
        self.comfy_sample = backend_modules["comfy_sample"]
        self.model_management = backend_modules["model_management"]
        self.NODE_CLASS_MAPPINGS = backend_modules["nodes"].NODE_CLASS_MAPPINGS
        self.update_status_callback = update_status_callback
        self.lm = lm
        
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        
        self.output_dir = os.path.join(project_root, 'output')
        
        # --- Début de la modification ---
        
        # Définir le chemin vers le dossier des modèles de manière robuste
        models_dir = os.path.join(project_root, 'models')

        # Les autres chemins de modèles restent les mêmes
        self.vae_path = "ae.safetensors"
        self.clip_l_path = "clip_l.safetensors"
        self.t5_path = "t5xxl_fp8_e4m3fn_scaled.safetensors"
        self.lora_path = "diffusion_pytorch_model.safetensors"
        
        # Logique dynamique pour sélectionner le bon modèle DIT
        fp4_model_name = "svdq-fp4_r32-flux.1-kontext-dev.safetensors"
        int4_model_name = "svdq-int4_r32-flux.1-kontext-dev.safetensors"

        # Vérifie si le modèle pour RTX 5000 existe, sinon utilise l'autre par défaut
        if os.path.exists(os.path.join(models_dir, fp4_model_name)):
            self.dit_path = fp4_model_name
        else:
            self.dit_path = int4_model_name

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

    def edit(self, **kwargs):
        """Édition optimisée : le VAE reste chargé pendant toute la tâche."""
        cancel_event = kwargs["cancel_event"]
        vae_model, clip_model, latent, guided_cond, neg_cond, dit_model, sampled_latent, decoded_image = [None] * 8

        # --- Étape 1: Grand bloc pour gérer le VAE du début à la fin ---
        try:
            self._update_status("eco_loading_vae")
            if cancel_event.is_set(): raise GenerationCancelledError()
            vae_model = self._get_node('VAELoader').load_vae(vae_name=self.vae_path)[0]

            # --- Étape 2: Bloc interne pour charger CLIP, encoder, puis décharger CLIP seul ---
            try:
                self._update_status("eco_loading_clip")
                if cancel_event.is_set(): raise GenerationCancelledError()
                clip_model = self._get_node('DualCLIPLoader').load_clip(clip_name1=self.t5_path, clip_name2=self.clip_l_path, type="flux")[0]
                
                self._update_status("eco_status_encode_vae")
                image_tensor, _ = self._get_node('LoadImage').load_image(image=kwargs["input_image_path"])
                scaled_image, = self._get_node('FluxKontextImageScale').scale(image=image_tensor)
                latent, = self._get_node('VAEEncode').encode(pixels=scaled_image, vae=vae_model)
                
                self._update_status("eco_status_encode_clip")
                pos_cond, = self._get_node('CLIPTextEncode').encode(clip=clip_model, text=kwargs["positive_prompt"])
                neg_cond, = self._get_node('ConditioningZeroOut').zero_out(conditioning=pos_cond)
                ref_latent_cond, = self._get_node('ReferenceLatent').append(conditioning=pos_cond, latent=latent)
                guided_cond, = self._get_node('FluxGuidance').append(guidance=kwargs["guidance"], conditioning=ref_latent_cond)

            finally:
                self._update_status("eco_unloading_clip")
                del clip_model; gc.collect()
                if torch.cuda.is_available(): torch.cuda.empty_cache()

            # --- Étape 3: Bloc interne pour charger DiT, sampler, puis décharger DiT seul ---
            try:
                self._update_status("eco_loading_dit")
                if cancel_event.is_set(): raise GenerationCancelledError()
                
                dit_model_base = self._get_node('NunchakuFluxDiTLoader').load_model(model_path=self.dit_path, attention="nunchaku-fp16", cache_threshold=-1.0, cpu_offload="auto", device_id=0, data_type="bfloat16", i2f_mode="enabled")[0]
                dit_model = self._get_node('NunchakuFluxLoraLoader').load_lora(lora_name=self.lora_path, lora_strength=1.0, model=dit_model_base)[0]
                del dit_model_base
                
                self._update_status("eco_status_sampling")
                sampled_latent, = self._ksampler_with_custom_callback(model=dit_model, seed=random.randint(0, 2**32-1), steps=kwargs["steps"], cfg=kwargs["cfg"], sampler_name="euler", scheduler="simple", positive=guided_cond, negative=neg_cond, latent=latent, denoise=kwargs["denoise"], callback=kwargs["progress_callback"], cancel_event=kwargs["cancel_event"])
            
            finally:
                self._update_status("eco_unloading_dit")
                del dit_model; gc.collect()
                if torch.cuda.is_available(): torch.cuda.empty_cache()

            # --- Étape 4: Décodage final avec le VAE toujours chargé ---
            if sampled_latent is None: raise GenerationCancelledError()
            self._update_status("eco_status_decode_vae")
            decoded_image, = self._get_node('VAEDecode').decode(samples=sampled_latent, vae=vae_model)

        finally:
            # --- Étape 5: Déchargement final du VAE et nettoyage global ---
            self._update_status("eco_unloading_vae")
            del vae_model, latent, guided_cond, neg_cond, sampled_latent
            self.model_management.unload_all_models()
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

        return self._save_result_image(decoded_image, cancel_event) if decoded_image is not None else None

    def _save_result_image(self, decoded_image, cancel_event):
        timestamp = time.strftime('%Y%m%d-%H%M%S')
        image_to_save = decoded_image.detach()
        result = self._get_node('SaveImage').save_images(images=image_to_save, filename_prefix=f"flux_edit_{timestamp}")
        filepath = os.path.join(self.output_dir, result['ui']['images'][0]['filename'])
        if not cancel_event.is_set():
            self._update_status("status_generation_done")
        return filepath