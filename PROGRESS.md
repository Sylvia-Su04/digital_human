# 数字人项目进度记录

**记录时间**: 2026-08-30 22:00
**项目目录**: D:\digital_human

---

## 一、已完成的工作 ✅

### 1. GPT-SoVITS 语音克隆
- ✅ 基础模型训练完成（Su_e8_s296.pth）
- ✅ 情感增量训练完成（Su_emotional）
- ✅ 语音推理测试通过
- ✅ 修复了 jieba_fast、onnxruntime 等依赖问题

### 2. LivePortrait 人脸驱动
- ✅ 环境配置完成
- ✅ 人脸驱动测试通过
- ✅ 源图片：D:\digital_human\LivePortrait\ref\face.jpg
- ✅ 驱动模板：D:\digital_human\LivePortrait\ref\ceshi.pkl

### 3. 自动化流水线（三步版）
- ✅ 脚本：D:\digital_human\run_digital_human.py
- ✅ 配置：D:\digital_human\digital_human_config.ini
- ✅ 流程：输入文字 → 生成语音 → 生成人脸视频 → 合并
- ✅ 测试通过，输出视频在 D:\digital_human\output\

### 4. Wav2Lip 对口型（已清理，不需要）
- ❌ 已删除：Wav2Lip 代码目录、模型文件、依赖模型
- 释放空间：592.55 MB（0.58 GB）
- 原因：用户不需要对口型功能
- 当前流水线为三步：语音 → 人脸视频 → 合并

### 5. 其他
- ✅ 清理无用文件，释放 7.63 GB 空间
- ✅ 修复 onnxruntime 兼容性问题（D:\ort_fix）

---

## 二、正在进行的工作 🔄

### 1. S3FD 人脸检测模型下载
- **文件**: C:\Users\范籽粟\.cache\torch\hub\checkpoints\s3fd-619a316812.pth
- **总大小**: 85.68 MB
- **当前进度**: 44%（37.67 MB）
- **下载速度**: 约 31 KB/s
- **下载脚本**: D:\digital_human\download_s3fd.py（支持断点续传）
- **下载源**: https://www.adrianbulat.com/downloads/python-fan/s3fd-619a316812.pth

### 2. 自动化完成脚本
- **脚本**: D:\digital_human\auto_complete.py
- **功能**: 等待 S3FD 下载 → 测试四步流水线 → 播放音乐
- **状态**: 后台运行中

---

## 三、待完成的工作 ⬜

1. ⬜ S3FD 人脸检测模型下载完成
2. ⬜ 测试完整四步流水线（语音 → 人脸视频 → 对口型 → 合并）
3. ⬜ 验证对口型效果（嘴型是否和声音同步）
4. ⬜ 优化参数（如果对口型效果不好）
5. ⬜ 最终交付：一个完整的、嘴型同步的数字人视频

---

## 四、遇到的问题及解决方案

### 问题1：Wav2Lip 第一次运行卡住
- **原因**: face-alignment 库需要下载 S3FD 人脸检测模型（85 MB），网络慢导致卡住
- **现象**: 进程运行 30 分钟，CPU 时间只有 6 秒，内存 13 MB
- **解决方案**: 手动下载 S3FD 模型，放到 torch 缓存目录（正在下载中）

### 问题2：外部网站访问不稳定
- **现象**: huggingface.co、adrianbulat.com 等国外网站连接超时或速度慢
- **解决方案**: 
  - Wav2Lip 主模型用 hf-mirror.com 国内镜像下载成功
  - S3FD 模型用断点续传慢慢下载（进行中）

### 问题3：LivePortrait 驱动视频文件丢失
- **原因**: ceshi.mp4 文件被清理了
- **解决方案**: 改用 ceshi.pkl 模板文件（已更新配置）

---

## 五、关键文件路径

| 项目 | 路径 |
|------|------|
| 项目根目录 | D:\digital_human |
| 自动化脚本 | D:\digital_human\run_digital_human.py |
| 配置文件 | D:\digital_human\digital_human_config.ini |
| 自动完成脚本 | D:\digital_human\auto_complete.py |
| S3FD 下载脚本 | D:\digital_human\download_s3fd.py |
| Wav2Lip 目录 | D:\digital_human\Wav2Lip |
| Wav2Lip 主模型 | D:\digital_human\Wav2Lip\checkpoints\wav2lip_gan.pth |
| S3FD 模型（下载中） | C:\Users\范籽粟\.cache\torch\hub\checkpoints\s3fd-619a316812.pth |
| GPT-SoVITS 目录 | D:\digital_human\GPT-SoVITS |
| LivePortrait 目录 | D:\digital_human\LivePortrait |
| 源图片 | D:\digital_human\LivePortrait\ref\face.jpg |
| 驱动模板 | D:\digital_human\LivePortrait\ref\ceshi.pkl |
| 输出目录 | D:\digital_human\output |
| 临时目录 | D:\digital_human\temp |
| onnxruntime 修复 | D:\ort_fix |
| Conda 环境 | D:\conda_envs\digital_human |

---

## 六、四步流水线说明

```
输入文字
    ↓
第一步：GPT-SoVITS 生成语音
    输出：temp/{run_id}_tts/output.wav
    ↓
第二步：LivePortrait 生成人脸视频
    输出：temp/{run_id}_liveportrait/face--ceshi.mp4
    ↓
第三步：Wav2Lip 对口型（新增！）
    输出：temp/{run_id}_lipsync.mp4
    ↓
第四步：合并语音和视频
    输出：output/digital_human_{run_id}.mp4
```

---

## 七、明天继续的步骤

### 第一步：检查 S3FD 下载状态
```powershell
# 检查文件大小
$modelPath = "$env:USERPROFILE\.cache\torch\hub\checkpoints\s3fd-619a316812.pth"
if (Test-Path $modelPath) {
    $size = (Get-Item $modelPath).Length
    Write-Output "当前大小: $([math]::Round($size/1MB,2)) MB / 85.68 MB"
}
```

### 第二步：如果没下载完，继续下载
```powershell
cd D:\digital_human
python download_s3fd.py
```

### 第三步：如果下载完了，测试四步流水线
```powershell
cd D:\digital_human
$env:PYTHONPATH = "D:\ort_fix"
python run_digital_human.py "测试文字"
```

### 第四步：检查输出视频
- 输出目录：D:\digital_human\output\
- 播放最新的 mp4 文件，检查嘴型是否和声音同步

### 第五步：如果效果不好，调整参数
- 检查 Wav2Lip 推理脚本参数
- 检查 LivePortrait 参数
- 检查语音质量

---

## 八、注意事项

1. **S3FD 模型必须下载完成**，否则 Wav2Lip 会卡住
2. **运行流水线前必须设置环境变量**：`$env:PYTHONPATH = "D:\ort_fix"`
3. **驱动视频用 ceshi.pkl**，不是 ceshi.mp4（已更新配置）
4. **Wav2Lip 对口型比较耗时**，12 秒视频约需 5~10 分钟
5. **如果 Wav2Lip 卡住**，检查 S3FD 模型是否下载完成，检查 face-alignment 是否能正常加载

---

**记录完成时间**: 2026-08-30 22:05
**下次继续时**: 先看本文件，了解当前进度，然后按"明天继续的步骤"操作
