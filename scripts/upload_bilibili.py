#!/usr/bin/env python3
"""
Step 6: B站上传
用法: python scripts/upload_bilibili.py <video> --title "..." --desc "..." --tag "..." --cover ...
"""
import argparse, json, os, subprocess, sys

COOKIE_FILE = os.environ.get('BILI_COOKIE_FILE', './cookies.json')

def upload(video_path, title, desc, tags, cover_path):
    cmd = [
        'biliup', '-u', COOKIE_FILE, 'upload', video_path,
        '--title', title,
        '--desc', desc,
        '--tag', tags,
    ]
    if cover_path:
        cmd.extend(['--cover', cover_path])
    
    print(f"📤 上传中: {title}", flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    
    # 从输出提取BV号
    import re
    bv_match = re.search(r'"bvid":\s*"(BV\w+)"', r.stdout)
    bv = bv_match.group(1) if bv_match else None
    
    if bv:
        print(f"✅ 上传成功! BV号: {bv}", flush=True)
    else:
        print(f"上传输出: {r.stdout[-200:]}", flush=True)
    
    return bv

def main():
    parser = argparse.ArgumentParser(description='B站上传')
    parser.add_argument('video', help='视频文件路径')
    parser.add_argument('--title', required=True, help='标题')
    parser.add_argument('--desc', required=True, help='简介')
    parser.add_argument('--tag', required=True, help='标签(逗号分隔)')
    parser.add_argument('--cover', help='封面图片路径')
    args = parser.parse_args()
    
    bv = upload(args.video, args.title, args.desc, args.tag, args.cover)
    
    if bv:
        # 输出JSON供pipeline使用
        print(f'\n{{"bvid": "{bv}"}}')

if __name__ == '__main__':
    main()
