#!/usr/bin/env python3
"""
Step 4: 歌词清理 - 去制作信息/去标点/逐字同步
用法: python scripts/clean_lyrics.py <work_dir>
"""
import re, sys, os

def clean_lyrics(work_dir):
    raw_path = os.path.join(work_dir, '歌词_raw.lrc')
    out_path = os.path.join(work_dir, '歌词.lrc')
    
    with open(raw_path, 'r', encoding='utf-8') as f:
        raw = f.read()
    
    lines = raw.strip().split('\n')
    result = []
    
    for line in lines:
        m = re.match(r'\[(\d+:\d+\.\d+)\](.*)', line.strip())
        if not m:
            continue
        
        time_str = m.group(1)
        text = m.group(2).strip()
        
        # 跳过制作信息
        if any(kw in text for kw in ['作词', '作曲', '编曲', '制作人', '监制', '录音', '混音']):
            continue
        
        # 跳过空行
        if not text:
            continue
        
        # 清除非歌词字符（保留中文、日文、韩文、英文、数字）
        cleaned = re.sub(r'[^一-龥぀-ヿ가-힯々〆a-zA-Z0-9]', '', text)
        
        if cleaned:
            result.append(f'[{time_str}]{cleaned}')
    
    output = '\n'.join(result)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(output)
    
    print(f"📝 歌词清理完成: {len(lines)}行 → {len(result)}行")
    print(f"   输出: {out_path}")
    
    # 预览
    for line in result[:5]:
        print(f"   {line}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python clean_lyrics.py <work_dir>")
        sys.exit(1)
    clean_lyrics(sys.argv[1])
