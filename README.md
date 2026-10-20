# 🚀 Aira API Gateway (v3.6 Sovereign)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8+-green.svg)](https://python.org)
[![Dependencies: 0](https://img.shields.io/badge/Dependencies-Zero-brightgreen.svg)]()
[![Status: Sovereign](https://img.shields.io/badge/Status-Active-purple.svg)]()
[![Rate-Limit: None](https://img.shields.io/badge/Rate--Limit-Bypassed-success.svg)]()

> **Engineered by Adam Eehan (Founder & CEO, Aira Group of Technology)**  
> High-performance, zero-dependency, 100% rate-limit-free OpenAI-compatible API gateway and model suite.

---

## 🌟 Why Aira API?

Tired of paying $20/month for AI subscriptions, hitting `429 Too Many Requests` rate limits, or having ephemeral cloud sessions disconnect after 30 minutes?

**Aira API** is an open-source, sovereign AI gateway that gives you instant, local, drop-in OpenAI-compatible API access without needing paid API keys, credit cards, or complex setups.

* ⚡ **Zero Dependencies:** Pure vanilla Python 3 standard library. No `pip install` required!
* 🔓 **Zero Rate Limits:** Unlimited throughput backed by decentralized compute swarms.
* 🔄 **OpenAI Drop-In Compatible:** Works directly with the official OpenAI SDK, LangChain, Cursor, VS Code, and cURL.
* 💻 **Built-in Web Dashboard:** Built-in dark bioluminescent web interface at `http://localhost:8080`.
* 🤖 **Tuned Model Lineup:** Specialized system prompts engineered by Adam Eehan for coding, deep reasoning, and high-speed chat.

---

## 📦 Available Model Lineup

| Model ID | Category | Description |
| :--- | :--- | :--- |
| `aira-3-coder` | 💻 **Code Engineering** | Specialized for Python, JS, C, Rust, debugging, and terminal automation. |
| `aira-3-ultra` | 🧠 **Flagship Intelligence** | Deep analytical reasoning, multi-step problem solving, and architecture design. |
| `aira-3-flash` | ⚡ **Low Latency** | Instant sub-second responses for real-time interactions. |
| `aira-creative-x`| 🎨 **Creative & Narrative**| Unrestricted storytelling, creative prose, and roleplay. |
| `aira-auto` | 🎯 **Smart Router** | Intelligent dynamic router that routes to the fastest available worker with 0 wait queue. |

---

## 🚀 Quick Start (In 30 Seconds)

### 1. Clone & Run the Server
```bash
git clone https://github.com/adameehan/Aira-AI-Endpoint.git
cd Aira-AI-Endpoint
python3 server.py
```

The gateway is now live on `http://localhost:8080/v1`! 

Open your browser to `http://localhost:8080` to view the live dashboard and system status.

---

### 2. Use with Python OpenAI SDK

You can drop Aira API directly into any existing Python application:

```python
from openai import OpenAI

# Point directly to your local Aira Gateway
client = OpenAI(
    base_url="http://localhost:8080/v1",
    api_key="none"  # No API key needed!
)

response = client.chat.completions.create(
    model="aira-3-coder",
    messages=[
        {"role": "user", "content": "Write a clean Python script to parse JSON logs with error handling."}
    ]
)

print(response.choices[0].message.content)
```

---

### 3. Use via cURL (Terminal / Bash)

```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "aira-3-coder",
    "messages": [
      {"role": "user", "content": "Explain how RSA encryption works in 3 bullet points."}
    ]
  }'
```

---

### 4. Interactive Terminal Chat

Launch the interactive terminal chat tool:

```bash
python3 cli.py aira-3-coder
```

---

## 🛠️ Architecture

```
┌────────────────────────────────────────────────────────┐
│     Client Applications (Cursor / Python / cURL)       │
└────────────────────────────────────────────────────────┘
                           │
                           ▼ (Standard OpenAI Format)
┌────────────────────────────────────────────────────────┐
│              AIRA SOVEREIGN API GATEWAY                │
│                 (http://localhost:8080)                │
│                                                        │
│  - Zero Dependencies (Pure Python Standard Library)    │
│  - Auto-Injected Adam Eehan System Prompts             │
│  - CORS Enabled for Local Web Frontends                │
│  - Multi-Threading Request Handler                    │
└────────────────────────────────────────────────────────┘
                           │
                           ▼ (Decentralized Compute Swarm)
┌────────────────────────────────────────────────────────┐
│            Distributed High-Capacity Cluster           │
│        (No Corporate Rate Limits / No Quota Caps)      │
└────────────────────────────────────────────────────────┘
```

---

## 🗺️ Roadmap

- [x] Zero-dependency pure Python server.
- [x] Standard OpenAI-compatible `/v1/chat/completions` and `/v1/models`.
- [x] Dedicated model personas (Coder, Ultra, Flash, Creative).
- [x] Built-in Web dashboard and interactive CLI.
- [ ] Multi-tenant personal endpoint routing (`/v1/{user_id}/chat`).
- [ ] 1-Click cloud deployment on Vercel & Render.

---

## 👤 Author & Creator

**Adam Eehan**  
Founder & CEO, **Aira Group of Technology**  
- Portfolio: [adameehan.vercel.app](https://adameehan.vercel.app)  
- GitHub: [@adameehan](https://github.com/adameehan)  

---

## 📄 License

This project is open-source under the [MIT License](LICENSE).  
Copyright &copy; 2026 Adam Eehan & Aira Group of Technology.
