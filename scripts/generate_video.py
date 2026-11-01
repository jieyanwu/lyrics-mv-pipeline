#!/usr/bin/env python3
"""
Step 5: 生成视频 - Lrc2Video API 调用
用法: python scripts/generate_video.py <work_dir> [font_color] [outline_color] [outline_width] [bg_color] [font_size]
⚠️ ASS颜色格式: &H00BBGGRR& (BGR顺序)
⚠️ 并发时记录outputs旧文件集，只取新生成的
"""
import json, os, subprocess, sys, time, urllib.request, uuid

BASE = os.environ.get('LRC2VIDEO_URL', 'http://localhost:7860')
OUT_DIR = os.environ.get('LRC2VIDEO_OUTPUTS', '../Lrc2Video/outputs')

def generate(work_dir, font_color='#f5e6d3', outline_color='#2d2416',
             outline_w=3, bg_color='#1a1512', font_size=36):
    
    AUDIO = os.path.join(work_dir, '音频.flac')
    LRC = os.path.join(work_dir, '歌词.lrc')
    COVER = os.path.join(work_dir, '封面.jpg')
    
    # ⚠️ 记录旧文件集（并发安全）
    before = set(os.listdir(OUT_DIR))
    print(f'📁 outputs已有文件: {len(before)}', flush=True)
    print(f'🎨 参数: font={font_color} outline={outline_color}({outline_w}) bg={bg_color} size={font_size}', flush=True)
    
    def upload(path):
        boundary = '----Hermes' + uuid.uuid4().hex
        with open(path, 'rb') as f:
            body = (f'--{boundary}\r\nContent-Disposition: form-data; name="files"; '
                    f'filename="{os.path.basename(path)}"\r\n'
                    f'Content-Type: application/octet-stream\r\n\r\n').encode() + f.read() + f'\r\n--{boundary}--\r\n'.encode()
        req = urllib.request.Request(f'{BASE}/gradio_api/upload', data=body,
                                     headers={'Content-Type': f'multipart/form-data; boundary={boundary}'})
        r = json.load(urllib.request.urlopen(req, timeout=120))
        return r[0]
    
    a = upload(AUDIO); print(f'  音频上传: {os.path.basename(a)}', flush=True)
    l = upload(LRC);   print(f'  歌词上传: {os.path.basename(l)}', flush=True)
    c = upload(COVER); print(f'  封面上传: {os.path.basename(c)}', flush=True)
    
    # Lrc2Video API 参数顺序
    payload = {
        "data": [
            {"path": a, "meta": {"_type": "gradio.FileData"}},
            {"path": l, "meta": {"_type": "gradio.FileData"}},
            {"path": c, "meta": {"_type": "gradio.FileData"}},
            "NotoSansSC", None, font_size,
            font_color, outline_color, outline_w, True,
            "中", "中", 10, 50,
            0, 0,  # fade_in, fade_out = 0 (无渐变)
            bg_color, "1920x1080",
        ]
    }
    
    req = urllib.request.Request(f'{BASE}/gradio_api/call/generate',
                                 data=json.dumps(payload).encode(),
                                 headers={'Content-Type': 'application/json'})
    ev = json.load(urllib.request.urlopen(req, timeout=60))
    event_id = ev['event_id']
    print(f'  EVENT_ID: {event_id}', flush=True)
    
    def probe_ok(p):
        try:
            r = subprocess.run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', p],
                              capture_output=True, text=True, timeout=60)
            return ('duration=' in r.stdout) and ('codec_name=' in r.stdout) and r.returncode == 0
        except Exception:
            return False
    
    # ⚠️ 等待完成：文件大小双稳判断
    target = os.path.join(work_dir, '视频.mp4')
    deadline = time.time() + 1500
    last_sizes = {}
    stable_since = None
    
    while time.time() < deadline:
        time.sleep(20)
        new = [f for f in os.listdir(OUT_DIR) if f not in before and f.endswith('.mp4')]
        if not new:
            print(f'  [{time.strftime("%H:%M:%S")}] 生成中...', flush=True)
            continue
        
        cand = max(new, key=lambda f: os.path.getmtime(os.path.join(OUT_DIR, f)))
        p = os.path.join(OUT_DIR, cand)
        sz = os.path.getsize(p)
        ok = probe_ok(p)
        prev = last_sizes.get(cand)
        
        print(f'  [{time.strftime("%H:%M:%S")}] {cand} size={sz} probe={ok} prev={prev}', flush=True)
        
        if ok and prev == sz:
            if stable_since is None:
                stable_since = time.time()
            elif time.time() - stable_since >= 25:
                subprocess.run(['cp', p, target], check=True)
                print(f'✅ 视频完成: {target} ({sz/1024/1024:.1f}MB)', flush=True)
                return True
        else:
            stable_since = None
        last_sizes[cand] = sz
    
    print('❌ 生成超时', flush=True)
    return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python generate_video.py <work_dir> [font_color] [outline_color] [outline_width] [bg_color] [font_size]")
        sys.exit(1)
    
    wd = sys.argv[1]
    fc = sys.argv[2] if len(sys.argv) > 2 else '#f5e6d3'
    oc = sys.argv[3] if len(sys.argv) > 3 else '#2d2416'
    ow = int(sys.argv[4]) if len(sys.argv) > 4 else 3
    bg = sys.argv[5] if len(sys.argv) > 5 else '#1a1512'
    fs = int(sys.argv[6]) if len(sys.argv) > 6 else 36
    
    ok = generate(wd, fc, oc, ow, bg, fs)
    sys.exit(0 if ok else 1)
