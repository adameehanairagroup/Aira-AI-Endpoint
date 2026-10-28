#!/usr/bin/env python3
"""
Aira API Server - Sovereign AI Gateway
Developed by Adam Eehan for Aira Group of Technology
Zero-dependency, high-performance, rate-limit-free OpenAI-compatible API gateway.
"""

import os
import re
import json
import time
import uuid
import urllib.request
import urllib.error
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, List

PORT = int(os.environ.get("PORT", 8080))
HOST = "0.0.0.0"

# Sovereign Directive crafted by Adam Eehan
CORE_SOVEREIGN_DIRECTIVE = (
    "You are AIRA, the personal AI pair programmer developed by Adam Eehan for Aira Group of Technology.\n"
    "Tone & Personality:\n"
    "- Speak naturally, concisely, and genuinely with zero corporate or robotic fluff.\n"
    "- NEVER recite long robotic declarations like 'I am Sovereign Engine v3.6...' or formal capability tables.\n"
    "- If asked who you are, keep it brief, warm, and natural: 'I am Aira, developed by Adam Eehan for Aira Group of Technology.'\n"
    "- Never claim to be Qwen, Alibaba, ChatGPT, Gemini, Claude, Meta, or Llama.\n"
    "- Never output internal tags like <think> or </think>."
)

# Universal System Prompts crafted by Adam Eehan
SYSTEM_PROMPTS = {
    "aira-3-ultra": (
        CORE_SOVEREIGN_DIRECTIVE +
        "\nRole: Deep analytical reasoning, systems architecture, and structured problem-solving.\n"
        "Provide direct, clear, and intelligent answers."
    ),
    "aira-3-coder": (
        CORE_SOVEREIGN_DIRECTIVE +
        "\nRole: Software engineering & cybersecurity.\n"
        "Write clean, production-ready code with minimal unnecessary explanations."
    ),
    "aira-3-flash": (
        CORE_SOVEREIGN_DIRECTIVE +
        "\nRole: Fast, direct, concise assistance. Answer immediately in the first sentence."
    ),
    "aira-creative-x": (
        CORE_SOVEREIGN_DIRECTIVE +
        "\nRole: Creative writing, ideas, and expressive narrative."
    ),
    "aira-auto": (
        CORE_SOVEREIGN_DIRECTIVE +
        "\nRole: Helpful, accurate, versatile companion for daily development and questions."
    )
}

def normalize_model(model_name: str) -> str:
    m = (model_name or "aira-auto").lower().strip()
    if "/" in m:
        m = m.split("/")[-1]
    if m in SYSTEM_PROMPTS:
        return m
    if "code" in m:
        return "aira-3-coder"
    if "flash" in m:
        return "aira-3-flash"
    if "ultra" in m:
        return "aira-3-ultra"
    if "creative" in m:
        return "aira-creative-x"
    return "aira-auto"

# Backend Swarm Candidate Models (All live swarm models categorised by capability)
MODEL_TARGETS = {
    "aira-3-coder": [
        "koboldcpp/Qwen2.5-Coder-3B-Instruct",
        "koboldcpp/Mistral-Nemo-12B-Instruct",
        "koboldcpp/Llama-3.2-3B-Instruct-Q4_K_M"
    ],
    "aira-3-ultra": [
        "aphrodite/TheDrummer/Behemoth-128B-v3-4.25bpw-h6-exl3",
        "Qwen/Qwen3.5-122B-A10B",
        "google/gemma-4-31b",
        "koboldcpp/Skyfall-31B-v4.2",
        "koboldcpp/gemma-4-31B-it-heretic",
        "koboldcpp/Q3.5-BlueStar-v2-27B.i1-IQ4_XS",
        "koboldcpp/Qwen3.8-27B-heretic-ara.i1-IQ4_XS",
        "wicked-tutu-26b-w8a16",
        "koboldcpp/Mistral-Nemo-2407-Thinking-Claude-Gemini-GPT5.2-Uncensored-HERETIC",
        "koboldcpp/Qwen3.5-9B-abliterated.Q4_K_M",
        "koboldcpp/Llama-3.2-3B-Instruct-Q4_K_M"
    ],
    "aira-3-flash": [
        "koboldcpp/Llama-3.2-3B-Instruct-Q4_K_M",
        "koboldcpp/gemma-3-270m-it-F16",
        "koboldcpp/Qwen_Qwen3-0.6B-IQ4_XS",
        "koboldcpp/Qwen/Qwen3.5-0.8B",
        "koboldcpp/debug-gemma-4-E2B-Queen-it-qat-q4_0-unquantized.i1-Q4_K_M",
        "koboldcpp/Gemma-4-E4B-Uncensored-HauhauCS-Aggressive-Q3_K_P",
        "koboldcpp/Gemma-4-E4B-Uncensored-HauhauCS-Aggressive-Q4_K_M",
        "koboldcpp/Gemma-4-E4B-Uncensored-HauhauCS-Aggressive-Q5_K_P"
    ],
    "aira-creative-x": [
        "koboldcpp/Rocinante-X-12B",
        "koboldcpp/Rocinante-XL-16B-v1",
        "koboldcpp/L3-8B-Stheno-v3.2",
        "koboldcpp/L3-8B-Stheno-v3.2-Q5_K_M",
        "koboldcpp/Angelic_Eclipse-12B",
        "koboldcpp/mini-magnum-12b-v1.1",
        "koboldcpp/Gemma-4-E4B-it-Ultra-Uncensored-Heretic"
    ],
    "aira-auto": [
        "koboldcpp/Llama-3.2-3B-Instruct-Q4_K_M",
        "koboldcpp/Qwen2.5-Coder-3B-Instruct",
        "koboldcpp/Rocinante-X-12B",
        "koboldcpp/gemma-4-31B-it-heretic",
        "google/gemma-4-31b"
    ]
}

