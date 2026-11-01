#!/usr/bin/env python3
"""
Step 3: 下载素材 - 音频(FLAC) + 歌词(LRC) + 封面(JPG)
用法: python scripts/download_assets.py <song_id> <work_dir>
"""
import json, os, ssl, subprocess, sys, time, urllib.parse, urllib.request

ssl._create_default_https_context = ssl._create_unverified_context

NETEASE_COOKIE = os.environ.get('NETEASE_COOKIE', '')
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

def get(url, binary=False, timeout=60):
    headers = {'User-Agent': UA, 'Referer': 'https://music.163.com/'}
    if NETEASE_COOKIE:
        headers['Cookie'] = NETEASE_COOKIE
    req = urllib.request.Request(url, headers=headers)
    data = urllib.request.urlopen(req, timeout=timeout).read()
    return data if binary else json.loads(data.decode())

def download_assets(song_id, work_dir):
    os.makedirs(work_dir, exist_ok=True)
    
    # 1. 详情
    print(f"📥 正在下载素材 (song_id={song_id})...", flush=True)
    d = get(f'https://music.163.com/api/song/detail?ids=[{song_id}]')
    s = d['songs'][0]
    alb = s['album']
    ar = ','.join(a['name'] for a in s['artists'])
    info = {
        'id': s['id'], 'name': s['name'], 'artist': ar,
        'album': alb['name'], 'picUrl': alb.get('picUrl'),
        'duration': s['duration'],
    }
    print(f"  详情: {info['name']} - {info['artist']} | {info['album']}", flush=True)
    
    with open(os.path.join(work_dir, '_info.json'), 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=1)
    time.sleep(1)
    
    # 2. 封面（⚠️ 字段是 picUrl）
    pic = alb.get('picUrl')
    if pic:
        for u in (pic + '?param=1000y1000', pic):
            try:
                raw = get(u, binary=True, timeout=90)
                if len(raw) > 10000:
                    open(os.path.join(work_dir, '封面.jpg'), 'wb').write(raw)
                    print(f"  ✅ 封面: {len(raw)//1024}KB", flush=True)
                    break
            except Exception as e:
                print(f"  封面重试: {e}", flush=True)
    time.sleep(1)
    
    # 3. 音频 320k
    ud = get(f'https://music.163.com/api/song/enhance/player/url?ids=[{song_id}]&br=320000')
    rec = (ud.get('data') or [{}])[0]
    url = rec.get('url')
    
    if url:
        raw = get(url, binary=True, timeout=300)
        mp3 = os.path.join(work_dir, '音频.mp3')
        open(mp3, 'wb').write(raw)
        print(f"  ✅ MP3: {len(raw)/1024/1024:.1f}MB", flush=True)
        
        flac = os.path.join(work_dir, '音频.flac')
        r = subprocess.run(['ffmpeg', '-y', '-i', mp3, '-c:a', 'flac', flac],
                          capture_output=True, text=True, timeout=300)
        if r.returncode == 0 and os.path.getsize(flac) > 100000:
            os.remove(mp3)
            print(f"  ✅ FLAC: {os.path.getsize(flac)/1024/1024:.1f}MB", flush=True)
    else:
        print(f"  ❌ 音频不可用 (code={rec.get('code')})，可能需要VIP Cookie", flush=True)
    time.sleep(1)
    
    # 4. 歌词
    ld = get(f'https://music.163.com/api/song/lyric?id={song_id}&lv=1&kv=1&tv=-1')
    lyric = ((ld.get('lrc') or {}).get('lyric')) or ''
    open(os.path.join(work_dir, '歌词_raw.lrc'), 'w', encoding='utf-8').write(lyric)
    print(f"  ✅ 歌词: {len(lyric)}字符", flush=True)
    
    print(f"\n🎉 素材下载完成: {work_dir}", flush=True)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("用法: python download_assets.py <song_id> <work_dir>")
        sys.exit(1)
    download_assets(sys.argv[1], sys.argv[2])
