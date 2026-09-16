# Digital Human & AI 漫剧生产平台

个人 AI 内容生产项目，包含两套可独立运行的框架：

1. **数字人流水线**：文本 → 语音克隆 → 人脸驱动 → 数字人视频
2. **AI 漫剧生产平台**：文案 → 配音 → 分镜 → 动画 → 口播 → 成片（ComfyUI 驱动）

## 环境信息

| 项目 | 配置 |
|------|------|
| 操作系统 | Windows |
| GPU | NVIDIA GeForce RTX 3050 Ti Laptop (4GB VRAM) |
| Anaconda | `D:\ProgramData\` |
| 虚拟环境目录 | `D:\conda_envs`（已配置，不占 C 盘） |
| 包缓存目录 | `D:\conda_pkgs` |
| Python | 3.10（`D:\conda_envs\digital_human`） |
| PyTorch | CUDA 11.8 |
| 项目根目录 | `D:\digital_human` |

## 框架一：数字人流水线

输入文字 → 生成语音 → 生成人脸视频 → 合并 → 输出完整数字人视频。

### 方案 A：GPT-SoVITS + LivePortrait

```bash
python run_digital_human.py "你想让数字人说的话"
```

配置在 `digital_human_config.ini`（音色模型、参考音频、源图片、驱动模板）。

流程：`GPT-SoVITS 生成语音 → LivePortrait 人脸驱动 → ffmpeg 合并`，支持视频循环补齐语音长度。

### 方案 B：edge-tts + SadTalker（4GB 显存优化）

```bash
python run_digital_human_sadtalker.py "你想让数字人说的话"
python run_digital_human_sadtalker.py --text "..." --image my_photo.jpg --voice zh-CN-YunxiNeural
```

流程：`edge-tts 语音合成 → SadTalker 口型驱动`，已内置 batch_size=1、256 分辨率、still 模式等显存优化。

## 框架二：AI 漫剧生产平台

### 总体架构（五段式流水线 + 配音引擎）

```
【GPT-SoVITS 配音引擎】（平台级，独立进程，端口 9880）
  文案 ──→ tts_to_lipsync.py ──→ role_voice.wav ──┐
                                                   │
① 角色立绘 ──→ ② 分镜画面 ──→ ③ 动画化 ──┐        │
                                          ├──→ ④ 口播唇形（SadTalker）──→ ⑤ 成片合成
                                          └────────────────────────────────┘
