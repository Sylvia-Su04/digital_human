# ComfyUI 漫剧工作流框架清单（2026-09-05 更新）

> 目标：为「下周搭建漫剧生成工作流」准备尽可能完整的本地模型与节点环境。
> 本文件记录全部已就位资产、验证结果与使用方式。

---

## 一、环境总览

| 项目 | 详情 |
|------|------|
| ComfyUI 根目录 | `D:\digital_human\ComfyUI` |
| 服务地址 | http://127.0.0.1:8189 |
| 启动脚本 | `D:\digital_human\ComfyUI\start_comfyui.bat`（双击启动） |
| Python | `D:\digital_human\venv`（Python 3.10.21，PyTorch 2.5.1+cu118） |
| GPU | RTX 3050 Ti Laptop，**4GB 显存** |
| 权限 | D 盘可写（用户已设置完全控制）；C 盘已无 ComfyUI 相关内容 |

### 启动必须携带的环境
- `PYTHONPATH`：`D:\digital_human\pylibs\basicsr_src;D:\digital_human\pylibs\gfpgan_src`
- `PATH` 前缀：`D:\digital_human\venv\Lib\site-packages\imageio_ffmpeg\binaries`

---

## 二、已就位节点（全部加载成功）

| 节点 | 版本/来源 | 用途 | 状态 |
|------|-----------|------|------|
| **SadTalker** | Comfyui-SadTalker | 音频驱动口播/唇形对齐 | ✅ 已跑通 |
| **LivePortraitKJ** | ComfyUI-LivePortraitKJ | 面部表情驱动 | ✅ 加载正常 |
| **VideoHelperSuite** | ComfyUI-VideoHelperSuite | 视频处理工具 | ✅ 加载正常 |
| **IPAdapter_plus** | ComfyUI_IPAdapter_plus | 角色一致性 | ✅ 已实测 |
| **AnimateDiff-Evolved** | ComfyUI-AnimateDiff-Evolved | 图生视频/动画（含运镜） | ✅ 已实测 |
| **ControlNet Aux 预处理器** | comfyui_controlnet_aux | DWPose姿态/DepthAnything深度/Tile/动漫线稿/AIO 全套 | ✅ 加载成功 |

---

## 三、已就位模型（全部实测/识别通过）

