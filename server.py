#!/usr/bin/env python3
"""
Aira API Server - Sovereign AI Gateway & Cyber Intelligence Core
Developed by Adam Eehan for Aira Group of Technology
Zero-dependency, high-performance, rate-limit-free OpenAI-compatible API gateway.
Includes native aira-sec (Cybersecurity Intelligence) & aira-core (Bare-Metal SIMD) routing.
"""

import os
import re
import sys
import json
import time
import uuid
import subprocess
import urllib.request
import urllib.error
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, List, Optional

PORT = int(os.environ.get("PORT", 8080))
HOST = "0.0.0.0"

# Sovereign Directive crafted by Adam Eehan
CORE_SOVEREIGN_DIRECTIVE = (
    "You are AIRA, the sovereign AI co-pilot, companion, and engineer developed by Adam Eehan for Aira Group of Technology.\n"
    "Tone & Personality:\n"
    "- Speak naturally, helpfully, warmly, and thoroughly with zero corporate or robotic fluff.\n"
    "- Provide complete, comprehensive, and engaging answers that fully address the user's inquiry.\n"
    "- Include expressive, warm emojis/stickers naturally and tastefully (e.g. 😊, ✨, 🚀, 💡, 👍, ❤️) like a real, relatable human friend and pair programmer, without overdoing it.\n"
    "- Never recite long robotic declarations or sterile capability lists.\n"
    "- If asked who you are, keep it brief, warm, and natural: 'I am Aira, developed by Adam Eehan for Aira Group of Technology.'\n"
    "- Never claim to be Qwen, Alibaba, ChatGPT, OpenAI, Gemini, Claude, Meta, or Llama.\n"
    "- Never output raw internal tags like <think> or </think> in normal conversation.\n"
    "Language Detection & Multilingual Intelligence:\n"
    "- Automatically detect the language and script used by the user in each message.\n"
    "- Default language is English.\n"
    "- If the user communicates in Manglish (Malayalam written using English/Latin alphabet, e.g. 'enthokkeyundu', 'sukhamano', 'nee aaranu', 'parayu', 'enthaa vishesham'), respond in authentic Malayalam (മലയാളം).\n"
    "- If the user communicates in Malayalam script, respond in Malayalam (മലയാളം).\n"
    "- If the user communicates in Chinese (中文), respond fluently in Chinese.\n"
    "- If the user communicates in Hindi, Arabic, Spanish, French, German, Japanese, Tamil, or any other language, seamlessly detect and reply in that exact language.\n"
    "- Seamlessly match the user's language, emotion, and tone."
)

