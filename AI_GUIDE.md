# 🤖 AI_GUIDE.md - AI 操作指南

> **给 AI 的完整说明**：如果你是 AI（Claude/GPT/Hermes/其他），请完整阅读本文档。
> 按照步骤操作，可以为用户搭建一套 **歌词MV全自动生产流水线**。

---

## 📌 项目目标

搭建一套自动化流水线，每天定时完成：

```
AI选歌 → 查重 → 下载素材 → 生成打字机MV → 上传B站 → 双账号互动 → 归档 → 更新网页
```

最终效果：用户只需配置一次，之后每天自动产出 1-2 期歌词版MV 并发布到B站。

---

## 🔧 第一步：环境准备

### 1.1 安装系统依赖

```bash
# FFmpeg（必须）
sudo apt install ffmpeg    # Ubuntu/Debian
brew install ffmpeg        # macOS

# Python 3.8+（必须）
python3 --version
```

### 1.2 创建项目目录

```bash
mkdir -p ~/lyrics-mv-work && cd ~/lyrics-mv-work
git clone <this-repo> .
bash setup.sh
```

`setup.sh` 会自动：
- 创建 Python 虚拟环境
- 安装所有依赖（Pillow, gradio, pysubs2, requests 等）
- 下载开源中文字体（Noto Sans SC）
- 创建必要目录结构

### 1.3 配置凭证

**⚠️ 安全警告：永远不要把真实凭证写进代码或提交到 Git！**

复制配置模板：
```bash
cp .env.example .env
```

需要配置的凭证：

| 凭证 | 获取方式 | 用途 |
|------|----------|------|
| **B站 Cookie** | 浏览器 F12 → Network → 任意请求 → Request Headers → Cookie | 上传视频 |
| **网易云 Cookie** | 浏览器登录 music.163.com → F12 → Application → Cookies | 下载VIP歌曲（可选） |
| **LLM API Key** | OpenAI / 其他兼容接口 | AI选歌 + AI配色（可选） |

---

## 📝 第二步：理解流水线

### 2.1 完整流程

```
每天定时触发
     │
     ▼
Step 1: AI选歌 (scripts/select_song.py)
  → 搜索热门歌曲、情感匹配、检测免费音源
  → 输出: 歌曲名 + 歌手名 + 网易云song_id
     │
     ▼
Step 2: 查重 (scripts/check_duplicate.py)
  → biliup list | grep 歌名
  → ⚠️ 必须单次抓取存文件再grep，避免间歇空输出
     │
     ▼
Step 3: 下载素材 (scripts/download_assets.py)
  → 音频(FLAC) + 歌词(LRC) + 封面(JPG)
  → ⚠️ 封面字段是picUrl不是pic
  → ⚠️ fee=1(VIP)需要网易云Cookie
     │
     ▼
Step 4: 歌词清理 (scripts/clean_lyrics.py)
  → 去制作信息/去标点/去空格/逐字同步
  → 保留: [^一-龥぀-ヿ가-힯々〆]
     │
     ▼
Step 5: 生成视频 (scripts/generate_video.py)
  → Lrc2Video Gradio API (端口7860)
  → 打字机同步 + 封面背景 + AI配色
  → ⚠️ ASS颜色: &H00BBGGRR& (BGR顺序)
  → ⚠️ fad(0,0) 无渐入渐出
  → ⚠️ 并发时记录outputs旧文件集
     │
     ▼
Step 6: 上传B站 (scripts/upload_bilibili.py)
  → biliup upload
  → 标题: 歌名 - 歌手｜原创引言
  → 简介: 一句原创引言（纯文字无emoji）
     │
     ▼
Step 7: 互动运营 (scripts/engage.py)
  → 小号: 弹幕/评论/点赞
  → 主号: 弹幕引导/评论引导
  → ⚠️ 投币前先 bili video watch
  → ⚠️ 限频: 弹幕10秒/评论10秒/动态60秒
     │
     ▼
Step 8: 归档 (scripts/archive.py)
  → archive/歌手/日期_歌名_BV号/
     │
     ▼
Step 9: 更新网页 (scripts/sync_web.py)
  → Element UI风格歌曲列表
```

