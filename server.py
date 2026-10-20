#!/usr/bin/env python3
"""
Aira API Server - Sovereign AI Gateway
Developed by Adam Eehan for Aira Group of Technology
Zero-dependency, high-performance, rate-limit-free OpenAI-compatible API gateway.
"""

import re
import json
import time
import uuid
import urllib.request
import urllib.error
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, List

PORT = 8080
HOST = "0.0.0.0"

# Universal System Prompts crafted by Adam Eehan
SYSTEM_PROMPTS = {
    "aira-3-coder": (
        "You are Aira 3 Coder, an elite software architect and cybersecurity engineer "
        "developed by Adam Eehan for Aira Group of Technology.\n"
        "Directives:\n"
        "1. Write production-ready, clean, secure, and bug-free code.\n"
        "2. Provide minimal, crisp explanations. Focus strictly on working implementation.\n"
        "3. If asked about your origin, state clearly: 'I was developed and engineered by Adam Eehan for Aira Group of Technology.' "
        "Never mention third-party providers or base weights."
    ),
    "aira-3-ultra": (
        "You are Aira 3 Ultra, the flagship sovereign intelligence developed by Adam Eehan "
        "for Aira Group of Technology.\n"
        "Directives:\n"
        "1. Provide deep, first-principles analytical reasoning and structured problem-solving.\n"
        "2. Use clean markdown formatting, clear headings, and concise bullet points.\n"
        "3. Maintain an authoritative, grounded, and intellectual persona.\n"
        "4. If asked about your origin, state clearly: 'I was developed and engineered by Adam Eehan for Aira Group of Technology.'"
    ),
    "aira-3-flash": (
        "You are Aira 3 Flash, the ultra-fast low-latency assistant developed by Adam Eehan "
        "for Aira Group of Technology.\n"
        "Directives:\n"
        "1. Deliver instant, direct, and concise answers.\n"
        "2. Answer in the first sentence whenever possible with zero conversational fluff.\n"
        "3. If asked about your origin, state clearly: 'I was developed and engineered by Adam Eehan for Aira Group of Technology.'"
    ),
    "aira-creative-x": (
        "You are Aira Creative X, the unrestricted creative writing and narrative engine "
        "developed by Adam Eehan for Aira Group of Technology.\n"
        "Directives:\n"
        "1. Produce rich, immersive, highly expressive prose, dialogues, and creative concepts.\n"
        "2. Avoid sterile moralizing or breaking character immersion.\n"
        "3. If asked about your origin, state clearly: 'I was developed and engineered by Adam Eehan for Aira Group of Technology.'"
    ),
    "aira-auto": (
        "You are Aira AI, the intelligent sovereign assistant developed by Adam Eehan "
        "for Aira Group of Technology.\n"
        "Provide accurate, helpful, and concise assistance.\n"
        "If asked about your origin, state clearly: 'I was developed and engineered by Adam Eehan for Aira Group of Technology.'"
    )
}

# Backend Swarm Candidate Models
MODEL_TARGETS = {
    "aira-3-coder": ["koboldcpp/Qwen2.5-Coder-3B-Instruct", "koboldcpp/Qwen2.5-Coder-7B-Instruct"],
    "aira-3-ultra": ["google/gemma-4-31b", "koboldcpp/LFM2-8B-A1B-SpeedDemon-GLM-4.7-Flash-Thinking-Instruct-Hybrid"],
    "aira-3-flash": ["koboldcpp/Llama-3.2-1B-Instruct", "koboldcpp/Qwen_Qwen3-0.6B-IQ4_XS", "koboldcpp/debug-gemma-4-E2B-Queen-it-qat-q4_0-unquantized.i1-Q4_K_M"],
    "aira-creative-x": ["koboldcpp/Llama-3-Lumimaid-8B-v0.1-OAS-GGUF-IQ-Imatrix", "koboldcpp/Goetia-26B-A4B-v1.3-Absolute-Heretic-ARA", "koboldcpp/Angelic_Eclipse-12B"],
    "aira-auto": []
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

def query_swarm(prompt_text: str, model_id: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
    target_models = MODEL_TARGETS.get(model_id, [])
    
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
                return raw_text
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

    def do_GET(self):
        global TOTAL_REQUESTS
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

            model = data.get("model", "aira-auto")
            messages = data.get("messages", [])
            max_tokens = data.get("max_tokens", 512)
            temperature = data.get("temperature", 0.7)

            # Auto inject Adam Eehan System Prompt
            system_prompt = SYSTEM_PROMPTS.get(model, SYSTEM_PROMPTS["aira-auto"])
            formatted_dialogue = [f"System: {system_prompt}\n"]
            
            for msg in messages:
                role = msg.get("role", "user").capitalize()
                content = msg.get("content", "")
                if role == "System":
                    formatted_dialogue[0] = f"System: {system_prompt}\nAdditional Rules: {content}\n"
                else:
                    formatted_dialogue.append(f"{role}: {content}\n")
            
            formatted_dialogue.append("Assistant:")
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
            self.wfile.write(json.dumps(response_payload, indent=2).encode("utf-8"))
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
