#!/usr/bin/env python3
"""
Aira Interactive CLI Chat & Cyber Security Terminal
Developed by Adam Eehan for Aira Group of Technology
Zero-dependency command-line interface for Aira models.
"""

import sys
import json
import urllib.request
import urllib.error

DEFAULT_LOCAL_URL = "http://localhost:8080/v1/chat/completions"
DEFAULT_RENDER_URL = "https://airaai-8ibs.onrender.com/v1/chat/completions"

def main():
    print("\n" + "="*55)
    print("🤖 AIRA SEC & AI INTERACTIVE TERMINAL")
    print("Developed by Adam Eehan for Aira Group of Technology")
    print("="*55)
    print("Models: aira-sec, aira-core, aira-3-coder, aira-3-ultra, aira-3-flash")
    print("Flags : --cloud (route directly via live Render endpoint)")
    print("Type 'exit' or 'quit' to close.\n")

    server_url = DEFAULT_LOCAL_URL
    args = sys.argv[1:]
    if "--cloud" in args or "--render" in args:
        server_url = DEFAULT_RENDER_URL
        args = [a for a in args if a not in ["--cloud", "--render"]]

    model = "aira-sec"
    if args:
        model = "".join(args).strip()
    
    print(f"🎯 Gateway URL : {server_url}")
    print(f"⚡ Active Model: {model}\n")

    history = []

    while True:
        try:
            user_input = input("\033[1;36mYou > \033[0m").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break

            history.append({"role": "user", "content": user_input})

            payload = {
                "model": model,
                "messages": history,
                "max_tokens": 512
            }

            req = urllib.request.Request(
                server_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36"
                }
            )

            print("\033[1;33m[AiraSec is analyzing...]\033[0m", end="\r", flush=True)

            with urllib.request.urlopen(req, timeout=90) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                reply = data["choices"][0]["message"]["content"]
                history.append({"role": "assistant", "content": reply})
                print(" " * 30, end="\r") # Clear thinking line
                print(f"\033[1;32mAiraSec > \033[0m{reply}\n")

        except KeyboardInterrupt:
            print("\nSession ended.")
            break
        except urllib.error.URLError as ue:
            print(f"\n❌ Error: Cannot connect to Aira Server at {server_url}")
            if server_url == DEFAULT_LOCAL_URL:
                print("👉 Run 'python server.py' or use '--cloud' to query live Render endpoint!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")

if __name__ == "__main__":
    main()
