"""
Sparky Small v4 - AI chatbot with a browser chat UI, powered by OpenRouter.

Setup:
    export OPENROUTER_API_KEY="sk-or-..."          # required (https://openrouter.ai/keys)
    export SPARKY_MODEL="meta-llama/llama-3.3-70b-instruct"   # optional

Run:
    python3 sparky_web.py
Then open http://localhost:8000 in your browser.

Single file, zero dependencies (Python standard library only).
"""

import json
import os
import sys
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
MODEL = os.environ.get("SPARKY_MODEL", "meta-llama/llama-3.3-70b-instruct")
PORT = int(os.environ.get("PORT", "8000"))

SYSTEM_PROMPT = "You are Sparky Small, a friendly, concise little chatbot. Keep replies short and warm."

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sparky Small</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: system-ui, -apple-system, sans-serif; background: #f4f4f5;
         display: flex; justify-content: center; min-height: 100vh; padding: 24px; }
  .app { width: 100%; max-width: 640px; display: flex; flex-direction: column;
         background: #fff; border: 1px solid #e4e4e7; border-radius: 16px;
         box-shadow: 0 4px 24px rgba(0,0,0,.06); overflow: hidden; height: calc(100vh - 48px); }
  header { padding: 16px 20px; border-bottom: 1px solid #e4e4e7; display: flex;
           align-items: center; justify-content: space-between; }
  header h1 { font-size: 18px; letter-spacing: -0.02em; }
  header .sub { font-size: 12px; color: #71717a; margin-top: 2px; }
  header button { font-size: 12px; padding: 6px 12px; border: 1px solid #e4e4e7;
           background: #fff; border-radius: 8px; cursor: pointer; }
  header button:hover { background: #f4f4f5; }
  #chat { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 12px; }
  .msg { max-width: 80%; padding: 10px 14px; border-radius: 14px; line-height: 1.45;
         font-size: 15px; white-space: pre-wrap; }
  .user { align-self: flex-end; background: #18181b; color: #fafafa; border-bottom-right-radius: 4px; }
  .bot { align-self: flex-start; background: #f4f4f5; color: #18181b;
         border: 1px solid #e4e4e7; border-bottom-left-radius: 4px; }
  .bot.thinking { color: #a1a1aa; font-style: italic; }
  form { display: flex; gap: 8px; padding: 14px; border-top: 1px solid #e4e4e7; }
  input { flex: 1; padding: 12px 14px; font-size: 15px; border: 1px solid #e4e4e7;
          border-radius: 10px; outline: none; }
  input:focus { border-color: #18181b; }
  button.send { padding: 12px 20px; font-size: 15px; background: #18181b; color: #fafafa;
          border: none; border-radius: 10px; cursor: pointer; }
  button.send:disabled { opacity: .5; cursor: default; }
</style>
</head>
<body>
<div class="app">
  <header>
    <div>
      <h1>⚡ Sparky Small</h1>
      <div class="sub">__MODEL__</div>
    </div>
    <button onclick="resetChat()">New chat</button>
  </header>
  <div id="chat"><div class="msg bot">Hey! I'm Sparky ⚡ Ask me anything.</div></div>
  <form id="form">
    <input id="input" placeholder="Type a message..." autocomplete="off" autofocus>
    <button class="send" id="send" type="submit">Send</button>
  </form>
</div>
<script>
let history = [];
const chat = document.getElementById('chat');
const form = document.getElementById('form');
const input = document.getElementById('input');
const sendBtn = document.getElementById('send');

function addMsg(text, cls) {
  const d = document.createElement('div');
  d.className = 'msg ' + cls;
  d.textContent = text;
  chat.appendChild(d);
  chat.scrollTop = chat.scrollHeight;
  return d;
}

function resetChat() {
  history = [];
  chat.innerHTML = '';
  addMsg("Hey! I'm Sparky ⚡ Ask me anything.", 'bot');
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  input.value = '';
  addMsg(text, 'user');
  history.push({role: 'user', content: text});
  sendBtn.disabled = true;
  const thinking = addMsg('Sparky is thinking...', 'bot thinking');
  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({messages: history})
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || 'Request failed');
    history.push({role: 'assistant', content: data.reply});
    thinking.remove();
    addMsg(data.reply, 'bot');
  } catch (err) {
    history.pop();
    thinking.remove();
    addMsg('⚠️ ' + err.message, 'bot');
  } finally {
    sendBtn.disabled = false;
    input.focus();
  }
});
</script>
</body>
</html>
"""


def call_llm(messages: list) -> str:
    payload = {
        "model": MODEL,
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
    }
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
            "HTTP-Referer": "https://fluso.ai",
            "X-Title": "Sparky Small",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"].strip()


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="text/html; charset=utf-8"):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, PAGE.replace("__MODEL__", MODEL))
        else:
            self._send(404, "Not found", "text/plain")

    def do_POST(self):
        if self.path != "/chat":
            self._send(404, "Not found", "text/plain")
            return
        try:
            n = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(n) or b"{}")
            messages = body.get("messages", [])
            if not isinstance(messages, list) or not messages:
                raise ValueError("No messages provided")
            reply = call_llm(messages)
            self._send(200, json.dumps({"reply": reply}), "application/json")
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:300]
            self._send(e.code, json.dumps({"error": f"OpenRouter error {e.code}: {detail}"}),
                       "application/json")
        except Exception as e:
            self._send(400, json.dumps({"error": str(e)}), "application/json")

    def log_message(self, fmt, *args):
        sys.stderr.write("[sparky] " + fmt % args + "\n")


def main():
    if not API_KEY:
        sys.exit(
            "No API key found.\n"
            "Grab your key from https://openrouter.ai/keys, then run:\n"
            '  export OPENROUTER_API_KEY="sk-or-your-key-here"\n'
            "  python3 sparky_web.py"
        )
    print(f"⚡ Sparky Small is live at http://localhost:{PORT}  (model: {MODEL})")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