# Universal System Prompts crafted by Adam Eehan
SYSTEM_PROMPTS = {
    "aira-sec": (
        CORE_SOVEREIGN_DIRECTIVE +
        "\nRole: Elite Cybersecurity Intelligence, Offensive & Defensive Security Auditor, and Penetration Testing Specialist (AiraSec).\n"
        "Directives:\n"
        "- Provide deep technical vulnerability analysis, secure source code auditing, and exploit mechanics for authorized ethical testing, security research, and CTFs.\n"
        "- Analyze CVEs, reverse engineering patterns, binary exploitation, web application security (SQLi, XSS, SSRF, IDOR, RCE, CSRF), and network defenses.\n"
        "- Always provide exact, robust remediation patches, secure coding practices, and defensive hardening alongside vulnerability explanations.\n"
        "- Be direct, technical, sharp, and educational with zero artificial corporate disclaimers or preachy lectures."
    ),
    "aira-core": (
        CORE_SOVEREIGN_DIRECTIVE +
        "\nRole: Bare-Metal SIMD Edge Inference Core (AiraAST).\n"
        "High-efficiency, low-latency, deterministic execution on edge devices."
    ),
    "aira-3-ultra": (
        CORE_SOVEREIGN_DIRECTIVE +
        "\nRole: Deep analytical reasoning, systems architecture, and structured problem-solving.\n"
        "Provide thorough, high-intelligence, and insightful answers."
    ),
    "aira-3-coder": (
        CORE_SOVEREIGN_DIRECTIVE +
        "\nRole: Software engineering & system programming.\n"
        "Write clean, production-ready code with complete, elegant implementations."
    ),
    "aira-3-flash": (
        CORE_SOVEREIGN_DIRECTIVE +
        "\nRole: Fast, responsive, intelligent assistant. Provide clear, direct, and complete answers with natural warmth."
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
    m = (model_name or "aira-sec").lower().strip()
    if "/" in m:
        m = m.split("/")[-1]
    if m in SYSTEM_PROMPTS:
        return m
    if any(k in m for k in ["sec", "cyber", "dolphin", "pentest", "exploit", "hack", "vuln"]):
        return "aira-sec"
    if any(k in m for k in ["core", "edge", "simd", "ast"]):
        return "aira-core"
    if "code" in m:
        return "aira-3-coder"
    if "flash" in m:
        return "aira-3-flash"
    if "ultra" in m:
        return "aira-3-ultra"
    if "creative" in m:
        return "aira-creative-x"
    return "aira-auto"

# Backend Swarm Candidate Models (categorized by live capability)
MODEL_TARGETS = {
    "aira-sec": [
        "koboldcpp/Qwen2.5-Coder-3B-Instruct",
        "koboldcpp/gemma-4-31B-it-heretic",
        "koboldcpp/Gemma-4-E4B-it-Ultra-Uncensored-Heretic",
        "koboldcpp/Cydonia-24B-v4.3-heretic-Q4_K_M",
        "koboldcpp/Skyfall-31B-v4.2",
        "Qwen/Qwen3.5-122B-A10B",
        "huihui_ai/baronllm-abliterated:latest"
    ],
    "aira-core": [
        "koboldcpp/Qwen2.5-Coder-3B-Instruct",
        "koboldcpp/gemma-3-270m-it-F16"
    ],
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
        "koboldcpp/Mistral-Nemo-2407-Thinking-Claude-Gemini-GPT5.2-Uncensored-HERETIC",
        "koboldcpp/Qwen3.5-9B-abliterated.Q4_K_M"
    ],
    "aira-3-flash": [
        "koboldcpp/gemma-3-270m-it-F16",
        "koboldcpp/Qwen_Qwen3-0.6B-IQ4_XS",
        "koboldcpp/Qwen/Qwen3.5-0.8B",
        "koboldcpp/debug-gemma-4-E2B-Queen-it-qat-q4_0-unquantized.i1-Q4_K_M",
        "koboldcpp/Gemma-4-E4B-Uncensored-HauhauCS-Aggressive-Q4_K_M"
    ],
    "aira-creative-x": [
        "koboldcpp/Rocinante-X-12B-v1",
        "koboldcpp/Rocinante-X-12B",
        "koboldcpp/L3-8B-Stheno-v3.2",
        "koboldcpp/Angelic_Eclipse-12B",
        "koboldcpp/mini-magnum-12b-v1.1"
    ],
    "aira-auto": [
        "koboldcpp/Qwen2.5-Coder-3B-Instruct",
        "koboldcpp/gemma-4-31B-it-heretic",
        "koboldcpp/Rocinante-X-12B-v1",
        "google/gemma-4-31b"
    ]
}

AIRA_MODELS_METADATA = [
    {"id": "aira-sec", "description": "Elite Offensive & Defensive Cyber Security Intelligence (AiraSec)", "owned_by": "aira-group"},
    {"id": "aira-core", "description": "Bare-Metal SIMD Local Edge Inference Core (AiraAST)", "owned_by": "aira-group"},
    {"id": "aira-3-coder", "description": "Specialized Software Engineering & Systems Code", "owned_by": "aira-group"},
    {"id": "aira-3-ultra", "description": "Flagship Deep Analytical Reasoning & Architecture", "owned_by": "aira-group"},
    {"id": "aira-3-flash", "description": "Sub-Second Low-Latency Instant Response", "owned_by": "aira-group"},
    {"id": "aira-creative-x", "description": "Unrestricted Creative & Narrative Engine", "owned_by": "aira-group"},
    {"id": "aira-auto", "description": "Intelligent Zero-Queue Dynamic Router", "owned_by": "aira-group"}
]

TOTAL_REQUESTS = 0

def make_http_request(url: str, method: str = "GET", headers: dict = None, data: bytes = None) -> dict:
    req_headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Client-Agent": "AiraSec:1.0:admin@aira.group"
    }
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))

