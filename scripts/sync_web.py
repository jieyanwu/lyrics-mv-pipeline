#!/usr/bin/env python3
"""
Step 9: 更新网页 - 生成Element UI风格歌曲列表
用法: python scripts/sync_web.py
数据以B站为准
"""
import json, os, re, subprocess
from datetime import datetime

COOKIE_FILE = os.environ.get('BILI_COOKIE_FILE', './cookies.json')
WEB_DIR = os.environ.get('WEB_DIR', './web_output')

def fetch_bili_list():
    """获取B站视频列表"""
    r = subprocess.run(['biliup', '-u', COOKIE_FILE, 'list'],
                      capture_output=True, text=True, timeout=120)
    
    videos = []
    for line in r.stdout.split('\n'):
        if 'BV' not in line:
            continue
        parts = line.split('\t')
        if len(parts) >= 2:
            bv = parts[0].strip()
            title = parts[1].strip()
            # 解析歌名和歌手
            m = re.match(r'(.+?) - (.+?)｜(.+)', title)
            if m:
                videos.append({
                    'bvid': bv,
                    'title': m.group(1),
                    'artist': m.group(2),
                    'quote': m.group(3),
                    'full_title': title,
                })
    return videos

def generate_web(videos):
    """生成网页"""
    os.makedirs(WEB_DIR, exist_ok=True)
    
    # 读取模板
    template_path = os.path.join(os.path.dirname(__file__), '..', 'web', 'template.html')
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            html = f.read()
    else:
        html = DEFAULT_TEMPLATE
    
    # 生成歌曲卡片
    cards = []
    for v in videos:
        cards.append(f'''
    <div class="song-card" data-search="{v['title']} {v['artist']}">
      <div class="song-title">
        <a href="https://www.bilibili.com/video/{v['bvid']}" target="_blank">{v['title']}</a>
      </div>
      <div class="song-artist">{v['artist']}</div>
      <div class="song-quote">{v['quote']}</div>
    </div>''')
    
    html = html.replace('<!-- SONG_CARDS -->', '\n'.join(cards))
    html = html.replace('{{COUNT}}', str(len(videos)))
    
    output_path = os.path.join(WEB_DIR, 'index.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ 网页已生成: {output_path} ({len(videos)}首歌)")

# 默认模板（Element UI风格）
DEFAULT_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>歌词MV · 作品集</title>
<link rel="stylesheet" href="https://unpkg.com/element-ui/lib/theme-chalk/index.css">
<style>
body { background: #f5f7fa; font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif; margin: 0; }
.container { max-width: 1200px; margin: 24px auto; padding: 0 24px; }
.page-title { font-size: 22px; font-weight: 600; color: #303133; }
.page-desc { color: #909399; font-size: 14px; margin-bottom: 24px; }
.song-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; }
.song-card { background: #fff; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); padding: 18px 20px; transition: all .2s; }
.song-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.1); transform: translateY(-2px); }
.song-title a { color: #303133; text-decoration: none; font-size: 15px; font-weight: 600; }
.song-title a:hover { color: #409EFF; }
.song-artist { color: #909399; font-size: 13px; margin: 4px 0; }
.song-quote { color: #606266; font-size: 13px; }
@media (max-width: 768px) { .song-grid { grid-template-columns: 1fr; } .container { padding: 0 12px; } }
</style>
</head>
<body>
<div class="container">
  <h1 class="page-title">🎵 歌词MV 作品集</h1>
  <p class="page-desc">共 {{COUNT}} 首歌曲</p>
  <div class="song-grid">
<!-- SONG_CARDS -->
  </div>
</div>
</body>
</html>'''

def main():
    videos = fetch_bili_list()
    print(f"📋 获取到 {len(videos)} 个视频")
    generate_web(videos)

if __name__ == '__main__':
    main()
