#!/usr/bin/env python3
"""
Step 7: 双账号互动
用法: python scripts/engage.py <BV号>
⚠️ 投币前必须先播放视频！
⚠️ 限频: 弹幕10秒/评论10秒/动态60秒
"""
import os, subprocess, sys, time

COOKIE_FILE = os.environ.get('BILI_COOKIE_FILE', './cookies.json')
SUB_CLI_HOME = os.environ.get('BILI_CLI_HOME_ALT', '')  # 小号配置目录

def bili_cmd(*args, sub_account=False):
    """执行bili命令"""
    env = os.environ.copy()
    if sub_account and SUB_CLI_HOME:
        env['BILI_CLI_HOME'] = SUB_CLI_HOME
    r = subprocess.run(['bili', *args], capture_output=True, text=True, timeout=60, env=env)
    return r.stdout

def engage(bv):
    print(f"💬 开始互动: {bv}", flush=True)
    
    # 主号弹幕
    danmaku_text = "听到这句你破防了吗"
    print(f"  发弹幕: {danmaku_text}", flush=True)
    bili_cmd('danmaku', 'send', bv, danmaku_text, '--time', '30')
    time.sleep(10)  # 限频
    
    # 主号评论
    comment_text = "你们第一次听这首歌是什么时候？"
    print(f"  发评论: {comment_text}", flush=True)
    bili_cmd('comment', 'post', bv, comment_text)
    time.sleep(10)
    
    # 小号互动（如果配置了）
    if SUB_CLI_HOME:
        print(f"  小号互动...", flush=True)
        bili_cmd('comment', 'post', bv, "好听！", sub_account=True)
        time.sleep(10)
        bili_cmd('video', 'like', bv, sub_account=True)
        time.sleep(5)
        bili_cmd('video', 'fav', bv, sub_account=True)
    
    print(f"✅ 互动完成", flush=True)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python engage.py <BV号>")
        sys.exit(1)
    engage(sys.argv[1])
