from flask import Flask, render_template, request, jsonify, session, redirect
import json, os, datetime
from groq import Groq

app = Flask(__name__)
app.secret_key = "jarvis_secret"

DAILY_LIMIT = 69
OWNER_PASSWORD = "784176"

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def load(file):
    if os.path.exists(file):
        return json.load(open(file))
    return {}

def save(file, data):
    json.dump(data, open(file, "w"))

@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

# -------- OTP --------
otp_store = {}

@app.route("/send-otp", methods=["POST"])
def send_otp():
    user = request.json["username"]
    otp_store[user] = "1234"
    return jsonify({"status": "sent"})

@app.route("/verify-otp", methods=["POST"])
def verify():
    user = request.json["username"]
    otp = request.json["otp"]

    if otp_store.get(user) == otp:
        session["user"] = user
        return jsonify({"status": "ok"})
    return jsonify({"status": "fail"})

# -------- CHAT --------
@app.route("/chat", methods=["POST"])
def chat():
    if "user" not in session:
        return jsonify({"reply": "Login first"})

    user = session["user"]
    premium = load("premium.json")
    memory = load("memory.json")

    today = str(datetime.date.today())

    if user not in premium:
        premium[user] = {"date": today, "count": 0, "premium": False}

    if premium[user]["date"] != today:
        premium[user]["date"] = today
        premium[user]["count"] = 0

    if not premium[user]["premium"] and premium[user]["count"] >= DAILY_LIMIT:
        return jsonify({"reply": "LIMIT"})

    msg = request.json["message"]

    # MEMORY
    history = memory.get(user, [])
    history.append({"role": "user", "content": msg})
    history = history[-5:]  # last 5 messages

    messages = [
        {"role": "system", "content": "You are Jarvis, a smart, cool AI. Short, powerful answers."}
    ] + history

    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=messages
    )

    reply = completion.choices[0].message.content

    history.append({"role": "assistant", "content": reply})
    memory[user] = history

    premium[user]["count"] += 1

    save("premium.json", premium)
    save("memory.json", memory)

    return jsonify({
        "reply": reply,
        "left": DAILY_LIMIT - premium[user]["count"]
    })

# -------- OWNER --------
@app.route("/make-premium", methods=["POST"])
def make_premium():
    if request.json.get("password") != OWNER_PASSWORD:
        return jsonify({"status": "no"})

    user = request.json.get("user")
    data = load("premium.json")

    if user in data:
        data[user]["premium"] = True
        save("premium.json", data)

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True)
