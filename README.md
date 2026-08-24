# Digital Human Pipeline

个人数字人项目：文本 → GPT-SoVITS 语音克隆 → LivePortrait 人脸驱动 → 数字人视频。

## 环境信息

| 项目 | 配置 |
|------|------|
| 操作系统 | Windows |
| GPU | NVIDIA GeForce RTX 3050 Ti Laptop (4GB VRAM) |
| Anaconda | `D:\ProgramData\` |
| 虚拟环境目录 | `D:\conda_envs`（已配置，不占 C 盘） |
| 包缓存目录 | `D:\conda_pkgs` |
| Python | 3.10 |
| PyTorch | CUDA 11.8 |
| 项目根目录 | `D:\digital_human` |

## 目录结构

```
D:\digital_human
├── LivePortrait/       # [Git 克隆] 人脸驱动项目（不纳入本仓库）
├── GPT-SoVITS/         # [Git 克隆] 语音克隆项目（不纳入本仓库）
├── ref/                # 人脸参考素材（图片/视频）
├── outputs/            # 训练好的音色模型、输出视频
├── run_pipeline.py     # 核心串联脚本
├── README.md
└── .gitignore
```

## 快速开始

### 1. 创建并激活虚拟环境

打开 **Anaconda Prompt**（D 盘安装的那个）：

```bash
conda create -n digital_human python=3.10 -y
conda activate digital_human
conda install -y ffmpeg
```

> 虚拟环境会自动创建在 `D:\conda_envs\digital_human`，不占用 C 盘。

### 2. 安装 PyTorch（CUDA 11.8）

```bash
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

验证 GPU：

```bash
python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0))"
```

应输出 `True` 和 `NVIDIA GeForce RTX 3050 Ti Laptop GPU`。

### 3. 克隆两个源码项目

```bash
D:
cd digital_human
git clone https://github.com/KwaiVGI/LivePortrait.git
git clone https://github.com/RVC-Boss/GPT-SoVITS.git
```

### 4. 安装项目依赖

#### LivePortrait

```bash
cd LivePortrait
pip install -r requirements.txt
python download_weights.py
cd ..
```

#### GPT-SoVITS

```bash
cd GPT-SoVITS
pip install -r requirements.txt
cd ..
```

### 5. 准备素材

- **人脸参考**：将图片或视频放入 `ref/` 目录
- **音色模型**：使用 GPT-SoVITS WebUI 训练 5~10 分钟人声，导出 `.pth` + `.json` 到 `outputs/`
- 修改 `run_pipeline.py` 顶部 CONFIG 区域的路径为实际文件名

### 6. 运行

```bash
python run_pipeline.py --text "大家好，这是我的个人数字分身演示" --output outputs/my_demo.mp4
```

## 注意事项

### RTX 3050 Ti (4GB) 显存优化

- LivePortrait 推理时已默认设置 `--resize 256` 降低分辨率
- 推理前关闭其他占用显卡的程序（浏览器、游戏等）
- 如仍遇 CUDA OOM，可进一步降低分辨率或使用 CPU 推理（`--device_id -1`）

### 路径规范

- 所有文件、文件夹**不要使用中文命名**
- 路径中避免空格

### 常见问题

| 问题 | 解决方案 |
|------|----------|
| `conda` 命令找不到 | 使用 Anaconda Prompt，而非普通 cmd/PowerShell |
| CUDA out of memory | 降低 LivePortrait 推理分辨率，关闭其他 GPU 程序 |
| ffmpeg 报错 | `conda install -y ffmpeg` 确认安装成功 |
| GPT-SoVITS 推理参数不对 | 以 GPT-SoVITS 仓库实际文档为准，可能需要用 API 方式调用 |

## Git 仓库说明

本仓库只包含自定义串联脚本和配置，`LivePortrait/` 和 `GPT-SoVITS/` 为第三方克隆仓库，不纳入版本控制（已在 `.gitignore` 中排除）。
