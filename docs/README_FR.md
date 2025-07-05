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

## Installation automatique

Choisissez la méthode d'installation qui vous convient le mieux.

### Méthode 1 : via l'Exécutable d'Installation

Cette méthode est la plus directe et simule l'installation d'une application Windows classique. Elle est parfaite si vous préférez un simple fichier à télécharger et à lancer, sans manipulation de code.

#### 1. Téléchargement
Téléchargez la dernière version de l'exécutable depuis la section [Releases de GitHub](https://github.com/Juste-Leo2/FastAPP-Flux-Kontext/releases).

#### 2. Lancement
Windows Defender SmartScreen peut bloquer l'exécution de l'application, car elle n'est pas encore largement reconnue.
<br>
<img src="windows_screen.png" alt="Écran Windows Defender SmartScreen" width="500">
<br>
Pour continuer, cliquez sur **Informations complémentaires**, puis sur **Exécuter quand même**.

#### 3. Emplacement d'installation
Préférez un emplacement d'installation standard (comme votre Bureau ou le dossier Documents). Évitez les dossiers système protégés comme `C:\Program Files`, qui pourraient causer des problèmes de permissions.

---

### Méthode 2 : via les Scripts du Dépôt (Transparence et Contrôle)

Cette méthode vous offre un contrôle total et une transparence complète. Elle est recommandée si vous préférez éviter les exécutables pré-compilés ou si vous souhaitez inspecter le code avant de l'exécuter. Bien que l'obtention du code soit une étape initiale, **l'installation reste entièrement automatique grâce aux scripts fournis**.

Vous pouvez inspecter le code des scripts avant de les lancer pour vérifier leur contenu :
- La logique d'installation est visible dans `setup.bat`, `src/setup.ps1` et `src/install_steps.bat`.
- Le script de lancement de l'application est `run.bat` et `src/run.ps1`.

#### 1. Obtenir le Code Source
Vous avez deux options :

*   **Option A (avec Git) :** Ouvrez un terminal et clonez le dépôt.
    ```bash
    git clone https://github.com/Juste-Leo2/FastAPP-Flux-Kontext.git
    cd FastAPP-Flux-Kontext
    ```
*   **Option B (sans Git) :** Cliquez sur le bouton vert `<> Code` en haut de la page du dépôt, puis sur `Download ZIP`. Décompressez l'archive dans le dossier de votre choix.

#### 2. Lancer l'Installation Automatique (`setup.bat`)
Une fois dans le dossier du projet, double-cliquez sur le fichier `setup.bat`. Ce script installera automatiquement tous les composants nécessaires.

**Avertissement :** Windows Defender SmartScreen peut également bloquer l'exécution de ce script. Comme pour l'exécutable, cliquez sur **Informations complémentaires**, puis sur **Exécuter quand même** pour l'autoriser.

#### 3. Lancer l'application (`run.bat`)
Après l'installation, double-cliquez sur `run.bat` pour démarrer l'application. Vous pouvez créer un raccourci de ce fichier sur votre bureau pour un accès plus facile.

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