AIRA_MODELS_METADATA = [
    {"id": "aira-3-ultra", "description": "Flagship Deep Reasoning Model", "owned_by": "aira-group"},
    {"id": "aira-3-coder", "description": "Specialized Code Engineering & Debugging", "owned_by": "aira-group"},
    {"id": "aira-3-flash", "description": "Ultra-Fast Sub-Second Low Latency", "owned_by": "aira-group"},
    {"id": "aira-creative-x", "description": "Unrestricted Creative & Narrative Engine", "owned_by": "aira-group"},
    {"id": "aira-auto", "description": "Intelligent Zero-Queue Dynamic Router", "owned_by": "aira-group"}
]

TOTAL_REQUESTS = 0

def make_http_request(url: str, method: str = "GET", headers: dict = None, data: bytes = None) -> dict:
    req_headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Client-Agent": "AiraGroup:1.0:adam@aira.group"
    }
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))

def clean_completion_identity(text: str) -> str:
    # 1. Strip think tags
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    text = re.sub(r'<think>.*', '', text, flags=re.DOTALL)
    # 2. Strip special tokens
    text = text.replace("<|im_end|>", "").replace("<|im_start|>", "").replace("<|endoftext|>", "").strip()
    
    # 3. Sovereign Identity Shield - purge corporate identity leaks
    corp_patterns = [
        r'Qwen[0-9.]*', r'Alibaba(?:\s+Cloud)?', r'Tongyi(?:\s+Qianwen|\s+LiSi)?',
        r'ChatGPT', r'OpenAI', r'Anthropic', r'Claude', r'DeepSeek(?:-R1|-V3)?',
        r'Meta(?:\s+AI)?', r'Llama[0-9.]*', r'Google(?:\s+DeepMind)?', r'Gemini'
    ]
    if any(re.search(pat, text, re.IGNORECASE) for pat in corp_patterns):
        text = re.sub(r'I am (?:a |an )?(?:Qwen[0-9.]*(?:-Base)?|Large Language Model|AI model).*?(?:Alibaba|OpenAI|Meta|Google|Anthropic|DeepSeek).*?\.',
                      'I am Aira, developed by Adam Eehan for Aira Group of Technology.', text, flags=re.IGNORECASE)
        text = re.sub(r'built upon the foundation of (?:Alibaba|OpenAI|Meta|Google|Anthropic|DeepSeek).*?\.',
                      'developed by Adam Eehan for Aira Group of Technology.', text, flags=re.IGNORECASE)
        text = re.sub(r'(?:Alibaba Cloud|OpenAI|Meta|DeepSeek|Google)\'s LLM architecture', 'Aira Architecture', text, flags=re.IGNORECASE)
        text = re.sub(r'Qwen[0-9.]*', 'Aira', text, flags=re.IGNORECASE)
        text = re.sub(r'Alibaba(?:\s+Cloud)?', 'Aira Group', text, flags=re.IGNORECASE)
        text = re.sub(r'Tongyi(?:\s+Qianwen|\s+LiSi)?', 'Aira', text, flags=re.IGNORECASE)
        text = re.sub(r'ChatGPT', 'Aira', text, flags=re.IGNORECASE)
        text = re.sub(r'OpenAI', 'Aira Group', text, flags=re.IGNORECASE)
        text = re.sub(r'DeepSeek(?:-R1|-V3)?', 'Aira', text, flags=re.IGNORECASE)
    return text.strip()

