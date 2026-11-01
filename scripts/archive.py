#!/usr/bin/env python3
"""
Step 8: 归档整理
用法: python scripts/archive.py <work_dir> <BV号> <歌手> <歌名>
结构: archive/歌手/日期_歌名_BV号/
"""
import json, os, shutil, sys
from datetime import datetime

def archive(work_dir, bvid, artist, title):
    date = datetime.now().strftime('%Y-%m-%d')
    archive_base = os.environ.get('ARCHIVE_DIR', './archive')
    
    # 归档目录名: 日期_歌名_BV号
    dir_name = f"{date}_{title}_{bvid}"
    archive_dir = os.path.join(archive_base, artist, dir_name)
    os.makedirs(archive_dir, exist_ok=True)
    
    # 复制文件
    files = {
        '音频.flac': '音频.flac',
        '歌词.lrc': '歌词.lrc',
        '封面.jpg': '封面.jpg',
        '视频.mp4': '视频.mp4',
    }
    
    for src_name, dst_name in files.items():
        src = os.path.join(work_dir, src_name)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(archive_dir, dst_name))
            print(f"  📁 {dst_name}")
    
    # 写info.json
    info = {
        'title': title,
        'artist': artist,
        'bvid': bvid,
        'date': date,
        'url': f'https://www.bilibili.com/video/{bvid}',
    }
    with open(os.path.join(archive_dir, 'info.json'), 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 归档完成: {archive_dir}")
    return archive_dir

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print("用法: python archive.py <work_dir> <BV号> <歌手> <歌名>")
        sys.exit(1)
    archive(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
