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
- 已安装最新驱动程序的 NVIDIA RTX 显卡。
- 16 GB RAM (最低)
- 4 GB VRAM (最低)
- *注意：此代码已在 64 GB RAM 和 12 GB VRAM 的配置上进行测试。*

---

## 自动安装

请选择最适合您的安装方法。

### 方法一：通过安装可执行文件

这是最直接的方法，模拟了标准的 Windows 应用程序安装过程。如果您倾向于下载并运行单个文件，而不想处理任何代码，那么这是完美的选择。

#### 1. 下载
从 [GitHub Releases](https://github.com/Juste-Leo2/FastAPP-Flux-Kontext/releases) 部分下载最新的可执行文件。

#### 2. 启动
Windows Defender SmartScreen 可能会阻止应用程序运行，因为它是一个未被广泛识别的软件。
<br>
<img src="windows_screen.png" alt="Windows Defender SmartScreen 屏幕" width="500">
<br>
要继续，请点击 **更多信息**，然后点击 **仍要运行**。

#### 3. 安装路径
请选择标准的安装位置（例如您的桌面或文档文件夹）。避免受保护的系统文件夹，如 `C:\Program Files`，这可能会导致权限问题。

---

### 方法二：通过仓库脚本（透明与可控）

此方法为您提供完全的控制和透明度。如果您希望避免使用预编译的可执行文件，或者想在运行前检查代码，推荐使用此方法。尽管获取代码是第一步，但**借助提供的脚本，安装过程仍然是全自动的**。

您可以在运行前检查脚本代码以验证其内容：
- 安装逻辑在 `setup.bat`、`src/setup.ps1` 和 `src/install_steps.bat` 文件中可见。
- 应用程序的启动脚本是 `run.bat` 和 `src/run.ps1`。

#### 1. 获取源代码
您有两种选择：

*   **选项A (使用 Git):** 打开终端并克隆仓库。
    ```bash
    git clone https://github.com/Juste-Leo2/FastAPP-Flux-Kontext.git
    cd FastAPP-Flux-Kontext
    ```
*   **选项B (不使用 Git):** 在仓库页面顶部点击绿色的 `<> Code` 按钮，然后点击 `Download ZIP`。将压缩包解压到您选择的文件夹中。

#### 2. 运行自动安装 (`setup.bat`)
进入项目文件夹后，双击 `setup.bat` 文件。此脚本将自动安装所有必需的组件。

**警告：** Windows Defender SmartScreen 也可能阻止此脚本运行。与可执行文件一样，请点击 **更多信息**，然后点击 **仍要运行** 以允许其执行。

#### 3. 启动应用程序 (`run.bat`)
安装完成后，双击 `run.bat` 以启动应用程序。您可以在桌面上为此文件创建一个快捷方式，以便更轻松地访问。



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
conda install -c nvidia/label/cuda-12.8.0 cuda -y
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
uv pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu128 --reinstall
```

### 7. 验证 PyTorch 是否检测到 GPU

运行以下命令，确保您的 GPU 被正确检测到。

```bash
python -c "import torch; assert torch.cuda.is_available(), 'PyTorch 未检测到 CUDA！'"
```


### 8. 下载模型

从以下链接下载所需的模型，并将它们放入 `models/` 文件夹中。

---

#### 主模型（扩散器）

**根据您的显卡选择：**

- **适用于 RTX 2000、3000、4000 显卡**  
  [svdq-int4_r32-flux.1-kontext-dev.safetensors](https://huggingface.co/mit-han-lab/nunchaku-flux.1-kontext-dev/resolve/main/svdq-int4_r32-flux.1-kontext-dev.safetensors)

- **适用于 RTX 5000 显卡**  
  [svdq-fp4_r32-flux.1-kontext-dev.safetensors](https://huggingface.co/mit-han-lab/nunchaku-flux.1-kontext-dev/resolve/main/svdq-fp4_r32-flux.1-kontext-dev.safetensors)

---

#### 其他所需模型

- [Autoencoder (AE)](https://huggingface.co/Comfy-Org/Lumina_Image_2.0_Repackaged/resolve/main/split_files/vae/ae.safetensors)  
- [T5 Encoder](https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn_scaled.safetensors)  
- [CLIP-L Encoder](https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors)  
- [LoRA (Turbo)](https://huggingface.co/alimama-creative/FLUX.1-Turbo-Alpha/resolve/main/diffusion_pytorch_model.safetensors)

---

### `models/` 文件夹的预期结构

```
models/
├── svdq-int4_r32-flux.1-kontext-dev.safetensors   （或 svdq-fp4_r32-flux.1-kontext-dev.safetensors，取决于您的显卡）
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