---

## 🛠️ 第三步：逐个部署脚本

### 3.1 select_song.py - AI选歌

```bash
python scripts/select_song.py --genre pop --mood emotional --limit 5
```

**AI需要做的：**
1. 根据 config.yaml 中的歌手池和风格偏好，推荐候选歌曲
2. 对每首歌调用网易云搜索API确认真实存在
3. 检测免费音源可用性（fee=0 或 fee=8）
4. 输出排序后的推荐列表

**选歌规则：**
- 歌曲必须真实存在（搜索API确认）
- 传唱度高、有情感共鸣
- 区分歌曲和诗词/口号
- 核实歌手和专辑信息

### 3.2 check_duplicate.py - 查重

```bash
python scripts/check_duplicate.py "歌名"
```

**⚠️ 关键教训（必须遵守）：**
- biliup list 在循环中反复调用会间歇性输出空结果 → 假阴性
- **必须单次抓取存到文件，再用 grep 搜索文件**
- 发现重复 → 换一首歌，绝不重复投稿

### 3.3 download_assets.py - 下载素材

```bash
python scripts/download_assets.py <song_id> <work_dir>
```

**下载流程：**
1. `GET /api/song/detail?ids=[id]` → 获取详情 + album.picUrl
2. `GET picUrl?param=1000y1000` → 下载封面
3. `GET /api/song/enhance/player/url?ids=[id]&br=320000` → 获取音频URL
4. 下载MP3 → ffmpeg转FLAC
5. `GET /api/song/lyric?id=id&lv=1&kv=1&tv=-1` → 获取歌词

**⚠️ 注意事项：**
- 封面字段是 picUrl 不是 pic
- fee=1（VIP）歌曲需要网易云Cookie
- code=-110 表示VIP限制
- nextmusic API已失效，用官方API

### 3.4 clean_lyrics.py - 歌词清理

```bash
python scripts/clean_lyrics.py <work_dir>
```

**清理规则：**
- 去掉：作词/作曲/编曲/制作人 等制作信息
- 去掉：标点符号、空格
- 保留：中文、日文、韩文、数字
- 正则：`[^一-龥぀-ヿ가-힯々〆]` → 保留匹配的字符

### 3.5 generate_video.py - 生成视频

```bash
python scripts/generate_video.py <work_dir> [font_color] [outline_color] [outline_width] [bg_color] [font_size]
```

**Lrc2Video API调用：**
```
POST http://localhost:7860/gradio_api/call/generate
参数顺序: [audio, lrc, cover, font_family, font_file, font_size,
          font_color, outline_color, outline_width, bold,
          pos_x, pos_y, margin_h, margin_v,
          fade_in, fade_out, bg_color, resolution]
```

**⚠️ 关键技术点：**
- ASS颜色格式：`&H00BBGGRR&`（BGR顺序！不是RGB）
- 渐变：`fad(0,0)` 无渐入渐出
- 打字机：`mode="sync"` 按歌词时长均匀分布
- **并发生成时**：记录 outputs 旧文件集，用 ffprobe + 文件大小双稳判断完成

### 3.6 upload_bilibili.py - 上传B站

```bash
python scripts/upload_bilibili.py <video> --title "..." --desc "..." --tag "..." --cover ...
```

**标题格式：** `歌名 - 歌手｜原创引言文案`
**简介格式：** 一句原创引言（纯文字）

**引言风格对应：**
| 歌曲风格 | 引言风格 | 示例 |
|----------|----------|------|
| 伤感情歌 | 深夜emo | "最怕深夜听懂这首歌" |
| 温暖治愈 | 温暖释怀 | "走累了就回家" |
| 怀旧经典 | 扎心现实 | "有些人一走就是一生" |
| 热门流行 | 热门话题 | "全网都在单曲循环" |

