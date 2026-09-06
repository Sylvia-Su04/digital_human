# 漫剧工作流平台使用手册

> 适用：在 ComfyUI（http://127.0.0.1:8189）内一站式完成漫剧生产。
> 所有模型/节点已就位并完成三层校验（节点类型 / 参数 / 引用），可直接加载运行。

---

## 一、平台结构：5 段式生产流水线

```
① 角色立绘 ──→ ② 分镜画面 ──→ ③ 动画化 ──┐
                                          ├──→ ⑤ 成片合成（拼接+音频+导出）
④ 口播唇形（音频驱动） ───────────────────┘
```

| # | Workflow 文件 | 环节 | 输出 |
|---|---------------|------|------|
| ① | `workflow_manhua_character.json` | 角色立绘（文生图） | 角色设定图 PNG |
| ② | `workflow_manhua_scene.json` | 分镜画面（姿态+角色一致） | 分镜图 PNG |
| ③ | `workflow_manhua_animation.json` | 动画化（运镜） | 动画 WEBP |
| ④ | `workflow_manhua_lipsync.json` | 口播（图片+音频） | 口播视频 MP4 |
| ⑤ | `workflow_manhua_final.json` | 成片合成 | 成片 MP4 |

---

## 二、素材约定（ComfyUI/input 目录）

| 文件名 | 用途 | 来源 |
|--------|------|------|
| `pose_ref.png` | 分镜姿态参考图（人物姿势图/火柴人/真人照片均可） | ② 用，自己画或 AI 生成 |
| `char_ref.png` | 角色参考图（用于保持角色一致） | ② 用，取 ① 的输出 |
| `role_voice.wav` | 角色配音 | ④ 用，GPT-SoVITS 生成 |
| `manhua_scene.png` / `manhua_character.png` | ③④ 的输入图 | ①/② 的输出复制过来 |

