# -*- coding: utf-8 -*-
"""
AI 漫剧生产平台 - 框架架构图（PPT 用）v3
输出: D:\digital_human\平台框架图.png (2880x1620)
布局：标题 → 应用领域 → 输入层 → [折线主链路 | 配音链路] → 五段流水线 → 基础设施
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from matplotlib import font_manager

# ---------- 中文字体 ----------
font_path = r"C:\Windows\Fonts\msyh.ttc"
font_manager.fontManager.addfont(font_path)
zh = font_manager.FontProperties(fname=font_path)
plt.rcParams["font.family"] = zh.get_name()

# ---------- 画布 ----------
W, H = 1920, 1080
fig, ax = plt.subplots(figsize=(W/100, H/100), dpi=150)
fig.patch.set_facecolor("#F4F6FA")
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")

# ---------- 颜色 ----------
C_TITLE   = "#1F2937"
C_SUB     = "#6B7280"
C_BLUE    = "#2B6CB0"
C_BLUE_D  = "#1E4E8C"
C_BORDER  = "#CBD5E1"
C_TEXT    = "#374151"
C_WHITE   = "#FFFFFF"
C_DARKBAR = "#1E3A5F"
C_GREEN   = "#0E9F6E"
C_ORANGE  = "#C05621"
C_GRAY    = "#64748B"

def box(x, y, w, h, fc, ec, lw=1.5, rad=14, zorder=2):
    p = FancyBboxPatch((x, y), w, h,
                       boxstyle=f"round,pad=0,rounding_size={rad}",
                       fc=fc, ec=ec, lw=lw, zorder=zorder)
    ax.add_patch(p)
    return p

def txt(x, y, s, size, color, weight="normal", ha="center", va="center", zorder=5):
    ax.text(x, y, s, fontsize=size, color=color, ha=ha, va=va,
            fontweight=weight, zorder=zorder, linespacing=1.5)

def arrow(x1, y1, x2, y2, color=C_BLUE, lw=3, style="-|>", ls="-"):
    a = FancyArrowPatch((x1, y1), (x2, y2),
                        arrowstyle=style, mutation_scale=28,
                        lw=lw, color=color, linestyle=ls, zorder=4)
    ax.add_patch(a)

def line(x1, y1, x2, y2, color=C_GRAY, lw=2.5, ls="-"):
    ax.plot([x1, x2], [y1, y2], color=color, lw=lw, linestyle=ls, zorder=4)

# ================= 标题 =================
txt(W/2, 1052, "AI 漫剧生产平台 · 整体架构", 46, C_TITLE, "bold")
txt(W/2, 1012, "从文案到成片的五段式自动化流水线（ComfyUI 驱动）", 20, C_SUB)

# ================= 应用领域 =================
apps = [
    ("AI 漫剧 / 短剧生产", "分镜 → 成片全流程", "#E0F2FE", "#1E4E8C"),
    ("数字人口播", "课程讲解 · 新闻播报 · 带货口播", "#DCFCE7", "#065F46"),
    ("角色一致性动画", "同角色跨场景、跨镜头样貌统一", "#FCE7F3", "#6B21A8"),
]
ay, app_h = 895, 75
app_w, gap = 570, 40
app_x0 = (W - (app_w*3 + gap*2)) / 2
for i, (t, s, bgc, tc) in enumerate(apps):
    ax0 = app_x0 + i * (app_w + gap)
    box(ax0, ay, app_w, app_h, bgc, "none", lw=0, rad=16)
    txt(ax0 + app_w/2, ay + app_h*0.63, t, 20, tc, "bold")
    txt(ax0 + app_w/2, ay + app_h*0.26, s, 13.5, C_TEXT)

# ================= 输入层 =================
in_y, in_h = 780, 85
in_w = 300
in_xs = [470, 810, 1150]
in_labels = ["剧本文案", "角色设定", "参考音频 / 音色"]
in_subs   = ["台词 / 分集脚本", "外观 / 服装 / 表情", "目标音色（GPT-SoVITS）"]
for i, (ix, lab, sub) in enumerate(zip(in_xs, in_labels, in_subs)):
    box(ix, in_y, in_w, in_h, C_WHITE, "#93C5FD", lw=2, rad=16)
    txt(ix + in_w/2, in_y + in_h*0.62, lab, 22, C_BLUE_D, "bold")
    txt(ix + in_w/2, in_y + in_h*0.26, sub, 14, C_SUB)

# ================= 五段流水线 =================
py, ph = 210, 380
pw = 300
pxs = [40, 425, 810, 1195, 1580]
steps = [
    ("①", "角色立绘", C_BLUE,
     ["日漫底模 Counterfeit-V2.5", "SD1.5 生态 · 4GB 显存优化", "动漫风格 · 高质量立绘", "输出：角色定妆照"]),
    ("②", "分镜画面", C_BLUE,
     ["DWPose 姿态检测", "ControlNet OpenPose 构图", "IPAdapter 角色一致性", "输出：分镜画面"]),
    ("③", "动画化", C_BLUE,
     ["AnimateDiff 运动模块", "8 种运镜 LoRA", "VideoHelperSuite 视频链", "输出：动态片段"]),
    ("④", "口播唇形", C_GREEN,
     ["SadTalker 唇形对齐", "GPT-SoVITS 配音引擎", "音频驱动 · 正脸特写", "输出：口播视频"]),
    ("⑤", "成片合成", C_ORANGE,
     ["视频拼接 · 音画合流", "字幕压制 · 转码", "导出 MP4 成片", "输出：完整漫剧"]),
]
for i, (num, name, color, lines) in enumerate(steps):
    x = pxs[i]
    box(x, py, pw, ph, C_WHITE, C_BORDER, lw=1.5, rad=18)
    head_h = 74
    hp = FancyBboxPatch((x, py+ph-head_h), pw, head_h,
                        boxstyle=f"round,pad=0,rounding_size=18",
                        fc=color, ec=color, zorder=3)
    ax.add_patch(hp)
    ax.add_patch(Rectangle((x, py+ph-head_h), pw, 22, fc=color, ec=color, zorder=3))
    txt(x + pw/2, py + ph - head_h/2, f"{num}  {name}", 26, C_WHITE, "bold")
    yy = py + ph - head_h - 30
    for ln in lines:
        txt(x + pw/2, yy, ln, 15.5, C_TEXT)
        yy -= 31
    if i < 4:
        arrow(x + pw + 4, py + ph/2, x + pw + 81, py + ph/2, color="#2B6CB0", lw=3.5)

# ================= 主链路：输入 → 流水线（折线，不斜穿） =================
mid_x = 960          # 输入层底边中点
feed_y = 635         # 汇流水平线高度
line(mid_x, in_y - 4, mid_x, feed_y, color=C_GRAY, lw=2.5)          # 垂直向下
line(mid_x, feed_y, 175, feed_y, color=C_GRAY, lw=2.5)              # 水平向左
arrow(175, feed_y, 175, py + ph + 4, color=C_GRAY, lw=2.5)          # 落入①顶部
txt(530, feed_y + 14, "素材输入", 15, C_GRAY)

# ================= 配音链路（右侧垂直虚线） =================
vx, vy, vw, vh = 1180, 655, 320, 80
box(vx, vy, vw, vh, "#F0FDF4", C_GREEN, lw=2, rad=14)
txt(vx + vw/2, vy + vh*0.62, "GPT-SoVITS 配音引擎", 18, "#065F46", "bold")
txt(vx + vw/2, vy + vh*0.26, "剧本文案 → Su 音色 → 配音 wav", 13, "#065F46")
# 剧本文案(1150-1450) → 配音条
arrow(1345, in_y - 4, 1345, vy + vh + 4, color=C_GREEN, lw=2, ls="--")
# 配音条 → ④口播顶部
arrow(1345, vy - 4, 1345, py + ph + 4, color=C_GREEN, lw=2, ls="--")

# ================= 基础设施层 =================
by, bh = 36, 72
box(40, by, 1840, bh, C_DARKBAR, C_DARKBAR, rad=16)
seg = [
    ("ComfyUI 运行时", ["v0.34 · 端口 8189", "15 个可复现工作流"]),
    ("模型体系 18.3GB", ["SD1.5 · Counterfeit · ControlNet×4", "AnimateDiff · LivePortrait · SadTalker"]),
    ("推理硬件", ["RTX 3050 Ti Laptop", "4GB 显存 · CUDA"]),
]
seg_w = 1840 / 3
for i, (t, ss) in enumerate(seg):
    cx = 40 + seg_w * i + seg_w / 2
    txt(cx, by + bh*0.63, t, 20, C_WHITE, "bold")
    txt(cx, by + bh*0.25, ss[0], 12, "#C7D6EA")
    txt(cx, by + bh*0.06, ss[1], 12, "#C7D6EA")

# ================= 保存 =================
plt.savefig(r"D:\digital_human\平台框架图.png", dpi=150, bbox_inches=None,
            facecolor="#F4F6FA", pad_inches=0)
print("saved: D:\\digital_human\\平台框架图.png")