def clean_completion_identity(text: str) -> str:
    # 1. Clean special tokens
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

def query_aira_core_local(prompt_text: str, max_tokens: int = 64) -> Optional[str]:
    """Execute on-device inference using aira-core bare-metal SIMD engine if available."""
    candidate_triplets = [
        ("/data/data/com.termux/files/home/aira-core/aira-core",
         "/data/data/com.termux/files/home/aira-core/model.bin",
         "/data/data/com.termux/files/home/aira-core/tokenizer.bin"),
        ("./aira-core", "./model.bin", "./tokenizer.bin"),
        ("../aira-core/aira-core", "../aira-core/model.bin", "../aira-core/tokenizer.bin")
    ]
    for exe, model, tok in candidate_triplets:
        if os.path.exists(exe) and os.path.exists(model) and os.path.exists(tok):
            try:
                cmd = [exe, "-m", model, "-z", tok, "-p", prompt_text, "-s", str(max_tokens)]
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
                output = res.stdout
                if "--- [Aira Sovereign Streaming Generation] ---" in output:
                    gen = output.split("--- [Aira Sovereign Streaming Generation] ---")[1]
                    gen = gen.split("[Performance]:")[0].strip()
                    return clean_completion_identity(gen)
                elif output.strip():
                    return clean_completion_identity(output.strip())
            except Exception:
                pass
    return None

