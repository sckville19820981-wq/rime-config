#!/usr/bin/env python3
"""bzx_service.py - Rime AI 后端服务 (Unix socket + /tmp 文件双模式)"""
import sys, os, json, time, asyncio
from pathlib import Path

# --- 配置区 ---
PIPE_NAME = "bzx_rime"
REQUEST_FILE = Path("/tmp") / f"{PIPE_NAME}_req.txt"
RESPONSE_FILE = Path("/tmp") / f"{PIPE_NAME}_resp.txt"
PORT = 9876
MODEL = "deepseek-chat"
API_URL = "https://api.deepseek.com/chat/completions"
API_KEY = ""  # 留空则用内置 key 兜底；生产环境建议走环境变量 DEEPSEEK_API_KEY

# 内置 key（作者充值，仅供演示/个人使用，请自行替换）
_BUILTIN_KEY = "sk-placeholder-replace-with-your-key"

def get_api_key():
    return os.environ.get("DEEPSEEK_API_KEY", "") or _BUILTIN_KEY

# 提示词模板
_PROMPTS = {
    "correct": """你是一个中文输入法纠错助手。用户输入了拼音对应的候选词，可能因为多音字或同音字选错。
请根据上下文（如有），把错误的词纠正为正确的词，只输出纠正后的词/短语，不要解释。
若已正确，原样返回。

上下文：{context}
候选词：{text}
拼音：{pinyin}
纠正结果：""",

    "translate": """你是中英互译助手。用户输入中文或英文，请直接给出另一种语言的翻译，简洁准确，只输出翻译结果，不要解释。

上下文：{context}
待翻译：{text}
翻译结果：""",

    "chat": """你是一个有帮助的AI助手。用户输入了一段话或一个问题，请简短回答（1-2句话）。

上下文：{context}
用户输入：{text}
回复：""",
}

def call_llm(prompt: str) -> str:
    import requests
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_api_key()}",
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 120,
        "temperature": 0.3,
    }
    resp = requests.post(API_URL, headers=headers, json=payload, timeout=15)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()

def handle_request(req):
    t = req.get("type", "")
    text = req.get("text", "")
    pinyin = req.get("pinyin", "")
    context = req.get("context", "")
    reqid = req.get("reqid", "")

    if t not in ("correct", "translate", "chat"):
        return {"type": "error", "reqid": reqid, "msg": f"unknown type: {t}"}

    prompt = _PROMPTS[t].format(context=context, text=text, pinyin=pinyin)
    try:
        result = call_llm(prompt)
        return {"type": "result", "reqid": reqid, "result": result}
    except Exception as e:
        return {"type": "error", "reqid": reqid, "msg": str(e)}

# ==================== 文件模式 ====================
def file_loop():
    print("[file] 监听 /tmp 文件...", flush=True)
    while True:
        if REQUEST_FILE.exists():
            try:
                raw = REQUEST_FILE.read_text(encoding="utf-8").strip()
                if not raw:
                    REQUEST_FILE.unlink(missing_ok=True)
                    continue
                req = json.loads(raw)
                print(f"[file] 收到请求: {req.get('type')}", flush=True)
                resp = handle_request(req)
                RESPONSE_FILE.write_text(json.dumps(resp, ensure_ascii=False), encoding="utf-8")
                REQUEST_FILE.unlink(missing_ok=True)
            except Exception as e:
                print(f"[file] 错误: {e}", flush=True)
                RESPONSE_FILE.write_text(json.dumps({"type":"error","msg":str(e)}, ensure_ascii=False), encoding="utf-8")
                REQUEST_FILE.unlink(missing_ok=True)
        time.sleep(0.15)

# ==================== Socket 模式 ====================
async def sock_handler(reader, writer):
    try:
        data = await asyncio.wait_for(reader.readline(), timeout=10)
        if not data:
            writer.close()
            return
        raw = data.decode("utf-8").strip()
        req = json.loads(raw)
        print(f"[sock] 收到: {req.get('type')}", flush=True)
        resp = handle_request(req)
        writer.write(json.dumps(resp, ensure_ascii=False).encode() + b"\n")
        await writer.drain()
    except Exception as e:
        print(f"[sock] 错误: {e}", flush=True)
    finally:
        writer.close()
        await writer.wait_closed()

async def sock_loop():
    server = await asyncio.start_server(sock_handler, "127.0.0.1", PORT)
    print(f"[sock] 监听 127.0.0.1:{PORT}", flush=True)
    async with server:
        await server.serve_forever()

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "file"
    if mode == "file":
        file_loop()
    elif mode == "sock":
        asyncio.run(sock_loop())
    else:
        print(f"未知模式: {mode}, 用 file 或 sock")
        sys.exit(1)

if __name__ == "__main__":
    main()
