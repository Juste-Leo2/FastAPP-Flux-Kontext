<div align="left">
  <a href="../README.md" target="_blank"><img src="https://img.shields.io/badge/🇬🇧-Back%20to%20English-555555?style=flat&labelColor=333" alt="Back to English" /></a>
</div>

# FastAPP-Flux-Kontext

在单个应用程序中实现快速图像生成和编辑。

<p align="center">
  <img src="app.png" alt="FastAPP-Flux-Kontext 界面">
</p>

## 系统要求

**系统与硬件**
- Windows 10/11
- 兼容 CUDA 12.6 的 NVIDIA GPU
- 16 GB RAM (最低)
- 4 GB VRAM (最低)
- *注意：此代码已在 64 GB RAM 和 12 GB VRAM 的配置上进行测试。*

---

## 自动安装

### 1. 下载

使用 [GitHub Releases](https://github.com/Juste-Leo2/FastAPP-Flux-Kontext/releases) 中提供的可执行文件。

### 2. 启动

Windows Defender SmartScreen 可能会阻止应用程序运行，因为它会将其识别为无法识别的软件。
<br>
<img src="windows_screen.png" alt="Windows Defender SmartScreen 提示" width="500">
<br>
点击**更多信息**，然后点击**仍要运行**。

### 3. 安装路径

请选择标准安装位置（例如，您的桌面或“文档”文件夹）。避免使用受保护的系统文件夹，如 `C:\Program Files`。

---

## 手动安装

**所需软件**
- [Anaconda](https://www.anaconda.com/products/individual)

### 1. 克隆仓库

首先，将 GitHub 仓库克隆到您选择的目录中。

```bash
git clone https://github.com/Juste-Leo2/FastAPP-Flux-Kontext.git
cd FastAPP-Flux-Kontext
```

### 2. 创建并激活 Conda 环境

为此项目创建一个特定的 Conda 环境并激活它。

```bash
conda create -n flux_env python=3.12.1 ca-certificates certifi openssl -y
conda activate flux_env
```

### 3. 安装 CUDA

通过 Conda 安装兼容的 CUDA 版本。

```bash
conda install -c nvidia/label/cuda-12.6.0 cuda -y
```

### 4. 安装 uv

安装 `uv`，一个更快的 Python 包管理器。

```bash
pip install uv
```

### 5. 安装 Python 依赖项

安装 `requirements.txt` 文件中列出的所有项目依赖项。

```bash
uv pip install -r requirements.txt
```

### 6. 安装支持 CUDA 的 PyTorch

安装适合 GPU 支持的 PyTorch 版本。

```bash
uv pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu126 --reinstall
```

### 7. 验证 PyTorch 是否检测到 GPU

运行以下命令，确保您的 GPU 被正确检测到。

```bash
python -c "import torch; assert torch.cuda.is_available(), 'PyTorch 未检测到 CUDA！'"
```

### 8. 下载模型

从下面的直接链接下载所需的模型，并将它们放在 `models/` 文件夹中。

- [下载 Diffuser (FLUX.1)](https://huggingface.co/mit-han-lab/nunchaku-flux.1-kontext-dev/resolve/main/svdq-int4_r32-flux.1-kontext-dev.safetensors)
- [下载 Autoencoder (AE)](https://huggingface.co/Comfy-Org/Lumina_Image_2.0_Repackaged/resolve/main/split_files/vae/ae.safetensors)
- [下载 T5 Encoder](https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn_scaled.safetensors)
- [下载 CLIP-L Encoder](https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors)
- [下载 LoRA (Turbo)](https://huggingface.co/alimama-creative/FLUX.1-Turbo-Alpha/resolve/main/diffusion_pytorch_model.safetensors)

您的 `models/` 文件夹结构应如下所示：

```
FastAPP-Flux-Kontext/
└── models/
    ├── svdq-int4_r32-flux.1-kontext-dev.safetensors
    ├── ae.safetensors
    ├── t5xxl_fp8_e4m3fn_scaled.safetensors
    ├── clip_l.safetensors
    └── diffusion_pytorch_model.safetensors
```

### 9. 启动应用程序

安装完成后，使用以下命令启动应用程序：

```bash
python src/main.py
```

---

## 致谢

- **[ComfyUI](https://github.com/comfyanonymous/ComfyUI)**：感谢这个令人难以置信的项目，它为大部分代码提供了基础。
- **[black-forest-labs](https://huggingface.co/black-forest-labs)**：感谢分享原始的 FLUX-Kontext 权重。
- **[mit-han-lab](https://huggingface.co/mit-han-lab)**：感谢对 FLUX-Kontext 进行量化，提供了更好的尺寸与性能比。

---

## 许可证

### 项目代码

本项目的代码根据 GNU 通用公共许可证 v3.0 (GPLv3) 分发。您可以根据 [LICENSE](../LICENSE) 文件中指定的条款自由使用、共享和修改代码。

### 模型

**重要提示：** 运行此应用程序所需的预训练模型受单独的许可证约束：**[FLUX.1 [dev] 非商业许可证](https://huggingface.co/black-forest-labs/FLUX.1-Kontext-dev/blob/main/LICENSE.md)**。

下载和使用这些模型即表示您同意其条款，该条款严格禁止任何商业用途。