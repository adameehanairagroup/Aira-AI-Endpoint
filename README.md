# 🚀 AIRA GROUP AI & CYBER INTELLIGENCE — FREE API ACCESS FOR DEVELOPERS

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8+-green.svg)](https://python.org)
[![Dependencies: 0](https://img.shields.io/badge/Dependencies-Zero-brightgreen.svg)]()
[![Status: Sovereign](https://img.shields.io/badge/Status-Active-purple.svg)]()
[![Cybersecurity: AiraSec](https://img.shields.io/badge/CyberSec-AiraSec--Core-red.svg)]()
[![Rate-Limit: None](https://img.shields.io/badge/Rate--Limit-Bypassed-success.svg)]()

> **Engineered by Er. Adam Eehan (Founder & CEO, Aira Group of Technology)**  
> High-performance, zero-dependency, 100% rate-limit-free OpenAI-compatible API gateway and cybersecurity model suite for developers & security researchers worldwide.

---

## 🌟 Why Aira API & AiraSec?

Tired of paying $20/month for AI subscriptions, hitting `429 Too Many Requests` rate limits, or corporate models refusing to analyze exploit mechanics during ethical security research?

**Aira API & AiraSec** is an open-source, sovereign AI gateway that provides drop-in OpenAI-compatible API access without needing paid API keys, credit cards, or complex setups.

* 🛡️ **AiraSec Cyber Intelligence:** Tuned for offensive & defensive cybersecurity, vulnerability auditing, CVE analysis, reverse engineering, and automated remediation without preachy corporate disclaimers.
* ⚡ **Zero Dependencies:** Pure vanilla Python 3 standard library. No `pip install` required!
* 🔓 **Zero Rate Limits:** Unlimited throughput backed by decentralized compute swarms.
* 🚀 **aira-core Native SIMD Edge Bridge:** Direct integration with our bare-metal C99 ARM NEON / AVX2 inference engine for sub-millisecond edge execution.
* 🔄 **OpenAI Drop-In Compatible:** Works directly with the official OpenAI SDK, LangChain, Cursor, VS Code, and cURL.
* 💻 **Cyber HUD Web Terminal:** Built-in futuristic dark cyber HUD interface served directly at `/`.

---

## 📦 Available Model Lineup

| Model ID | Category | Description |
| :--- | :--- | :--- |
| `aira-sec` | 🛡️ **Cyber Intelligence** | Elite offensive & defensive security auditor, exploit mechanics analysis, CVE research, and secure patch creation. |
| `aira-core` | ⚡ **Bare-Metal SIMD Edge** | Native on-device C99 SIMD inference core (`AiraAST`) reaching 131+ tokens/second. |
| `aira-3-coder` | 💻 **Code Engineering** | Specialized for Python, JS, C, Rust, systems architecture, and debugging. |
| `aira-3-ultra` | 🧠 **Flagship Intelligence** | Deep analytical reasoning, multi-step problem solving, and architecture design. |
| `aira-3-flash` | ⚡ **Low Latency** | Instant sub-second responses for real-time interactions. |
| `aira-creative-x`| 🎨 **Creative & Narrative**| Unrestricted storytelling, creative prose, and roleplay. |
| `aira-auto` | 🎯 **Smart Router** | Intelligent dynamic router that routes to the fastest available worker with 0 wait queue. |

---

## 🚀 Quick Start (In 30 Seconds)

### 1. Public Cloud Endpoint (Instant Access)
The official cloud endpoint is live 24/7 on Render:
- **Base URL:** `https://airaai-8ibs.onrender.com/v1`
- **Web Terminal:** `https://airaai-8ibs.onrender.com/`

### 2. Local Self-Hosted Setup
```bash
git clone https://github.com/adameehanairagroup/Aira-AI-Endpoint.git
cd Aira-AI-Endpoint
python3 server.py
```

The gateway is now live on `http://localhost:8080/v1`! 

Open your browser to `http://localhost:8080` to access the **AiraSec Cyber Intelligence Terminal**.

---

## 🛡️ Python OpenAI SDK Integration

You can drop AiraSec directly into any existing Python application or security script:

```python
from openai import OpenAI

# Connect to AiraSec Cloud Gateway or Local Server
client = OpenAI(
    base_url="https://airaai-8ibs.onrender.com/v1",
    api_key="none"  # Zero keys needed!
)

response = client.chat.completions.create(
    model="aira-sec",
    messages=[
        {"role": "user", "content": "Audit this PHP login script for SQL injection and provide the secure PDO prepared statement fix."}
    ]
)

print(response.choices[0].message.content)
```

---

## 💻 Terminal cURL Usage

```bash
# Query AiraSec Cyber Model
curl -X POST https://airaai-8ibs.onrender.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "aira-sec",
    "messages": [
      {"role": "user", "content": "Explain how buffer overflows hijack execution flow and how ASLR/Canaries prevent it."}
    ]
  }'
```

---

## 🤖 Interactive CLI Terminal

Launch the interactive terminal chat tool:

```bash
# Chat with AiraSec locally
python3 cli.py aira-sec

# Or connect directly to Cloud Render Gateway
python3 cli.py --cloud aira-sec
```

---

## 🌐 Deploy Your Own Cyber Web HUD

A standalone single-page web interface is included in `web/index.html`. You can:
1. Double-click `web/index.html` to open it in any browser.
2. Deploy it in 1 click to GitHub Pages or Vercel.
3. It connects directly to `https://airaai-8ibs.onrender.com/v1/chat/completions` with zero backend configuration needed!

---

## 📜 License & Sovereign Guarantee

Released under the **MIT License**.  
Architected and engineered by **Er. Adam Eehan** for **Aira Group of Technology**. Sovereign, independent, and dedicated to empowering developers and cybersecurity researchers globally.