```

| # | Workflow 文件 | 环节 | 输出 |
|---|---------------|------|------|
| ① | `ComfyUI/workflow_manhua_character.json` | 角色立绘（文生图） | 角色设定图 PNG |
| ② | `ComfyUI/workflow_manhua_scene.json` | 分镜画面（姿态+角色一致） | 分镜图 PNG |
| ③ | `ComfyUI/workflow_manhua_animation.json` | 动画化（AnimateDiff+运镜） | 动画 MP4 |
| ④ | `ComfyUI/workflow_manhua_lipsync.json` | 口播唇形（SadTalker 音频驱动） | 口播视频 MP4 |
| ⑤ | `ComfyUI/workflow_manhua_final.json` | 成片合成 | 成片 MP4 |

### 配音引擎（tts_to_lipsync.py）

文案 → GPT-SoVITS 配音 → `ComfyUI/input/role_voice.wav` → SadTalker 口播

```bash
# CLI 模式（默认，一次性加载模型）
python tts_to_lipsync.py --text "你的台词文案"
# API 模式（模型常驻，适合批量配音）
python tts_to_lipsync.py --start-api
python tts_to_lipsync.py --text "你的台词文案" --mode api
# 内置角色音色（edge-tts，零素材即用）：--voice 旁白/男主/女主/反派/...
python tts_to_lipsync.py --text "你的台词" --voice 男主
```

音色：`Su`（基础）/ `Su_emotional`（情感版）为本地 GPT-SoVITS 微调音色；另有 11 个 edge-tts 内置角色。

### 批量口播（voice/ 目录）

- `voice/run_sadtalker.py`：通过 ComfyUI API 串行跑 lipsync workflow，输出 `voice/N.mp4`
- `voice/batch_sadtalker.py`：批量提交 + 轮询，从 SadTalker output 目录取最新 mp4
- `voice/concat_segments.py`：ffmpeg 拼接分页音频

### 工作流批量提交

```bash
python comfy_submit.py <workflow.json> [nodeid.field=value ...]
python manhua_work/run_batch.py <workflow1.json> <workflow2.json> ...
```

### 漫剧生产平台使用手册

详见 `ComfyUI/MANHUA_WORKFLOW_GUIDE.md`（五段流水线用法、素材约定、4GB 显存注意事项）与 `ComfyUI/SETUP_REPORT.md`（模型清单与实测记录）。

## 核心脚本一览

| 脚本 | 作用 |
|------|------|
| `run_digital_human.py` | 数字人流水线：GPT-SoVITS → LivePortrait → 合并 |
| `run_digital_human_sadtalker.py` | 数字人流水线：edge-tts → SadTalker 口播 |
| `tts_to_lipsync.py` | 漫剧配音引擎：文案 → role_voice.wav（CLI/API 双模式） |
| `generate_segmented_tts.py` | 分段生成语音并拼接，避免长文本漏字 |
| `comfy_submit.py` | ComfyUI workflow 提交与轮询（支持节点参数覆盖） |
| `platform_framework.py` | 生成平台架构图（matplotlib） |
| `download_models*.py` | 模型权重下载脚本（SadTalker/ComfyUI 等） |

## 目录结构

```
D:\digital_human
├── ComfyUI/            # 第三方运行时（不纳入版本控制，仅保留自定义 workflow 与文档）
│   ├── workflow_manhua_*.json   # 漫剧五段流水线工作流（已跟踪）
│   └── MANHUA_WORKFLOW_GUIDE.md # 平台使用手册（已跟踪）
├── GPT-SoVITS/         # 第三方克隆仓库：语音克隆 + 配音引擎（不纳入版本控制）
├── LivePortrait/       # 第三方克隆仓库：人脸驱动（不纳入版本控制）
├── SadTalker/          # 第三方源码：口型驱动（不纳入版本控制）
├── pylibs/             # 第三方源码：basicsr/gfpgan（不纳入版本控制）
├── manhua_work/        # 漫剧分镜/动画工作流模板与批量脚本
├── voice/              # 批量口播脚本与分页配音产物（媒体文件不纳入版本控制）
├── ref/                # 人脸参考素材
├── output/ outputs/    # 输出视频、训练产物（不纳入版本控制）
├── temp/               # 临时文件（不纳入版本控制）
├── run_digital_human.py
├── run_digital_human_sadtalker.py
├── tts_to_lipsync.py
├── digital_human_config.ini
└── README.md
```

## Git 仓库说明

本仓库只包含**自定义串联脚本、工作流与文档**。以下第三方开源项目均在 `.gitignore` 中排除，需按各自官方文档单独安装：

| 目录 | 用途 | 获取方式 |
|------|------|----------|
| `LivePortrait/` | 人脸驱动 | `git clone https://github.com/KwaiVGI/LivePortrait.git` |
| `GPT-SoVITS/` | 语音克隆/配音引擎 | `git clone https://github.com/RVC-Boss/GPT-SoVITS.git` |
| `SadTalker/` | 口型驱动 | `git clone https://github.com/OpenTalker/SadTalker.git` |
| `ComfyUI/` | 漫剧生产运行时 | `git clone https://github.com/comfyanonymous/ComfyUI.git` |
| `pylibs/` | gfpgan/basicsr 依赖源码 | 随 SadTalker/ComfyUI 环境安装 |

> 注意：仓库历史中曾误提交过 ComfyUI/SadTalker/pylibs 第三方源码，已在 2026-09 整理时移出跟踪（磁盘文件不受影响）。如需彻底从历史中移除以减小仓库体积，可另行执行 `git filter-repo` 重写历史。
