<div align="left">
  <a href="docs/README_FR.md" target="_blank"><img src="https://img.shields.io/badge/🇫🇷-Version%20Française-0073E6?style=flat&labelColor=333" alt="Version Française" /></a>
  <a href="docs/README_ES.md" target="_blank"><img src="https://img.shields.io/badge/🇪🇸-Versión%20Española-FFA500?style=flat&labelColor=333" alt="Versión Española" /></a>
  <a href="docs/README_DE.md" target="_blank"><img src="https://img.shields.io/badge/🇩🇪-Deutsche%20Version-FFD700?style=flat&labelColor=333" alt="Deutsche Version" /></a>
  <a href="docs/README_CN.md" target="_blank"><img src="https://img.shields.io/badge/🇨🇳-中文版-DE2910?style=flat&labelColor=333" alt="中文版" /></a>
</div>

# FastAPP-Flux-Kontext

Fast image generation and editing in a single application.

<p align="center">
  <img src="docs/app.png" alt="FastAPP-Flux-Kontext Interface">
</p>

## Prerequisites

**System & Hardware**
- Windows 10/11
- NVIDIA RTX graphics card with the latest drivers installed.
- 16 GB of RAM (minimum)
- 4 GB of VRAM (minimum)
- *Note: This code was tested on a setup with 64 GB of RAM and 12 GB of VRAM.*

---

## Automatic Installation

Choose the installation method that suits you best.

### Method 1: via the Installation Executable

This is the most direct method and simulates a standard Windows application installation. It's perfect if you prefer a single file to download and run, without handling any code.

#### 1. Download
Download the latest executable from the [GitHub Releases](https://github.com/Juste-Leo2/FastAPP-Flux-Kontext/releases) section.

#### 2. Launch
Windows Defender SmartScreen may prevent the application from running, identifying it as unrecognized software.
<br>
<img src="docs/windows_screen.png" alt="Windows Defender SmartScreen prompt" width="500">
<br>
To proceed, click on **More info**, then **Run anyway**.

#### 3. Installation Path
Prefer standard installation locations (e.g., your Desktop or Documents folder). Avoid protected system folders like `C:\Program Files`, which could cause permission issues.

---

### Method 2: via Repository Scripts (Transparency and Control)

This method gives you full control and complete transparency. It's recommended if you prefer to avoid pre-compiled executables or want to inspect the code before running it. Although getting the code is an initial step, **the installation remains fully automatic thanks to the provided scripts**.

You can inspect the scripts' code before running them to verify their content:
- The installation logic is visible in `setup.bat`, `src/setup.ps1`, and `src/install_steps.bat`.
- The application launch script is `run.bat` and `src/run.ps1`.

#### 1. Get the Source Code
You have two options:

*   **Option A (with Git):** Open a terminal and clone the repository.
    ```bash
    git clone https://github.com/Juste-Leo2/FastAPP-Flux-Kontext.git
    cd FastAPP-Flux-Kontext
    ```
*   **Option B (without Git):** Click the green `<> Code` button at the top of the repository page, then `Download ZIP`. Unzip the archive into a folder of your choice.

#### 2. Run the Automatic Installation (`setup.bat`)
Once inside the project folder, double-click the `setup.bat` file. This script will automatically install all necessary components.

**Warning:** Windows Defender SmartScreen may also block this script. As with the executable, click **More info**, then **Run anyway** to allow it.

#### 3. Launch the Application (`run.bat`)
After installation, double-click `run.bat` to start the application. You can create a shortcut for this file on your desktop for easier access.




---

## Manual Installation

**Required Software**
- [Anaconda](https://www.anaconda.com/products/individual)

### 1. Clone the Repository

Start by cloning the GitHub repository to a directory of your choice.

```bash
git clone https://github.com/Juste-Leo2/FastAPP-Flux-Kontext.git
cd FastAPP-Flux-Kontext
```

### 2. Create and Activate Conda Environment

Create a specific Conda environment for this project and activate it.

```bash
conda create -n flux_env python=3.12.1 ca-certificates certifi openssl -y
conda activate flux_env
```

### 3. Install CUDA

Install the compatible CUDA version via Conda.

```bash
conda install -c nvidia/label/cuda-12.8.0 cuda -y
```

### 4. Install uv

Install `uv`, a faster package manager for Python.

```bash
pip install uv
```

### 5. Install Python Dependencies

Install all project dependencies listed in the `requirements.txt` file.

```bash
uv pip install -r requirements.txt
```

### 6. Install PyTorch with CUDA Support

Install the appropriate PyTorch version for GPU support.

```bash
uv pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu128 --reinstall
```

### 7. Verify GPU Detection by PyTorch

Run the following command to ensure your GPU is correctly detected.

```bash
python -c "import torch; assert torch.cuda.is_available(), 'PyTorch did not detect CUDA!'"
```

### 8. Download the Models

Download the required models from the links below and place them in the `models/` folder.

---

#### Main Model (Diffuser)

**Choose according to your GPU:**

- **For RTX 2000, 3000, 4000 cards**  
  [svdq-int4_r32-flux.1-kontext-dev.safetensors](https://huggingface.co/mit-han-lab/nunchaku-flux.1-kontext-dev/resolve/main/svdq-int4_r32-flux.1-kontext-dev.safetensors)

- **For RTX 5000 cards**  
  [svdq-fp4_r32-flux.1-kontext-dev.safetensors](https://huggingface.co/mit-han-lab/nunchaku-flux.1-kontext-dev/resolve/main/svdq-fp4_r32-flux.1-kontext-dev.safetensors)

---

#### Other Required Models

- [Autoencoder (AE)](https://huggingface.co/Comfy-Org/Lumina_Image_2.0_Repackaged/resolve/main/split_files/vae/ae.safetensors)  
- [T5 Encoder](https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn_scaled.safetensors)  
- [CLIP-L Encoder](https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors)  
- [LoRA (Turbo)](https://huggingface.co/alimama-creative/FLUX.1-Turbo-Alpha/resolve/main/diffusion_pytorch_model.safetensors)

---

### Expected Folder Structure for `models/`

```
models/
├── svdq-int4_r32-flux.1-kontext-dev.safetensors   (or svdq-fp4_r32-flux.1-kontext-dev.safetensors depending on your GPU)
├── ae.safetensors
├── t5xxl_fp8_e4m3fn_scaled.safetensors
├── clip_l.safetensors
└── diffusion_pytorch_model.safetensors
```


### 9. Launch the Application

Once the setup is complete, launch the application with the following command:

```bash
python src/main.py
```

---

## Acknowledgements

- **[ComfyUI](https://github.com/comfyanonymous/ComfyUI)**: For this incredible project, which served as the basis for a large part of the code.
- **[black-forest-labs](https://huggingface.co/black-forest-labs)**: For sharing the original FLUX-Kontext weights.
- **[mit-han-lab](https://huggingface.co/mit-han-lab)**: For quantizing FLUX-Kontext, providing a better size-to-performance ratio.

---

## License

### Project Code

The code for this project is distributed under the GNU General Public License v3.0 (GPLv3). You are free to use, share, and modify the code under the terms specified in the [LICENSE](LICENSE) file.

### Models

**Important:** The pre-trained models required to run this application are subject to a separate license: the **[FLUX.1 [dev] Non-Commercial License](https://huggingface.co/black-forest-labs/FLUX.1-Kontext-dev/blob/main/LICENSE.md)**.

By downloading and using these models, you agree to its terms, which strictly prohibit any commercial use.


