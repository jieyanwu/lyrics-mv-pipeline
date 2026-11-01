#!/usr/bin/env python3
"""
Step 1: AI选歌 - 搜索热门歌曲 + 检测音源可用性
用法: python scripts/select_song.py [--genre pop] [--mood emotional] [--limit 5] [--test]
"""
import json, ssl, sys, time, urllib.parse, urllib.request, argparse, os

ssl._create_default_https_context = ssl._create_unverified_context

# 从环境变量加载Cookie（可选）
NETEASE_COOKIE = os.environ.get('NETEASE_COOKIE', '')
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

def get(url, timeout=30):
    headers = {'User-Agent': UA, 'Referer': 'https://music.163.com/'}
    if NETEASE_COOKIE:
        headers['Cookie'] = NETEASE_COOKIE
    req = urllib.request.Request(url, headers=headers)
    return json.load(urllib.request.urlopen(req, timeout=timeout))

def search_song(keyword, limit=5):
    """搜索歌曲"""
    data = urllib.parse.urlencode({'s': keyword, 'type': 1, 'limit': limit}).encode()
    headers = {'User-Agent': UA, 'Referer': 'https://music.163.com/'}
    if NETEASE_COOKIE:
        headers['Cookie'] = NETEASE_COOKIE
    req = urllib.request.Request('https://music.163.com/api/search/get/web', data=data, headers=headers)
    return json.load(urllib.request.urlopen(req, timeout=30))['result']['songs']

def check_audio_availability(song_id):
    """检测320k音频可用性"""
    j = get(f'https://music.163.com/api/song/enhance/player/url?ids=[{song_id}]&br=320000')
    d0 = (j.get('data') or [{}])[0]
    return {
        'available': bool(d0.get('url')),
        'code': d0.get('code'),
        'br': d0.get('br'),
    }

def select_song(candidates, limit=5):
    """从候选列表选歌"""
    results = []
    for name, artist in candidates:
        try:
            songs = search_song(f'{name} {artist}')
            hit = None
            for s in songs:
                ar = ','.join(a['name'] for a in s['artists'])
                if name in s['name'] and artist in ar and 'Live' not in s['name'] and '伴奏' not in s['name']:
                    hit = s
                    break
            
            if not hit:
                results.append({'name': name, 'artist': artist, 'status': 'not_found'})
                continue
            
            sid = hit['id']
            time.sleep(1)
            audio = check_audio_availability(sid)
            
            results.append({
                'name': hit['name'],
                'artist': ','.join(a['name'] for a in hit['artists']),
                'album': hit['album']['name'],
                'song_id': sid,
                'duration': hit['duration'] / 1000,
                'fee': hit.get('fee', '?'),
                'audio_available': audio['available'],
                'audio_code': audio['code'],
                'status': 'available' if audio['available'] else 'vip_restricted',
            })
            
            time.sleep(1)
        except Exception as e:
            results.append({'name': name, 'artist': artist, 'status': f'error: {e}'})
    
    return results[:limit]

def main():
    parser = argparse.ArgumentParser(description='AI选歌')
    parser.add_argument('--genre', default='pop', help='音乐类型')
    parser.add_argument('--mood', default='emotional', help='情感偏好')
    parser.add_argument('--limit', type=int, default=5, help='推荐数量')
    parser.add_argument('--test', action='store_true', help='测试模式')
    parser.add_argument('--auto', action='store_true', help='自动选择最佳歌曲')
    args = parser.parse_args()
    
    # 候选歌曲池（真实热门歌曲）
    candidates = [
        ('小幸运', '田馥甄'),
        ('突然好想你', '五月天'),
        ('江南', '林俊杰'),
        ('童话', '光良'),
        ('蓝莲花', '许巍'),
        ('老男孩', '筷子兄弟'),
        ('唯一', '王力宏'),
        ('再见', '张震岳'),
        ('听海', '张惠妹'),
        ('晴天', '周杰伦'),
    ]
    
    if args.test:
        print("测试模式：检测音源可用性")
        results = select_song(candidates[:3], limit=3)
        for r in results:
            status = "✅" if r.get('audio_available') else "❌"
            print(f"  {status} {r['name']} - {r['artist']} | fee={r.get('fee')} | {r.get('status')}")
        return
    
    print(f"🎵 AI选歌 (genre={args.genre}, mood={args.mood})")
    results = select_song(candidates, limit=args.limit)
    
    available = [r for r in results if r.get('audio_available')]
    
    print(f"\n📊 结果: {len(available)}/{len(results)} 首可用")
    for i, r in enumerate(results):
        status = "✅" if r.get('audio_available') else "❌"
        print(f"  {i+1}. {status} {r['name']} - {r['artist']} | {r.get('album', '?')} | fee={r.get('fee')}")
    
    if args.auto and available:
        best = available[0]
        print(f"\n🎯 自动选择: {best['name']} - {best['artist']} (id={best['song_id']})")
    
    # 输出JSON供pipeline使用
    print(f"\n{json.dumps(available[0] if available else {}, ensure_ascii=False)}")

if __name__ == '__main__':
    main()
