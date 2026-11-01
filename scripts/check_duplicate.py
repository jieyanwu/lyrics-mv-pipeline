#!/usr/bin/env python3
"""
Step 2: 查重 - 检查B站是否已有同名视频
用法: python scripts/check_duplicate.py "歌名"
⚠️ 必须单次抓取存文件再grep！
"""
import subprocess, sys, os, tempfile

COOKIE_FILE = os.environ.get('BILI_COOKIE_FILE', './cookies.json')

def fetch_list(cache_file='/tmp/biliup_list_cache.txt'):
    """单次抓取B站视频列表存到文件"""
    r = subprocess.run(
        ['biliup', '-u', COOKIE_FILE, 'list'],
        capture_output=True, text=True, timeout=120
    )
    with open(cache_file, 'w', encoding='utf-8') as f:
        f.write(r.stdout)
    return cache_file

def check_duplicate(song_name, cache_file=None):
    """查重：返回是否重复"""
    if cache_file is None or not os.path.exists(cache_file):
        cache_file = fetch_list()
    
    with open(cache_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # grep搜索
    matches = [line for line in content.split('\n') if song_name in line]
    
    return {
        'duplicate': len(matches) > 0,
        'matches': matches,
        'count': len(matches),
    }

def main():
    if len(sys.argv) < 2:
        print("用法: python check_duplicate.py <歌名>")
        sys.exit(1)
    
    song_name = sys.argv[1]
    
    # 先抓取列表存文件（关键！避免循环调用）
    cache = fetch_list()
    print(f"📋 已缓存视频列表: {cache}")
    
    result = check_duplicate(song_name, cache)
    
    if result['duplicate']:
        print(f"❌ 发现重复 ({result['count']}个):")
        for m in result['matches']:
            print(f"  {m}")
        print(f"\n⚠️ 「{song_name}」已存在，请换一首歌！")
        sys.exit(1)
    else:
        print(f"✅ 「{song_name}」无重复，可以制作")
        sys.exit(0)

if __name__ == '__main__':
    main()
