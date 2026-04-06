
from flask import Flask, request, jsonify, render_template_string
import requests
import os

app = Flask(__name__)

# 🔐 Secure API key
API_KEY = os.getenv("GROQ_API_KEY")

API_URL = "https://api.groq.com/openai/v1/chat/completions"

# 🧠 Memory (simple chat history)
chat_history = []

# 🎨 Premium ChatGPT-like UI
HTML_UI = """
<!DOCTYPE html>
<html>
<head>
<title>Jarvis AI</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<style>
body {
    margin: 0;
    font-family: Arial;
    background: #343541;
    color: white;
}

.chat-container {
    display: flex;
    flex-direction: column;
    height: 100vh;
}

.messages {
    flex: 1;
    overflow-y: auto;
    padding: 15px;
}

.message {
    max-width: 80%;
    padding: 10px;
    margin: 8px;
    border-radius: 10px;
}

.user {
    background: #0b93f6;
    margin-left: auto;
}

.bot {
    background: #444654;
}

.input-box {
    display: flex;
    padding: 10px;
    background: #202123;
    position: sticky;
    bottom: 0;
}

input {
    flex: 1;
    padding: 12px;
    border-radius: 20px;
    border: none;
    outline: none;
}

button {
    margin-left: 10px;
    padding: 12px;
    border-radius: 50%;
    border: none;
    background: #19c37d;
    color: white;
    cursor: pointer;
}
</style>
</head>

<body>

<div class="chat-container">
    <div class="messages" id="messages"></div>

    <div class="input-box">
        <input id="input" placeholder="Ask Jarvis anything...">
        <button onclick="send()">➤</button>
    </div>
</div>

<script>
async function send() {
    let input = document.getElementById("input");
    let msg = input.value.trim();
    if (!msg) return;

    addMessage(msg, "user");
    input.value = "";

    let res = await fetch("/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({message: msg})
    });

    let data = await res.json();
    addMessage(data.reply, "bot");
}

function addMessage(text, type) {
    let div = document.createElement("div");
    div.className = "message " + type;
    div.innerText = text;

    document.getElementById("messages").appendChild(div);
    div.scrollIntoView({behavior: "smooth"});
}
</script>

</body>
</html>
"""

# 🏠 Home
@app.route("/")
def home():
    return render_template_string(HTML_UI)

# 💬 Chat API
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")

    # 🧠 Add memory
    chat_history.append({"role": "user", "content": user_message})

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "system", "content": "You are Jarvis AI created by Mahmudul Hasan aka Hasan."}
        ] + chat_history[-10:]  # last 10 messages
    }

    response = requests.post(API_URL, headers=headers, json=data)
    result = response.json()

    reply = result["choices"][0]["message"]["content"]

    # 🧠 Save bot reply
    chat_history.append({"role": "assistant", "content": reply})

    return jsonify({"reply": reply})

# 🚀 Run
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