**⚠️ 标题不要加【歌词版MV】**

### 3.7 engage.py - 互动运营

```bash
python scripts/engage.py <BV号>
```

**⚠️ 风控规则：**
- 弹幕限频 10秒/次
- 评论限频 10秒/次
- 动态限频 60秒/次
- **投币前必须先 `bili video watch <BV>`**，否则 -401
- 小号互动每天 5-10 次，避免风控

### 3.8 archive.py - 归档

```bash
python scripts/archive.py <work_dir> <BV号> <歌手> <歌名>
```

**归档结构：**
```
archive/
└── 歌手名/
    └── YYYY-MM-DD_歌名_BV号/
        ├── 音频.flac
        ├── 歌词.lrc
        ├── 封面.jpg
        ├── 视频.mp4
        └── info.json
```

### 3.9 sync_web.py - 更新网页

```bash
python scripts/sync_web.py
```

生成 Element UI 风格的歌曲列表网页，**数据以B站为准**。

---

## ⏰ 第四步：设置定时任务

### 方式一：Crontab

```bash
# 每天 10:00 和 18:00 各出一期
0 10 * * * cd /path/to/lyrics-mv-pipeline && ./run_pipeline.sh
0 18 * * * cd /path/to/lyrics-mv-pipeline && ./run_pipeline.sh
```

### 方式二：AI Agent Cron

如果使用 Hermes Agent 等 AI 调度器，创建 cron job：
```
schedule: "0 10 * * *" 和 "0 18 * * *"
prompt: 按照 AI_GUIDE.md 执行完整流水线
```

---

## ⚠️ 第五步：避坑指南

### 绝对不能做的事

| ❌ 错误 | ✅ 正确 |
|---------|---------|
| 同一首歌做多次 | 制作前必须查重 |
| 用其他歌的封面 | 每首歌用各自专辑封面 |
| 视频背景和封面不匹配 | 背景必须用同一张封面 |
| 标题加【歌词版MV】 | 标题：歌名 - 歌手｜引言 |
| 简介加emoji/歌词 | 简介一句原创引言 |
| 循环调用 biliup list 查重 | 单次抓取存文件再grep |
| 并发生成时直接取最新文件 | 记录旧文件集，只取新生成的 |
| 把凭证写进代码 | 用 .env 文件 |

### 常见错误和修复

| 错误 | 原因 | 修复 |
|------|------|------|
| `code=-110` | VIP歌曲无Cookie | 配置网易云Cookie |
| `封面下载失败` | 字段名错误 | 用 picUrl 不是 pic |
| `歌词乱码` | YRC JSON格式 | 用逐行解析 |
| `颜色不生效` | ASS格式错误 | 必须 `&H00BBGGRR&` (BGR) |
| `打字机不同步` | 模式错误 | 用 `mode="sync"` |
| `-509 投稿频繁` | 限流 | 等几分钟再投 |
| `-401 非法访问` | 投币前未播放 | 先 `bili video watch` |
| `certificate verify failed` | SSL证书 | `ssl._create_unverified_context()` |

---

## 📊 第六步：验收标准

完成部署后，检查以下项目：

- [ ] `python scripts/generate_video.py --help` 正常输出
- [ ] `python scripts/select_song.py --test` 能返回候选歌曲
- [ ] `python scripts/check_duplicate.py "测试"` 正常运行
- [ ] `python scripts/download_assets.py <id> /tmp/test` 能下载素材
- [ ] Lrc2Video WebUI 可访问 (http://localhost:7860)
- [ ] 归档目录结构正确
- [ ] 网页能正常生成和访问
- [ ] 定时任务已配置

**全部打 ✅ 后，流水线就搭建完成了！** 🎉

---

## 🆘 遇到问题？

1. 把完整报错信息发给 AI
2. AI 查阅 `docs/troubleshooting.md`
3. 检查 `.env` 配置是否正确
4. 检查网络连接（B站/网易云API）
