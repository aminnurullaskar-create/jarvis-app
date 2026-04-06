from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)

# 🔑 YOUR API KEY (paste here)
API_KEY = "gsk_SqDpi0gm52iZPKwwwLsQWGdyb3FYgl66bdLNFKy4MQt1JKdOrER"

# 🌐 API URL (using OpenAI-compatible endpoint)
API_URL = "https://api.openai.com/v1/chat/completions"

# 🎨 SIMPLE CHATGPT-LIKE UI
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
    background: #f7f7f8;
}

.chat-container {
    max-width: 600px;
    margin: auto;
    height: 100vh;
    display: flex;
    flex-direction: column;
}

.messages {
    flex: 1;
    overflow-y: auto;
    padding: 10px;
}

.message {
    margin: 10px;
    padding: 10px;
    border-radius: 10px;
    max-width: 80%;
}

.user {
    background: #007aff;
    color: white;
    margin-left: auto;
}

.bot {
    background: #e5e5ea;
}

.input-box {
    display: flex;
    padding: 10px;
    background: white;
    position: sticky;
    bottom: 0;
}

input {
    flex: 1;
    padding: 10px;
    border-radius: 20px;
    border: 1px solid #ccc;
}

button {
    margin-left: 10px;
    padding: 10px;
    border-radius: 50%;
    border: none;
    background: #007aff;
    color: white;
}
</style>
</head>

<body>

<div class="chat-container">
    <div class="messages" id="messages"></div>

    <div class="input-box">
        <input id="input" placeholder="Ask Jarvis...">
        <button onclick="send()">➤</button>
    </div>
</div>

<script>
async function send() {
    let input = document.getElementById("input");
    let msg = input.value;
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
    div.scrollIntoView();
}
</script>

</body>
</html>
"""

# 🏠 Home route
@app.route("/")
def home():
    return render_template_string(HTML_UI)

# 💬 Chat API
@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are Jarvis AI created by Mahmudul Hasan aka Hasan."},
            {"role": "user", "content": user_msg}
        ]
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        result = response.json()

        reply = result["choices"][0]["message"]["content"]
        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": "Error: " + str(e)})

# ❌ DO NOT ADD app.run() (Render uses gunicorn)
