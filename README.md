# 🎵 Lyrics MV Pipeline - 歌词MV全自动流水线

> **AI选歌 → 查重 → 下载 → 生成 → 上传 → 互动 → 归档 → 更新网页**
>
> 把这个项目给 AI（Claude/GPT/Hermes等），AI 能帮你 **1:1 搭建全自动歌词MV生产线**。

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-4.0+-green.svg)](https://ffmpeg.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 这是什么？

一套 **全自动歌词版MV生产流水线**：

```
每天定时触发
     │
     ▼
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ 1.AI选歌  │──▶│ 2.查重    │──▶│ 3.下载素材 │──▶│ 4.生成视频 │
│ 热门+情感  │   │ 防重复    │   │ 音频+歌词  │   │ 打字机MV  │
└──────────┘   └──────────┘   └──────────┘   └──────────┘
                                                   │
     ┌──────────┐   ┌──────────┐   ┌──────────┐   │
     │ 7.更新网页│◀──│ 6.归档    │◀──│ 5.上传B站 │◀──┘
     │ 自动列表  │   │ 文件管理  │   │ 自动投稿  │
     └──────────┘   └──────────┘   └──────────┘
```

## ✨ 核心功能

| 模块 | 功能 | 脚本 |
|------|------|------|
| 🎯 **AI选歌** | 热门歌曲搜索、情感匹配、免费音源检测 | `select_song.py` |
| 🔍 **查重** | 防止重复投稿 | `check_duplicate.py` |
| ⬇️ **下载** | 网易云API：音频(FLAC) + 歌词(LRC) + 封面(JPG) | `download_assets.py` |
| 📝 **歌词处理** | 逐字同步、去标点、清理制作信息 | `clean_lyrics.py` |
| 🎬 **视频生成** | 打字机同步字幕 + 封面背景 + AI配色 | `generate_video.py` |
| 📤 **B站上传** | 自动投稿、标题简介生成 | `upload_bilibili.py` |
| 💬 **互动运营** | 双账号弹幕/评论/点赞 | `engage.py` |
| 📁 **归档** | 歌手/日期_歌名_BV号 标准结构 | `archive.py` |
| 🌐 **网页更新** | 自动生成作品集网页 | `sync_web.py` |

## 🚀 快速开始

### 给 AI 的方式（推荐）

把这个项目 clone 下来，然后对 AI 说：

> "请阅读 AGENTS.md，帮我搭建歌词MV全自动流水线"

AI 会根据 `AGENTS.md` 的完整指南，帮你：
1. 安装所有依赖
2. 配置你的凭证（B站Cookie、网易云Cookie等）
3. 设置定时任务
4. 一键启动

### 手动安装

```bash
git clone https://github.com/YOUR_USERNAME/lyrics-mv-pipeline.git
cd lyrics-mv-pipeline
bash setup.sh
cp .env.example .env
# 编辑 .env 填入你的凭证
python scripts/generate_video.py --help
```

## 📁 项目结构

```
lyrics-mv-pipeline/
├── AGENTS.md              # 🤖 AI操作指南（给AI看的完整文档）
├── README.md              # 本文件
├── setup.sh               # 一键安装脚本
├── .env.example           # 环境变量模板（不含真实凭证）
├── config.yaml            # 流水线配置
├── scripts/
│   ├── select_song.py     # AI选歌
│   ├── check_duplicate.py # 查重
│   ├── download_assets.py # 下载素材
│   ├── clean_lyrics.py    # 歌词清理
│   ├── generate_video.py  # 视频生成
│   ├── upload_bilibili.py # B站上传
│   ├── engage.py          # 互动运营
│   ├── archive.py         # 归档整理
│   └── sync_web.py        # 网页更新
├── web/
│   └── template.html      # 网页模板（Element UI风格）
├── docs/
│   ├── pipeline.md        # 流程详解
│   └── troubleshooting.md # 故障排除
└── lrc2video/             # 视频生成引擎（子模块）
```

## ⚙️ 配置

复制 `.env.example` 为 `.env`，填入你的信息：

```bash
# B站上传（从浏览器Cookie获取）
BILI_COOKIE_FILE=./cookies.json

# 网易云音乐（VIP账号可下载付费歌曲）
NETEASE_COOKIE=your_netease_cookie_here

# AI选歌（可选，使用OpenAI兼容接口）
LLM_API_BASE=https://api.openai.com/v1
LLM_API_KEY=sk-your-key-here
LLM_MODEL=gpt-4o-mini

# 视频生成
LRC2VIDEO_URL=http://localhost:7860

# 网站部署
WEB_DIR=/var/www/html
```

## 🎨 视频效果

- ✅ **打字机同步**：逐字显示，和演唱完全同步
- ✅ **AI智能配色**：根据歌词情感自动配色
- ✅ **封面背景**：专辑封面作视频背景
- ✅ **无渐入渐出**：干净利落
- ✅ **1080P高清**：1920x1080
- ✅ **320kbps音频**：高品质音质

## 📋 系统要求

- Python 3.8+
- FFmpeg 4.0+
- Linux / macOS / Windows

## 📄 License

MIT License

---

> 💡 **提示**：遇到问题？把报错信息发给 AI，让 AI 读 `docs/troubleshooting.md` 帮你排查。