| 模型 | 路径 | 体积 | 用途 | 验证 |
|------|------|------|------|------|
| SD1.5 底模 v1-5 | `models\checkpoints\v1-5-pruned-emaonly.safetensors` | 4.07 GB | 基础文生图 | ✅ 512×512 测试 |
| **Counterfeit-V2.5 日漫底模** | `models\checkpoints\Counterfeit-V2.5_fp16.safetensors` | 2.03 GB | 漫剧日漫画风 | ✅ 生成测试 |
| ControlNet canny | `models\controlnet\control_v11p_sd15_canny.pth` | 1.38 GB | 线稿构图控制 | ✅ canny 测试 |
| ControlNet openpose | `models\controlnet\control_v11p_sd15_openpose.pth` | 1.38 GB | 人物姿态控制 | ✅ 已识别 |
| ControlNet depth | `models\controlnet\control_v11f1p_sd15_depth.pth` | 1.38 GB | 场景深度控制 | ✅ 已识别 |
| **ControlNet tile** | `models\controlnet\control_v11f1e_sd15_tile.pth` | 1.38 GB | 线稿重绘细节保持 | ✅ 已识别 |
| IPAdapter Plus | `models\ipadapter\ip-adapter-plus_sd15.safetensors` | 93.6 MB | 角色一致性 | ✅ IPAdapter 测试 |
| CLIP-ViT-H-14 | `models\clip_vision\CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors` | 2.41 GB | IPAdapter 图像编码 | ✅ 已识别 |
| **AnimateDiff v2 运动模块** | `models\animatediff_models\mm_sd_v15_v2.ckpt` | 1.73 GB | 图生视频/动画 | ✅ 16 帧动画测试 |
| **AnimateDiff 运镜 LoRA × 8** | `models\animatediff_motion_lora\`（ZoomIn/Out、PanLeft/Right、TiltUp/Down、Rolling 双向） | 0.59 GB | 动画推拉/平移/倾斜运镜 | ✅ ZoomIn 实测 |
| **RealESRGAN x4plus** | `models\upscale_models\RealESRGAN_x4plus.safetensors` | 63.8 MB | 图片/视频超分 4× | ✅ 512→2048px 实测 |
| **优化 VAE** | `models\vae\vae-ft-mse-840000-ema-pruned.safetensors` | 319 MB | 替代自带 VAE，色彩更佳 | ✅ 已识别 |
| **GPT-SoVITS（配音引擎，含 Su/Su_emotional 音色）** | `D:\digital_human\GPT-SoVITS`（GPT_weights_v2Pro + SoVITS_weights_v2Pro） | ~200 MB | 文案→人声 wav，平台配音引擎，API 端口 9880 | ✅ 微调完成 |

**累计模型体积：约 18.6 GB（含 GPT-SoVITS）**

### 预处理器检测模型（comfyui_controlnet_aux/ckpts）

| 文件 | 体积 | 用途 |
|------|------|------|
| yolox_l.onnx | 206.7 MB | DWPose 人体检测 |
| dw-ll_ucoco_384.onnx | 128.2 MB | DWPose 姿态估计 |
| depth-anything-base-hf（HF 缓存） | 371.9 MB | DepthAnything 深度估计（vitb14） |

> transformers/timm 已装入 D:\digital_human\venv；HF 模型缓存位于 C:\Users\范籽粟\.cache\huggingface（已预下载完成）

---

## 四、实测结果

| 测试 | 输出 | 状态 |
|------|------|------|
| SD1.5 基线文生图 | `output\controlnet_sd15_test_00001_.png` | ✅ |
| ControlNet canny | `output\controlnet_canny_test_00001_.png` | ✅ 构图遵循参考图 |
| IPAdapter 角色一致 | `output\ipadapter_test_00001_.png` | ✅ 保持参考角色风格 |
| Counterfeit 日漫画风 | `output\counterfeit_test_00001_.png` | ✅ 日漫风 |
| AnimateDiff 图生视频 | `output\animatediff_test_00001_.webp/gif` | ✅ 16 帧动画，80 秒生成 |
| **AnimateDiff + ZoomIn 运镜** | `output\animatediff_zoomin_test_00001_.webp/gif` | ✅ 16 帧推近镜头，79 秒 |
| **RealESRGAN 超分** | `output\realesrgan_test_00001_.png` | ✅ 512→2048px 清晰放大 |
| SadTalker 音频口播 | `output\20260904214509.mp4` | ✅ 图片+音频→对口型视频 |
| GPT-SoVITS 配音（Su 音色） | `ComfyUI\input\role_voice.wav` | ✅ 文案→人声 wav（API 模式） |

---

## 五、可复现 Workflow（都在 ComfyUI 根目录）

| 文件 | 用途 |
|------|------|
| `workflow_sadtalker_api.json` | 音频驱动口播（图片+音频→视频） |
| `workflow_sd15_baseline.json` | 基线文生图 |
| `workflow_controlnet_canny_test.json` | ControlNet canny 测试 |
| `workflow_ipadapter_test.json` | IPAdapter 角色一致性测试 |
| `workflow_animatediff_test.json` | AnimateDiff 图生视频 |
| `workflow_animatediff_zoomin.json` | AnimateDiff + 运镜 LoRA（ZoomIn） |
| `workflow_upscale_test.json` | RealESRGAN 超分 |
| `workflow_manhua_character.json` | **角色立绘生成**（漫剧生产模板） |
| `workflow_manhua_scene.json` | **分镜画面生成**（DWPose 姿态 + IPAdapter 角色一致） |
| `workflow_manhua_animation.json` | **分镜动画化**（AnimateDiff + 运镜 LoRA） |
| `workflow_manhua_lipsync.json` | **口播唇形**（SadTalker 音频驱动） |
| `workflow_manhua_final.json` | **成片合成**（多段拼接 + 音频 + MP4 导出） |

> 漫剧 5 段式生产 workflow 使用说明见 `MANHUA_WORKFLOW_GUIDE.md`

---

## 六、关键修复记录（勿覆盖回退）

1. **librosa 延迟导入** — `SadTalker\src\utils\audio.py` 函数内 import，否则 ComfyUI 启动挂死
2. **gfpgan/basicsr 源码** — `D:\digital_human\pylibs\`，PYTHONPATH 引入（venv 只读无法 pip）
3. **gfpgan 包装器** — ComfyUI 根 `gfpgan\__init__.py` 重新导出真实包
4. **Unicode 路径 cv2 补丁** — `cv2.imread/imwrite` → `imdecode(np.fromfile())` / `imencode().tofile()`
5. **ffmpeg 完整路径** — `videoio.py` 用 `imageio_ffmpeg.get_ffmpeg_exe()` + subprocess
6. **启动恢复 `__import__`** — 兼容 torch 2.5.1
7. **ShowText 空值检查** — 防止 SadTalker 返回 STRING 崩溃
8. **motion LoRA 目录名** — 必须放 `models\animatediff_motion_lora\`（不是 motion_lora）

---

## 七、漫剧工作流建议路线（下周可落地）

```
剧本/分镜文案
    ↓
GPT-SoVITS 配音引擎（tts_to_lipsync.py，Su/Su_emotional 音色）→ role_voice.wav
    ↓
SD1.5/Counterfeit 底模 + ControlNet(openpose/depth/canny/tile) → 分镜画面
    ↓
IPAdapter Plus → 角色一致性保持
    ↓
AnimateDiff + 运镜 LoRA → 分镜动态化（图生视频，可加推拉/平移镜头）
    ↓
SadTalker → 口播唇形对齐（音频驱动）
    ↓
RealESRGAN → 画面超分提升画质
    ↓
VideoHelperSuite → 合流/拼接/导出
```

---

## 八、后续可选项（需评估后再装）

| 项目 | 说明 | 预估体积 |
|------|------|----------|
| 漫画风格 LoRA | civitai 需登录，可浏览器手动下载 | 288 MB |
| Wan2.1/LTX 图生视频 | 新一代视频模型，**最低 8GB 显存**，4GB 跑不动 | 10+ GB |
| RealESRGAN anime 版 | 动漫专用超分变体 | ~70 MB |

> 4GB 显存提示：AnimateDiff 是本地图生视频的最优解；追求大动态效果建议用云平台（即梦/可灵）做动态部分，ComfyUI 负责画面生成 + 口播精修。