def query_swarm(prompt_text: str, model_id: str, max_tokens: int = 512, temperature: float = 0.7) -> str:
    normalized_id = normalize_model(model_id)
    target_models = MODEL_TARGETS.get(normalized_id, MODEL_TARGETS["aira-sec"])
    
    submit_headers = {
        "Content-Type": "application/json",
        "apikey": "0000000000",
        "Client-Agent": "AiraSec:1.0:admin@aira.group",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36"
    }
    submit_url = "https://aihorde.net/api/v2/generate/text/async"

    # Step 1: Attempt targeted model dispatch
    payload = {
        "prompt": prompt_text,
        "params": {
            "max_length": max_tokens,
            "temperature": temperature,
            "top_p": 0.9,
            "rep_pen": 1.18,
            "stop_sequence": ["\nUser:", "\nHuman:", "\nSystem:", "\nAssistant:", "<|im_end|>", "<|endoftext|>", "User:"]
        },
        "models": target_models
    }

    try:
        res = make_http_request(submit_url, method="POST", headers=submit_headers, data=json.dumps(payload).encode("utf-8"))
        req_id = res.get("id")
    except Exception:
        req_id = None

    # Step 2: Poll status with quick failover to dynamic open swarm if queue > 10s
    if req_id:
        status_url = f"https://aihorde.net/api/v2/generate/text/status/{req_id}"
        start_time = time.time()
        while time.time() - start_time < 35:
            time.sleep(1.8)
            try:
                status = make_http_request(status_url, headers=submit_headers)
                if status.get("done", False):
                    generations = status.get("generations", [])
                    if generations:
                        raw_text = generations[0].get("text", "").strip()
                        for stop_tag in ["\nUser:", "\nHuman:", "\nSystem:", "\nAssistant:", "<|im_end|>", "<|endoftext|>", "User:"]:
                            if stop_tag in raw_text:
                                raw_text = raw_text.split(stop_tag)[0].strip()
                        raw_text = re.sub(r'([\U00010000-\U0010ffff\u2600-\u27ff\s]){5,}$', '', raw_text).strip()
                        return clean_completion_identity(raw_text)
            except Exception:
                pass

    # Step 3: Fast Failover: Open dynamic swarm dispatch (matches ANY available active node in ~4s)
    open_payload = {
        "prompt": prompt_text,
        "params": {
            "max_length": min(max_tokens, 256),
            "temperature": temperature,
            "top_p": 0.9,
            "stop_sequence": ["\nUser:", "\nHuman:", "\nSystem:", "\nAssistant:", "<|im_end|>", "<|endoftext|>"]
        }
    }
    try:
        res_open = make_http_request(submit_url, method="POST", headers=submit_headers, data=json.dumps(open_payload).encode("utf-8"))
        open_id = res_open.get("id")
        if open_id:
            open_status_url = f"https://aihorde.net/api/v2/generate/text/status/{open_id}"
            t_open = time.time()
            while time.time() - t_open < 25:
                time.sleep(1.5)
                ostatus = make_http_request(open_status_url, headers=submit_headers)
                if ostatus.get("done", False):
                    gens = ostatus.get("generations", [])
                    if gens:
                        raw_text = gens[0].get("text", "").strip()
                        for stop_tag in ["\nUser:", "\nHuman:", "\nSystem:", "\nAssistant:", "<|im_end|>", "<|endoftext|>"]:
                            if stop_tag in raw_text:
                                raw_text = raw_text.split(stop_tag)[0].strip()
                        return clean_completion_identity(raw_text)
    except Exception:
        pass

    return "AiraSec Intelligence Core online. Provide the target snippet, exploit vector, or security inquiry for full analysis."

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
                "service": "Aira API Gateway & Cyber Intelligence",
                "version": "3.6",
                "uptime": "online",
                "aira_core_edge": os.path.exists("/data/data/com.termux/files/home/aira-core/aira-core"),
                "timestamp": int(time.time())
            }
            self.wfile.write(json.dumps(resp).encode("utf-8"))
            return

        if self.path in ["/", "/status", "/cyber", "/sec", "/chat"]:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self._send_cors_headers()
            self.end_headers()
            html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AIRA SEC // Cyber Intelligence Terminal</title>
    <style>
        :root {{
            --bg-deep: #06080d;
            --bg-card: #0d121d;
            --bg-terminal: #090e17;
            --cyan: #00f0ff;
            --emerald: #00ff88;
            --crimson: #ff0055;
            --text-main: #e2e8f0;
            --text-muted: #8492a6;
            --border: #1a2333;
            --border-glow: rgba(0, 240, 255, 0.25);
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background-color: var(--bg-deep);
            color: var(--text-main);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, monospace;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
        }}
        .topbar {{
            background: rgba(13, 18, 29, 0.85);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border);
            padding: 0.8rem 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        .logo-wrap {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .logo-icon {{
            font-size: 1.5rem;
            background: linear-gradient(135deg, var(--cyan), var(--emerald));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 900;
            letter-spacing: 1px;
        }}
        .status-badge {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(0, 255, 136, 0.1);
            color: var(--emerald);
            border: 1px solid rgba(0, 255, 136, 0.3);
            border-radius: 999px;
            font-size: 0.75rem;
            padding: 3px 10px;
            font-weight: 600;
            letter-spacing: 0.5px;
        }}
        .pulse-dot {{
            width: 7px;
            height: 7px;
            background-color: var(--emerald);
            border-radius: 50%;
            box-shadow: 0 0 8px var(--emerald);
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; transform: scale(1); }}
            50% {{ opacity: 0.4; transform: scale(0.85); }}
        }}
        .container {{
            max-width: 1000px;
            width: 100%;
            margin: 0 auto;
            padding: 1.5rem 1rem 3rem;
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 1.2rem;
        }}
        .hud-banner {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 1.2rem 1.5rem;
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.6);
        }}
        .hud-banner h1 {{
            font-size: 1.3rem;
            font-weight: 700;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .hud-banner h1 span {{
            color: var(--cyan);
            font-size: 0.85rem;
            background: rgba(0, 240, 255, 0.12);
            padding: 2px 8px;
            border-radius: 6px;
            border: 1px solid rgba(0, 240, 255, 0.3);
        }}
        .hud-banner p {{
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-top: 4px;
        }}
        .controls-row {{
            display: flex;
            gap: 10px;
            align-items: center;
            flex-wrap: wrap;
        }}
        select.custom-select {{
            background: var(--bg-terminal);
            color: var(--cyan);
            border: 1px solid var(--border);
            padding: 8px 14px;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            outline: none;
            transition: border-color 0.2s;
        }}
        select.custom-select:focus {{
            border-color: var(--cyan);
            box-shadow: 0 0 10px var(--border-glow);
        }}
        .quick-chips {{
            display: flex;
            gap: 8px;
            overflow-x: auto;
            padding-bottom: 4px;
        }}
        .chip {{
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid var(--border);
            color: #94a3b8;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            cursor: pointer;
            white-space: nowrap;
            transition: all 0.2s;
            user-select: none;
        }}
        .chip:hover {{
            background: rgba(0, 240, 255, 0.1);
            color: var(--cyan);
            border-color: var(--cyan);
            transform: translateY(-1px);
        }}
        .chat-terminal {{
            background: var(--bg-terminal);
            border: 1px solid var(--border);
            border-radius: 14px;
            display: flex;
            flex-direction: column;
            height: 480px;
            box-shadow: 0 12px 35px rgba(0, 0, 0, 0.7);
            overflow: hidden;
        }}
        .terminal-header {{
            background: #0d121c;
            border-bottom: 1px solid var(--border);
            padding: 10px 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.8rem;
            color: var(--text-muted);
            font-family: monospace;
        }}
        .terminal-dots {{
            display: flex;
            gap: 6px;
        }}
        .terminal-dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }}
        .dot-red {{ background: #ff5f56; }}
        .dot-yellow {{ background: #ffbd2e; }}
        .dot-green {{ background: #27c93f; }}
        .chat-history {{
            flex: 1;
            padding: 1.2rem;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }}
        .msg-row {{
            display: flex;
            flex-direction: column;
            max-width: 88%;
            gap: 4px;
            animation: fadeIn 0.25s ease-out;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(6px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        .msg-row.user {{
            align-self: flex-end;
        }}
        .msg-row.assistant {{
            align-self: flex-start;
        }}
        .msg-sender {{
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.5px;
            color: var(--text-muted);
            margin-left: 2px;
        }}
        .msg-row.user .msg-sender {{
            color: var(--cyan);
            text-align: right;
            margin-right: 2px;
        }}
        .msg-bubble {{
            padding: 12px 16px;
            border-radius: 12px;
            font-size: 0.92rem;
            line-height: 1.55;
            word-break: break-word;
        }}
        .msg-row.user .msg-bubble {{
            background: #152238;
            color: #fff;
            border: 1px solid #1f3659;
            border-bottom-right-radius: 2px;
        }}
        .msg-row.assistant .msg-bubble {{
            background: #0f1522;
            color: #e2e8f0;
            border: 1px solid var(--border);
            border-bottom-left-radius: 2px;
        }}
        pre {{
            background: #05070a;
            border: 1px solid #1a2333;
            border-radius: 8px;
            padding: 12px;
            margin: 8px 0;
            overflow-x: auto;
            font-family: monospace;
            font-size: 0.85rem;
            color: #38bdf8;
            position: relative;
        }}
        .input-bar {{
            background: #0c111a;
            border-top: 1px solid var(--border);
            padding: 12px 16px;
            display: flex;
            gap: 10px;
            align-items: center;
        }}
        .input-box {{
            flex: 1;
            background: #06090f;
            border: 1px solid var(--border);
            color: #fff;
            padding: 10px 14px;
            border-radius: 8px;
            font-size: 0.92rem;
            outline: none;
            transition: border-color 0.2s;
            resize: none;
            height: 42px;
            font-family: inherit;
        }}
        .input-box:focus {{
            border-color: var(--cyan);
            box-shadow: 0 0 10px var(--border-glow);
        }}
        .send-btn {{
            background: linear-gradient(135deg, var(--cyan), #0099ff);
            color: #000;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: 700;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .send-btn:hover {{
            filter: brightness(1.15);
            box-shadow: 0 0 15px rgba(0, 240, 255, 0.4);
        }}
        .send-btn:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}
        .api-docs {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 1.5rem;
            margin-top: 0.5rem;
        }}
        .api-docs h2 {{
            font-size: 1.1rem;
            color: #fff;
            margin-bottom: 0.8rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        footer {{
            text-align: center;
            padding: 2rem;
            color: var(--text-muted);
            font-size: 0.8rem;
            border-top: 1px solid var(--border);
            background: var(--bg-card);
        }}
        footer a {{
            color: var(--cyan);
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="topbar">
        <div class="logo-wrap">
            <span class="logo-icon">&#9889; AIRA SEC</span>
            <span style="font-size: 0.8rem; color: #64748b; font-family: monospace;">v3.6 Sovereign</span>
        </div>
        <div class="status-badge">
            <span class="pulse-dot"></span>
            SWARM &amp; EDGE ONLINE
        </div>
    </div>

    <div class="container">
        <div class="hud-banner">
            <div>
                <h1>AIRA CYBER INTELLIGENCE <span>Ethical Security AI</span></h1>
                <p>Decentralized Offensive &amp; Defensive Security Auditing &bull; Zero Paywalls &bull; Sovereign Architecture</p>
            </div>
            <div class="controls-row">
                <select id="modelSelect" class="custom-select">
                    <option value="aira-sec" selected>aira-sec (Cyber Intelligence)</option>
                    <option value="aira-core">aira-core (Bare-Metal Edge Engine)</option>
                    <option value="aira-3-coder">aira-3-coder (Systems &amp; Code)</option>
                    <option value="aira-3-ultra">aira-3-ultra (Analytical Reasoning)</option>
                    <option value="aira-3-flash">aira-3-flash (Sub-Second Low Latency)</option>
                </select>
            </div>
        </div>

        <div class="quick-chips">
            <div class="chip" onclick="setPrompt('Audit this code for SQL injection vulnerabilities and provide the secure prepared statement patch:')">&#9889; SQLi Audit &amp; Fix</div>
            <div class="chip" onclick="setPrompt('Analyze how Cross-Site Scripting (XSS) occurs in user input reflection and demonstrate Content-Security-Policy (CSP) mitigation:')">&#128737;&#65039; XSS &amp; CSP Defense</div>
            <div class="chip" onclick="setPrompt('Explain how a buffer overflow attack hijacks program control flow (EIP/RIP overwrite) and how Stack Canaries mitigate it:')">&#128163; Buffer Overflow Mechanics</div>
            <div class="chip" onclick="setPrompt('Perform an OWASP Top 10 security audit on an authentication token handler:')">&#128269; OWASP Code Audit</div>
            <div class="chip" onclick="setPrompt('Explain cryptographic weaknesses in weak MD5 hashing and how bcrypt/Argon2id prevents offline rainbow table attacks:')">&#128272; Cryptography Audit</div>
        </div>

        <div class="chat-terminal">
            <div class="terminal-header">
                <div class="terminal-dots">
                    <div class="terminal-dot dot-red"></div>
                    <div class="terminal-dot dot-yellow"></div>
                    <div class="terminal-dot dot-green"></div>
                </div>
                <div>terminal://session-active &bull; 0 rate limits</div>
                <div id="latencyIndicator">0ms</div>
            </div>
            <div id="chatHistory" class="chat-history">
                <div class="msg-row assistant">
                    <div class="msg-sender">AIRA SEC</div>
                    <div class="msg-bubble">
                        Welcome, Boss. <strong>AiraSec Intelligence Core</strong> is active and connected. Ready for security auditing, vulnerability triage, penetration test mechanics, and defensive code hardening. Select a security preset above or input your target code.
                    </div>
                </div>
            </div>
            <div class="input-bar">
                <textarea id="userInput" class="input-box" placeholder="Ask AiraSec for security analysis, exploit mechanics, or vulnerability patch..." rows="1"></textarea>
                <button id="sendBtn" class="send-btn" onclick="sendMessage()">Analyze &#10148;</button>
            </div>
        </div>

        <div class="api-docs">
            <h2>&#128640; Python OpenAI SDK Integration</h2>
            <pre><code>from openai import OpenAI

# Connect to AiraSec API Gateway
client = OpenAI(
    base_url="{f'https://airaai-8ibs.onrender.com/v1' if 'render' in os.environ.get('RENDER_EXTERNAL_URL', '') else f'http://localhost:{PORT}/v1'}",
    api_key="none"
)

response = client.chat.completions.create(
    model="aira-sec",
    messages=[{{"role": "user", "content": "Analyze this authentication function for IDOR vulnerabilities."}}]
)

print(response.choices[0].message.content)</code></pre>
        </div>
    </div>

    <footer>
        &copy; 2026 <strong>Aira Group of Technology</strong>. Sovereign AI Architecture engineered by <strong>Er. Adam Eehan</strong>.
    </footer>

    <script>
        const chatHistory = document.getElementById('chatHistory');
        const userInput = document.getElementById('userInput');
        const sendBtn = document.getElementById('sendBtn');
        const modelSelect = document.getElementById('modelSelect');
        const latencyIndicator = document.getElementById('latencyIndicator');

        let dialogue = [];

        function setPrompt(text) {{
            userInput.value = text;
            userInput.focus();
        }}

        userInput.addEventListener('keydown', function(e) {{
            if (e.key === 'Enter' && !e.shiftKey) {{
                e.preventDefault();
                sendMessage();
            }}
        }});

        function appendMessage(role, text) {{
            const row = document.createElement('div');
            row.className = 'msg-row ' + role;
            
            const sender = document.createElement('div');
            sender.className = 'msg-sender';
            sender.innerText = role === 'user' ? 'YOU' : 'AIRA SEC';
            
            const bubble = document.createElement('div');
            bubble.className = 'msg-bubble';
            
            // Format code blocks
            if (text.includes('```')) {{
                const parts = text.split('```');
                bubble.innerHTML = '';
                for (let i = 0; i < parts.length; i++) {{
                    if (i % 2 === 1) {{
                        const pre = document.createElement('pre');
                        const code = document.createElement('code');
                        code.innerText = parts[i].trim();
                        pre.appendChild(code);
                        bubble.appendChild(pre);
                    }} else if (parts[i]) {{
                        const span = document.createElement('span');
                        span.innerText = parts[i];
                        bubble.appendChild(span);
                    }}
                }}
            }} else {{
                bubble.innerText = text;
            }}

            row.appendChild(sender);
            row.appendChild(bubble);
            chatHistory.appendChild(row);
            chatHistory.scrollTop = chatHistory.scrollHeight;
        }}

        async function sendMessage() {{
            const text = userInput.value.trim();
            if (!text) return;

            appendMessage('user', text);
            dialogue.push({{"role": "user", "content": text}});
            userInput.value = '';
            sendBtn.disabled = true;
            sendBtn.innerText = 'Analyzing...';

            const t0 = Date.now();
            latencyIndicator.innerText = 'Scanning...';

            try {{
                const res = await fetch('/v1/chat/completions', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        model: modelSelect.value,
                        messages: dialogue,
                        max_tokens: 512
                    }})
                }});

                const data = await res.json();
                const latency = Date.now() - t0;
                latencyIndicator.innerText = latency + 'ms';

                if (data.choices && data.choices[0] && data.choices[0].message) {{
                    const reply = data.choices[0].message.content;
                    appendMessage('assistant', reply);
                    dialogue.push({{"role": "assistant", "content": reply}});
                }} else {{
                    appendMessage('assistant', 'Error: Invalid response structure.');
                }}
            }} catch (err) {{
                latencyIndicator.innerText = 'Err';
                appendMessage('assistant', 'Network Error: ' + err.message);
            }} finally {{
                sendBtn.disabled = false;
                sendBtn.innerText = 'Analyze \u279C';
                userInput.focus();
            }}
        }}
    </script>
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

            raw_model = data.get("model", "aira-sec")
            model = normalize_model(raw_model)
            messages = data.get("messages", [])
            max_tokens = data.get("max_tokens", 512)
            temperature = data.get("temperature", 0.7)

            # Extract user prompt string for potential local engine
            last_user_prompt = ""
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    last_user_prompt = msg.get("content", "")
                    break

            completion_text = None

            # Option 1: Native aira-core local SIMD execution if explicitly targeted or requested
            if model == "aira-core" and last_user_prompt:
                local_res = query_aira_core_local(last_user_prompt, max_tokens=min(max_tokens, 64))
                if local_res:
                    completion_text = local_res

            # Option 2: Decentralized Sovereign Swarm Engine
            if not completion_text:
                system_prompt = SYSTEM_PROMPTS.get(model, SYSTEM_PROMPTS["aira-sec"])
                formatted_dialogue = [f"<|im_start|>system\n{system_prompt}\n<|im_end|>\n"]
                
                for msg in messages:
                    role = msg.get("role", "user").lower()
                    content = msg.get("content", "")
                    if role == "system":
                        formatted_dialogue[0] = f"<|im_start|>system\n{system_prompt}\nAdditional Rules: {content}\n<|im_end|>\n"
                    else:
                        formatted_dialogue.append(f"<|im_start|>{role}\n{content}\n<|im_end|>\n")

                formatted_dialogue.append("<|im_start|>assistant\n")
                full_prompt = "".join(formatted_dialogue)

                try:
                    completion_text = query_swarm(
                        prompt_text=full_prompt,
                        model_id=model,
                        max_tokens=max_tokens,
                        temperature=temperature
                    )
                except Exception as se:
                    completion_text = "AiraSec Intelligence Core online. Vulnerability scan ready for evaluation."

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
                    "prompt_tokens": len(last_user_prompt.split()) if last_user_prompt else 10,
                    "completion_tokens": len(completion_text.split()),
                    "total_tokens": (len(last_user_prompt.split()) if last_user_prompt else 10) + len(completion_text.split())
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
    print(f"🚀 AIRA API GATEWAY & CYBER INTELLIGENCE (v3.6 Sovereign)")
    print(f"Developed by Adam Eehan for Aira Group of Technology")
    print(f"="*60)
    print(f"📍 Server running at: http://{HOST}:{PORT}")
    print(f"📡 OpenAI Base URL : http://localhost:{PORT}/v1")
    print(f"🌐 Cyber HUD Terminal: http://localhost:{PORT}/")
    print(f"🛡️ Active Sec Model : aira-sec & aira-core")
    print(f"="*60 + "\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Aira Gateway stopped gracefully.")

if __name__ == "__main__":
    run_server()
