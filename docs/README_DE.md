<div align="left">
  <a href="../README.md" target="_blank"><img src="https://img.shields.io/badge/🇬🇧-Back%20to%20English-555555?style=flat&labelColor=333" alt="Back to English" /></a>
</div>

# FastAPP-Flux-Kontext

Schnelle Bilderzeugung und -bearbeitung in einer einzigen Anwendung.

<p align="center">
  <img src="app.png" alt="FastAPP-Flux-Kontext Benutzeroberfläche">
</p>

## Voraussetzungen

**System & Hardware**
- Windows 10/11
- NVIDIA GPU, kompatibel mit CUDA 12.6
- 16 GB RAM (Minimum)
- 4 GB VRAM (Minimum)
- *Hinweis: Dieser Code wurde auf einem System mit 64 GB RAM und 12 GB VRAM getestet.*

---

## Automatische Installation

### 1. Herunterladen

Verwenden Sie die ausführbare Datei, die in den [GitHub Releases](https://github.com/Juste-Leo2/FastAPP-Flux-Kontext/releases) verfügbar ist.

### 2. Starten

Windows Defender SmartScreen kann die Ausführung der Anwendung blockieren, da sie als nicht erkannte Software identifiziert wird.
<br>
<img src="windows_screen.png" alt="Windows Defender SmartScreen-Meldung" width="500">
<br>
Klicken Sie auf **Weitere Informationen** und dann auf **Trotzdem ausführen**.

### 3. Installationspfad

Bevorzugen Sie Standard-Installationsorte (z. B. Ihren Desktop oder Ihren Dokumente-Ordner). Vermeiden Sie geschützte Systemordner wie `C:\Program Files`.

---

## Manuelle Installation

**Erforderliche Software**
- [Anaconda](https://www.anaconda.com/products/individual)

### 1. Repository klonen

Klonen Sie zunächst das GitHub-Repository in ein Verzeichnis Ihrer Wahl.

```bash
git clone https://github.com/Juste-Leo2/FastAPP-Flux-Kontext.git
cd FastAPP-Flux-Kontext
```

### 2. Conda-Umgebung erstellen und aktivieren

Erstellen Sie eine spezifische Conda-Umgebung für dieses Projekt und aktivieren Sie sie.

```bash
conda create -n flux_env python=3.12.1 ca-certificates certifi openssl -y
conda activate flux_env
```

### 3. CUDA installieren

Installieren Sie die kompatible CUDA-Version über Conda.

```bash
conda install -c nvidia/label/cuda-12.6.0 cuda -y
```

### 4. uv installieren

Installieren Sie `uv`, einen schnelleren Paketmanager für Python.

```bash
pip install uv
```

### 5. Python-Abhängigkeiten installieren

Installieren Sie alle Projektabhängigkeiten, die in der Datei `requirements.txt` aufgeführt sind.

```bash
uv pip install -r requirements.txt
```

### 6. PyTorch mit CUDA-Unterstützung installieren

Installieren Sie die passende PyTorch-Version für die GPU-Unterstützung.

```bash
uv pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu126 --reinstall
```

### 7. GPU-Erkennung durch PyTorch überprüfen

Führen Sie den folgenden Befehl aus, um sicherzustellen, dass Ihre GPU korrekt erkannt wird.

```bash
python -c "import torch; assert torch.cuda.is_available(), 'PyTorch hat CUDA nicht erkannt!'"
```

### 8. Modelle herunterladen

Laden Sie die erforderlichen Modelle über die direkten Links unten herunter und legen Sie sie im Ordner `models/` ab.

- [Diffuser (FLUX.1) herunterladen](https://huggingface.co/mit-han-lab/nunchaku-flux.1-kontext-dev/resolve/main/svdq-int4_r32-flux.1-kontext-dev.safetensors)
- [Autoencoder (AE) herunterladen](https://huggingface.co/Comfy-Org/Lumina_Image_2.0_Repackaged/resolve/main/split_files/vae/ae.safetensors)
- [T5 Encoder herunterladen](https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn_scaled.safetensors)
- [CLIP-L Encoder herunterladen](https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors)
- [LoRA (Turbo) herunterladen](https://huggingface.co/alimama-creative/FLUX.1-Turbo-Alpha/resolve/main/diffusion_pytorch_model.safetensors)

Die Struktur Ihres `models/`-Ordners sollte wie folgt aussehen:

```
FastAPP-Flux-Kontext/
└── models/
    ├── svdq-int4_r32-flux.1-kontext-dev.safetensors
    ├── ae.safetensors
    ├── t5xxl_fp8_e4m3fn_scaled.safetensors
    ├── clip_l.safetensors
    └── diffusion_pytorch_model.safetensors
```

### 9. Anwendung starten

Sobald die Einrichtung abgeschlossen ist, starten Sie die Anwendung mit dem folgenden Befehl:

```bash
python src/main.py
```

---

## Danksagungen

- **[ComfyUI](https://github.com/comfyanonymous/ComfyUI)**: für dieses unglaubliche Projekt, das als Grundlage für einen großen Teil des Codes diente.
- **[black-forest-labs](https://huggingface.co/black-forest-labs)**: für das Teilen der ursprünglichen FLUX-Kontext-Gewichte.
- **[mit-han-lab](https://huggingface.co/mit-han-lab)**: für die Quantisierung von FLUX-Kontext, was ein besseres Verhältnis von Größe zu Leistung bietet.

---

## Lizenz

### Projektcode

Der Code dieses Projekts wird unter der GNU General Public License v3.0 (GPLv3) vertrieben. Es steht Ihnen frei, den Code gemäß den in der [LICENSE](../LICENSE)-Datei angegebenen Bedingungen zu verwenden, zu teilen und zu ändern.

### Modelle

**Wichtig:** Die vorab trainierten Modelle, die zur Ausführung dieser Anwendung erforderlich sind, unterliegen einer separaten Lizenz: der **[FLUX.1 [dev] Non-Commercial License](https://huggingface.co/black-forest-labs/FLUX.1-Kontext-dev/blob/main/LICENSE.md)**.

Durch das Herunterladen und Verwenden dieser Modelle stimmen Sie deren Bedingungen zu, die jegliche kommerzielle Nutzung strikt untersagen.