> 所有输入图/音频先放到 `D:\digital_human\ComfyUI\input\`，ComfyUI 网页界面里才能选到。
> ③ 的输入图：把 ② 输出的分镜图复制到 input 目录并改名。
> ⑤ 的路径参数在网页界面里直接改。

---

## 三、每个 workflow 的用法

### ① 角色立绘（workflow_manhua_character.json）
- **作用**：生成漫画风角色设定图（无参考，文生图）
- **改哪里**：节点 2 的提示词（描述角色外貌/服装/姿势）
- **出图**：512×768 竖版 → `output/manhua_character_*.png`
- **建议**：多跑几张挑满意的一张作为全片"角色定妆照"

### ② 分镜画面（workflow_manhua_scene.json）
- **作用**：按姿态参考图生成分镜画面，同时用 IPAdapter 保持角色长相一致
- **素材**：`input/pose_ref.png`（姿态）+ `input/char_ref.png`（角色，用 ① 的输出）
- **改哪里**：节点 8 提示词（场景/动作/镜头描述）
- **出图**：512×768 → `output/manhua_scene_*.png`
- **技术细节**：DWPose 从 pose_ref 提取骨架 → ControlNet openpose 控制姿态；IPAdapter PLUS 锁定角色
- **每格一图**：一格分镜跑一次，把结果改名存入 input

### ③ 动画化（workflow_manhua_animation.json）
- **作用**：把分镜图变成 16 帧短动画，可加运镜
- **素材**：`input/manhua_scene.png`（用 ② 的输出改名）
- **改哪里**：节点 5 的运镜 LoRA（可换 ZoomOut/PanLeft/TiltUp 等 8 种）；节点 10 的 seed/denoise
- **出图**：`output/manhua_animation_*.webp`（16 帧，约 2 秒 @8fps）
- **注意**：denoise 0.7（图生视频保留构图）；动作幅度靠换 LoRA 或调 strength

### ④ 口播唇形（workflow_manhua_lipsync.json）
- **作用**：角色图片 + 配音音频 → 对口型说话视频
- **素材**：`input/manhua_character.png` + `input/role_voice.wav`（GPT-SoVITS 生成）
- **出图**：`output/*.mp4`
- **注意**：stillMode=true 时仅唇部动（适合分镜静止特写）；要全身动改 false

### ⑤ 成片合成（workflow_manhua_final.json）
- **作用**：把动画片段/口播片段拼接，配乐/配音合流，导出 MP4
- **改哪里**：节点 1/2 的视频路径（指向 output 里的实际片段）、节点 4 音频路径
- **出图**：`output/manhua_episode_*.mp4`
- **多段拼接**：需要拼更多片段时，复制一个"节点 1→合并"结构（VHS_MergeImages 可级联）

---

## 四、一集漫剧的推荐生产流程（示例）

1. **写剧本/分镜**：确定台词与分镜（每格画面+对应配音时长）
2. **① 生成角色**：设计 1-2 个主角定妆照，固定为 char_ref
3. **GPT-SoVITS 配音**：按台词生成每格的角色音频 → input/role_voice.wav
4. **② 逐格生成分镜**：每格画一个姿态参考（可用上一格改动作），跑 scene workflow
5. **③ 动画化**：重要的格（转场/特写）跑 animation workflow 加运镜
6. **④ 口播**：说话格跑 lipsync workflow
7. **⑤ 合成**：按顺序把所有片段填进 final workflow → 导出成片 MP4
8. （可选）**超分**：用 `workflow_upscale_test.json` 对关键画面做 4× 超分提升画质

---

## 五、注意事项（4GB 显存环境）

- **连续跑大任务后必须重启 ComfyUI**：连续跑 ①②③ 后显存碎片化，SadTalker 渲染速度会从 1.4it/s 暴跌到 0.04it/s（慢 35 倍），甚至进程崩溃。规律：每跑 2-3 个大任务重启一次。
- **④ 口播必须用正脸特写图**：全身图人脸占比太小，SadTalker 检测不到 landmark 会直接报错。口播环节单独生成一张 "close-up portrait, face closeup" 的角色图。
- **SadTalker 对日漫脸识别偏弱**：insightface 检测器为真人脸训练，纯日漫风格脸可能检测失败。半写实/写实风格角色图更稳；日漫脸可尝试加 "semi-realistic, realistic face" 提示词，或用 GFPGAN 增强后再喂入口播。
- **③ 动画输出必须用 mp4**：SaveAnimatedWEBP 输出的 webp 无法被 ⑤ 的 VHS_LoadVideoPath 加载（OpenCV 不支持 webp 动画解码）。动画 workflow 已固定用 VHS_VideoCombine 输出 h264-mp4。
- **VHS_LoadAudio 路径需加 input/ 前缀**：如 `input/role_voice.wav`，直接写文件名会报 "Invalid file path"。
- **AnimateDiff 16 帧**约需 3-4 分钟（512×768）；**SadTalker 口播**约 1 分钟（fresh restart 后）。
- ③ 的 batch（帧数）与分辨率不要同时拉大；512×768×16 帧是当前安全上限。
- ⑤ 超分整段视频在 4GB 显存下可能 OOM，建议只对关键帧单张超分。
- 启动脚本 `start_comfyui.bat` 已内置：PYTHONPATH（gfpgan/basicsr）、ffmpeg 路径、HF 镜像兜底。

---

## 六、资源清单速查

| 资源 | 位置 |
|------|------|
| ComfyUI 根目录 | `D:\digital_human\ComfyUI` |
| 启动脚本 | `D:\digital_human\ComfyUI\start_comfyui.bat` |
| 漫剧 5 段 workflow | `D:\digital_human\ComfyUI\workflow_manhua_*.json` |
| 输入素材目录 | `D:\digital_human\ComfyUI\input\` |
| 输出目录 | `D:\digital_human\ComfyUI\output\` |
| 节点代码 | `D:\digital_human\ComfyUI\custom_nodes\` |
| 模型 | `D:\digital_human\ComfyUI\models\`（另见 SETUP_REPORT.md） |
| GPT-SoVITS（配音） | `D:\digital_human\GPT-SoVITS`（独立项目） |
