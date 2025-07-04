<div align="left">
  <a href="../README.md" target="_blank"><img src="https://img.shields.io/badge/🇬🇧-Back%20to%20English-555555?style=flat&labelColor=333" alt="Back to English" /></a>
</div>

# FastAPP-Flux-Kontext

Génération et édition rapides d'images dans une seule application.

<p align="center">
  <img src="app.png" alt="Interface de FastAPP-Flux-Kontext">
</p>

## Prérequis

**Système et Matériel**
- Windows 10/11
- GPU NVIDIA compatible avec CUDA 12.6
- 16 Go de RAM (minimum)
- 4 Go de VRAM (minimum)
- *Note : Le code a été testé sur une configuration avec 64 Go de RAM et 12 Go de VRAM.*

---

## Installation Automatique

### 1. Téléchargement

Utilisez l'exécutable disponible dans les [releases GitHub](https://github.com/Juste-Leo2/FastAPP-Flux-Kontext/releases).

### 2. Lancement

L'écran Windows Defender SmartScreen peut bloquer l'exécution de l'application, la considérant à tort comme un logiciel non reconnu.
<br>
<img src="windows_screen.png" alt="Écran Windows Defender SmartScreen" width="500">
<br>
Cliquez sur **Informations complémentaires**, puis sur **Exécuter quand même**.

### 3. Emplacement d'installation

Privilégiez des emplacements standards (par exemple, sur votre bureau ou dans vos documents). Évitez les dossiers système protégés comme `C:\Program Files`.

---

## Installation Manuelle

**Logiciels Requis**
- [Anaconda](https://www.anaconda.com/products/individual)

### 1. Cloner le dépôt

Commencez par cloner le dépôt GitHub dans le répertoire de votre choix.

```bash
git clone https://github.com/Juste-Leo2/FastAPP-Flux-Kontext.git
cd FastAPP-Flux-Kontext
```

### 2. Créer et activer l'environnement Conda

Créez un environnement Conda spécifique pour ce projet et activez-le.

```bash
conda create -n flux_env python=3.12.1 ca-certificates certifi openssl -y
conda activate flux_env
```

### 3. Installer CUDA

Installez la version de CUDA compatible via Conda.

```bash
conda install -c nvidia/label/cuda-12.6.0 cuda -y
```

### 4. Installer uv

Installez `uv`, un gestionnaire de paquets plus rapide pour Python.

```bash
pip install uv
```

### 5. Installer les dépendances Python

Installez toutes les dépendances du projet listées dans le fichier `requirements.txt`.

```bash
uv pip install -r requirements.txt
```

### 6. Installer PyTorch avec support CUDA

Installez la version appropriée de PyTorch pour le support du GPU.

```bash
uv pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu126 --reinstall
```

### 7. Vérifier la détection du GPU par PyTorch

Exécutez la commande suivante pour vous assurer que votre GPU est bien détecté.

```bash
python -c "import torch; assert torch.cuda.is_available(), 'PyTorch ne détecte pas CUDA !'"
```

### 8. Télécharger les modèles

Téléchargez les modèles requis depuis les liens directs ci-dessous et placez-les dans le dossier `models/`.

- [Télécharger Diffuser (FLUX.1)](https://huggingface.co/mit-han-lab/nunchaku-flux.1-kontext-dev/resolve/main/svdq-int4_r32-flux.1-kontext-dev.safetensors)
- [Télécharger Autoencoder (AE)](https://huggingface.co/Comfy-Org/Lumina_Image_2.0_Repackaged/resolve/main/split_files/vae/ae.safetensors)
- [Télécharger T5 Encoder](https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn_scaled.safetensors)
- [Télécharger CLIP-L Encoder](https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors)
- [Télécharger LoRA (Turbo)](https://huggingface.co/alimama-creative/FLUX.1-Turbo-Alpha/resolve/main/diffusion_pytorch_model.safetensors)

La structure de votre dossier `models/` doit ressembler à ceci :

```
FastAPP-Flux-Kontext/
└── models/
    ├── svdq-int4_r32-flux.1-kontext-dev.safetensors
    ├── ae.safetensors
    ├── t5xxl_fp8_e4m3fn_scaled.safetensors
    ├── clip_l.safetensors
    └── diffusion_pytorch_model.safetensors
```

### 9. Lancer l'application

Une fois l'installation terminée, lancez l'application avec la commande suivante :

```bash
python src/main.py
```

---

## Remerciements

- **[ComfyUI](https://github.com/comfyanonymous/ComfyUI)** : pour ce projet incroyable qui a servi de base à une grande partie du code.
- **[black-forest-labs](https://huggingface.co/black-forest-labs)** : pour avoir partagé les poids originaux de FLUX-Kontext.
- **[mit-han-lab](https://huggingface.co/mit-han-lab)** : pour avoir quantifié FLUX-Kontext, offrant ainsi un meilleur rapport taille/performance.

---

## Licence

### Code du Projet

Le code de ce projet est distribué sous la Licence Publique Générale GNU v3.0 (GPLv3). Vous êtes libre d'utiliser, de partager et de modifier le code selon les termes spécifiés dans le fichier [LICENSE](../LICENSE).

### Modèles

**Important :** Les modèles pré-entraînés nécessaires pour faire fonctionner cette application sont soumis à une licence distincte : la **[Licence Non-Commerciale FLUX.1 [dev]](https://huggingface.co/black-forest-labs/FLUX.1-Kontext-dev/blob/main/LICENSE.md)**.

En téléchargeant et en utilisant ces modèles, vous acceptez de vous conformer à ses termes, qui interdisent strictement toute utilisation commerciale.