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
        dit_model_base = self._get_node('NunchakuFluxDiTLoader').load_model(model_path=self.dit_path, attention="nunchaku-fp16", cache_threshold=-1.0, cpu_offload="auto", device_id=0, data_type="bfloat16", i2f_mode="enabled")[0]
        self.models['dit'] = self._get_node('NunchakuFluxLoraLoader').load_lora(lora_name=self.lora_path, lora_strength=1.0, model=dit_model_base)[0]
        del dit_model_base
        gc.collect()

        # Instancier les noeuds de workflow une seule fois
        self._update_status("perf_preparing_nodes")
        self.nodes['load_image'] = self._get_node('LoadImage')
        self.nodes['image_scale'] = self._get_node('FluxKontextImageScale')
        self.nodes['vae_encode'] = self._get_node('VAEEncode')
        self.nodes['clip_text_encode'] = self._get_node('CLIPTextEncode')
        self.nodes['conditioning_zero_out'] = self._get_node('ConditioningZeroOut')
        self.nodes['reference_latent'] = self._get_node('ReferenceLatent')
        self.nodes['flux_guidance'] = self._get_node('FluxGuidance')
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

    def edit(self, **kwargs):
        """Dispatcher vers la méthode d'édition appropriée en fonction du mode mémoire."""
        if kwargs.get("management_mode") == self.lm.get("mode_performant"):
            return self._edit_performant(**kwargs)
        else:
            return self._edit_economique(**kwargs)

    def _edit_performant(self, **kwargs):
        """Édition en mode performance, garde les modèles en mémoire."""
        try:
            self.setup_persistent_environment()
            
            # Utiliser les modèles et noeuds pré-chargés
            vae = self.models['vae']
            clip = self.models['clip']
            final_model = self.models['dit']
            load_image_node = self.nodes['load_image']
            image_scale_node = self.nodes['image_scale']
            vae_encode_node = self.nodes['vae_encode']
            clip_text_encode_node = self.nodes['clip_text_encode']
            conditioning_zero_out_node = self.nodes['conditioning_zero_out']
            reference_latent_node = self.nodes['reference_latent']
            flux_guidance_node = self.nodes['flux_guidance']
            vae_decode_node = self.nodes['vae_decode']

            image_tensor, _ = load_image_node.load_image(image=kwargs["input_image_path"])
            scaled_image, = image_scale_node.scale(image=image_tensor)
            latent, = vae_encode_node.encode(pixels=scaled_image, vae=vae)
            pos_cond, = clip_text_encode_node.encode(clip=clip, text=kwargs["positive_prompt"])
            neg_cond, = conditioning_zero_out_node.zero_out(conditioning=pos_cond)
            ref_latent_cond, = reference_latent_node.append(conditioning=pos_cond, latent=latent)
            guided_cond, = flux_guidance_node.append(guidance=kwargs["guidance"], conditioning=ref_latent_cond)
            
            self._update_status("perf_generating")
            sampled_latent, = self._ksampler_with_custom_callback(model=final_model, seed=random.randint(0, 2**32-1), steps=kwargs["steps"], cfg=kwargs["cfg"], sampler_name="euler", scheduler="simple", positive=guided_cond, negative=neg_cond, latent=latent, denoise=kwargs["denoise"], callback=kwargs["progress_callback"], cancel_event=kwargs["cancel_event"])
            decoded_image, = vae_decode_node.decode(samples=sampled_latent, vae=vae)
            self._update_status("perf_done")
            return self._save_result_image(decoded_image, kwargs["cancel_event"])
        finally:
            self.model_management.soft_empty_cache()
            gc.collect()

    def _edit_economique(self, **kwargs):
        """Édition en mode économique, charge/décharge les modèles séquentiellement."""
        cancel_event = kwargs["cancel_event"]
        vae_model, clip_model, latent, guided_cond, neg_cond, dit_model, sampled_latent, decoded_image = [None] * 8

        # --- Étape 1: Charger VAE+CLIP, encoder image et prompts, créer le conditionnement, décharger ---
        try:
            self._update_status("eco_loading_vae_clip");
            if cancel_event.is_set(): raise GenerationCancelledError()
            
            vae_model = self._get_node('VAELoader').load_vae(vae_name=self.vae_path)[0]
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
            self._update_status("eco_unloading_vae_clip")
            del vae_model, clip_model; self.model_management.unload_all_models(); gc.collect()

        # --- Étape 2: Charger DiT, effectuer le sampling, décharger DiT ---
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
            del dit_model; self.model_management.unload_all_models(); gc.collect()

        # --- Étape 3: Charger VAE, décoder l'image finale, décharger VAE ---
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
        result = self._get_node('SaveImage').save_images(images=image_to_save, filename_prefix=f"flux_edit_{timestamp}")
        filepath = os.path.join(self.output_dir, result['ui']['images'][0]['filename'])
        if not cancel_event.is_set():
            self._update_status("status_generation_done")
        return filepath