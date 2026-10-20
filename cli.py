#!/usr/bin/env python3
"""
Aira Interactive CLI Chat
Developed by Adam Eehan for Aira Group of Technology
Zero-dependency command-line interface for Aira models.
"""

import sys
import json
import urllib.request
import urllib.error

SERVER_URL = "http://localhost:8080/v1/chat/completions"

def main():
    print("\n" + "="*50)
    print("🤖 AIRA AI INTERACTIVE TERMINAL")
    print("Developed by Adam Eehan for Aira Group of Technology")
    print("="*50)
    print("Models: aira-3-coder, aira-3-ultra, aira-3-flash, aira-creative-x, aira-auto")
    print("Type 'exit' or 'quit' to close.\n")

    model = "aira-3-coder"
    if len(sys.argv) > 1:
        model = sys.argv[1]
    
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
                SERVER_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )

            print("\033[1;33m[Aira is thinking...]\033[0m", end="\r", flush=True)

            with urllib.request.urlopen(req, timeout=90) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                reply = data["choices"][0]["message"]["content"]
                history.append({"role": "assistant", "content": reply})
                print(" " * 30, end="\r") # Clear thinking line
                print(f"\033[1;32mAira > \033[0m{reply}\n")

        except KeyboardInterrupt:
            print("\nSession ended.")
            break
        except urllib.error.URLError:
            print("\n❌ Error: Cannot connect to Aira Server at http://localhost:8080.")
            print("👉 Run 'python server.py' in another terminal window first!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")

if __name__ == "__main__":
    main()