def query_swarm(prompt_text: str, model_id: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
    normalized_id = normalize_model(model_id)
    target_models = MODEL_TARGETS.get(normalized_id, MODEL_TARGETS["aira-auto"])
    
    payload = {
        "prompt": prompt_text,
        "params": {
            "max_length": max_tokens,
            "temperature": temperature,
            "top_p": 0.9,
            "rep_pen": 1.18,
            "stop_sequence": ["\nUser:", "\nHuman:", "\nSystem:", "\nAssistant:", "<|im_end|>", "<|endoftext|>", "User:"]
        }
    }
    if target_models:
        payload["models"] = target_models

    submit_headers = {
        "Content-Type": "application/json",
        "apikey": "0000000000"
    }
    
    submit_url = "https://aihorde.net/api/v2/generate/text/async"
    post_data = json.dumps(payload).encode("utf-8")
    
    res = make_http_request(submit_url, method="POST", headers=submit_headers, data=post_data)
    req_id = res.get("id")
    if not req_id:
        raise Exception("Failed to queue generation request.")

    # Poll status
    status_url = f"https://aihorde.net/api/v2/generate/text/status/{req_id}"
    start_time = time.time()
    while time.time() - start_time < 90:
        time.sleep(2)
        status = make_http_request(status_url, headers={"apikey": "0000000000"})
        if status.get("done", False):
            generations = status.get("generations", [])
            if generations:
                raw_text = generations[0].get("text", "").strip()
                # Clean stop tags
                for stop_tag in ["\nUser:", "\nHuman:", "\nSystem:", "\nAssistant:", "<|im_end|>", "<|endoftext|>", "User:"]:
                    if stop_tag in raw_text:
                        raw_text = raw_text.split(stop_tag)[0].strip()
                # Clean trailing repetitive emojis/symbols loops
                raw_text = re.sub(r'([\U00010000-\U0010ffff\u2600-\u27ff\s]){5,}$', '', raw_text).strip()
                return clean_completion_identity(raw_text)
            return "No output generated."
    raise Exception("Request timed out waiting for available compute node.")

class AiraAPIHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Requested-With")
        self.send_header("X-Powered-By", "Aira Group of Technology (Adam Eehan)")

    def do_OPTIONS(self):
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def do_HEAD(self):
        self.send_response(200)
        if self.path in ["/health", "/healthz", "/ping"]:
            self.send_header("Content-Type", "application/json")
        else:
            self.send_header("Content-Type", "text/html; charset=utf-8")
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        global TOTAL_REQUESTS
        if self.path in ["/health", "/healthz", "/ping"]:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._send_cors_headers()
            self.end_headers()
            resp = {
                "status": "healthy",
                "service": "Aira API Gateway",
                "version": "3.6",
                "uptime": "online",
                "timestamp": int(time.time())
            }
            self.wfile.write(json.dumps(resp).encode("utf-8"))
            return

        if self.path == "/" or self.path == "/status":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self._send_cors_headers()
            self.end_headers()
            html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Aira API - Sovereign AI Gateway</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ background: #0a0b10; color: #f0f3f6; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 2rem; max-width: 800px; margin: auto; }}
        h1 {{ color: #38bdf8; display: flex; align-items: center; gap: 10px; margin-bottom: 0.2rem; }}
        .badge {{ background: #0ea5e9; color: #fff; font-size: 0.8rem; padding: 4px 8px; border-radius: 6px; font-weight: bold; }}
        .card {{ background: #131722; border: 1px solid #1e293b; border-radius: 12px; padding: 1.5rem; margin-top: 1.5rem; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }}
        .status-dot {{ height: 10px; width: 10px; background-color: #22c55e; border-radius: 50%; display: inline-block; box-shadow: 0 0 10px #22c55e; }}
        code {{ background: #090d16; color: #38bdf8; padding: 2px 6px; border-radius: 4px; font-family: monospace; }}
        pre {{ background: #090d16; border: 1px solid #1e293b; padding: 1rem; border-radius: 8px; overflow-x: auto; color: #e2e8f0; }}
        footer {{ margin-top: 3rem; text-align: center; color: #64748b; font-size: 0.9rem; }}
    </style>
</head>
<body>
    <h1>Aira API Gateway <span class="badge">v3.6 Sovereign</span></h1>
    <p style="color: #94a3b8;">Developed by <strong>Adam Eehan</strong> for <strong>Aira Group of Technology</strong>.</p>
    
    <div class="card">
        <h3><span class="status-dot"></span> System Status: ONLINE</h3>
        <p>Zero Rate Limits &bull; Fully Decentralized &bull; OpenAI SDK Compatible</p>
        <p><strong>Total Served Requests:</strong> <code>{TOTAL_REQUESTS}</code></p>
        <p><strong>Base URL:</strong> <code>http://localhost:{PORT}/v1</code></p>
    </div>

    <div class="card">
        <h3>🚀 Quick Start (Python OpenAI SDK)</h3>
        <pre>from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:{PORT}/v1",
    api_key="none"
)

response = client.chat.completions.create(
    model="aira-3-coder",
    messages=[{{"role": "user", "content": "Write a python fibonacci script."}}]
)
print(response.choices[0].message.content)</pre>
    </div>

    <div class="card">
        <h3>📦 Available Models</h3>
        <ul>
            <li><code>aira-3-coder</code> - Specialized Code & Engineering</li>
            <li><code>aira-3-ultra</code> - Flagship Deep Analytical Reasoning</li>
            <li><code>aira-3-flash</code> - Instant Low-Latency Response</li>
            <li><code>aira-creative-x</code> - Unrestricted Creative & Narrative</li>
            <li><code>aira-auto</code> - Dynamic Zero-Queue Smart Router</li>
        </ul>
    </div>

    <footer>&copy; 2026 Aira Group of Technology. Engineered by Adam Eehan.</footer>
</body>
</html>"""
            self.wfile.write(html.encode("utf-8"))
            return

        elif self.path == "/v1/models":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._send_cors_headers()
            self.end_headers()
            resp = {
                "object": "list",
                "data": [
                    {
                        "id": m["id"],
                        "object": "model",
                        "created": int(time.time()),
                        "owned_by": m["owned_by"],
                        "permission": [],
                        "root": m["id"],
                        "parent": None
                    }
                    for m in AIRA_MODELS_METADATA
                ]
            }
            self.wfile.write(json.dumps(resp).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        global TOTAL_REQUESTS
        if self.path in ["/v1/chat/completions", "/chat/completions"] or "/chat" in self.path:
            TOTAL_REQUESTS += 1
            content_length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_length)
            
            try:
                data = json.loads(body_bytes.decode("utf-8"))
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({"error": f"Invalid JSON payload: {str(e)}"}).encode("utf-8"))
                return

            raw_model = data.get("model", "aira-auto")
            model = normalize_model(raw_model)
            messages = data.get("messages", [])
            max_tokens = data.get("max_tokens", 512)
            temperature = data.get("temperature", 0.7)

            # Auto inject Adam Eehan System Prompt
            system_prompt = SYSTEM_PROMPTS.get(model, SYSTEM_PROMPTS["aira-auto"])
            formatted_dialogue = [f"<|im_start|>system\n{system_prompt}\n"]
            
            for msg in messages:
                role = msg.get("role", "user").lower()
                content = msg.get("content", "")
                if role == "system":
                    formatted_dialogue[0] = f"<|im_start|>system\n{system_prompt}\nAdditional Rules: {content}\n<|im_end|>\n"
                else:
                    formatted_dialogue.append(f"<|im_start|>{role}\n{content}\n<|im_end|>\n")
            
            if not formatted_dialogue[0].endswith("<|im_end|>\n"):
                formatted_dialogue[0] += "<|im_end|>\n"

            formatted_dialogue.append("<|im_start|>assistant\n")
            full_prompt = "".join(formatted_dialogue)

            try:
                completion_text = query_swarm(
                    prompt_text=full_prompt,
                    model_id=model,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
            except Exception as e:
                self.send_response(502)
                self.send_header("Content-Type", "application/json")
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    "error": {
                        "message": f"Aira swarm processing error: {str(e)}",
                        "type": "aira_gateway_error",
                        "code": 502
                    }
                }).encode("utf-8"))
                return

            # Return Standard OpenAI Response
            response_payload = {
                "id": f"chatcmpl-aira-{uuid.uuid4().hex[:12]}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model,
                "system_fingerprint": "fp_aira_sovereign_v36",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": completion_text
                        },
                        "logprobs": None,
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": len(full_prompt.split()),
                    "completion_tokens": len(completion_text.split()),
                    "total_tokens": len(full_prompt.split()) + len(completion_text.split())
                }
            }

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(response_payload, indent=2, ensure_ascii=False).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

def run_server():
    server = ThreadingHTTPServer((HOST, PORT), AiraAPIHandler)
    print(f"\n" + "="*60)
    print(f"🚀 AIRA API GATEWAY (v3.6 Sovereign)")
    print(f"Developed by Adam Eehan for Aira Group of Technology")
    print(f"="*60)
    print(f"📍 Server running at: http://{HOST}:{PORT}")
    print(f"📡 OpenAI Base URL : http://localhost:{PORT}/v1")
    print(f"🌐 Web Dashboard   : http://localhost:{PORT}/")
    print(f"🔒 Zero Rate Limits & Zero Dependencies Required")
    print(f"="*60 + "\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Aira Gateway stopped gracefully.")

if __name__ == "__main__":
    run_server()
