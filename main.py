from flask import Flask, render_template, request, jsonify, session, redirect
import json, os, random

app = Flask(__name__)
app.secret_key = "jarvis_secret"

FREE_LIMIT = 10
OWNER_PASSWORD = "784176"

# ---------- DATA ----------
def load_json(file):
    if os.path.exists(file):
        return json.load(open(file))
    return []

def save_json(file, data):
    json.dump(data, open(file, "w"))

# ---------- OTP ----------
otp_store = {}

@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")
    return render_template("index.html")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/send-otp", methods=["POST"])
def send_otp():
    username = request.json["username"]
    otp = str(random.randint(1000,9999))
    otp_store[username] = otp
    print("OTP:", otp)
    return jsonify({"msg":"OTP sent (check console)"})

@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    username = request.json["username"]
    otp = request.json["otp"]

    if otp_store.get(username) == otp:
        session["user"] = username
        return jsonify({"success":True})
    return jsonify({"success":False})

@app.route("/owner-login", methods=["POST"])
def owner_login():
    if request.json["password"] == OWNER_PASSWORD:
        session["user"] = "OWNER"
        return jsonify({"success":True})
    return jsonify({"success":False})

# ---------- CHAT ----------
@app.route("/chat", methods=["POST"])
def chat():
    user = session.get("user")
    msg = request.json["message"]

    if user == "OWNER":
        return jsonify({"reply": f"👑 OWNER: {msg}"})

    file = f"{user}_history.json"
    history = load_json(file)

    premium = load_json("premium.json")

    if user not in premium and len(history) >= FREE_LIMIT:
        return jsonify({"reply":"🚫 Limit reached. Go Premium 💎"})

    reply = f"Jarvis: {msg}"

    history.append({"user":msg,"bot":reply})
    save_json(file, history)

    return jsonify({"reply":reply})

# ---------- PREMIUM ----------
@app.route("/make-premium", methods=["POST"])
def make_premium():
    username = request.json["username"]

    premium = load_json("premium.json")
    premium.append(username)
    save_json("premium.json", premium)

    return jsonify({"msg":"Upgraded"})

# ---------- IMAGE ----------
@app.route("/generate-image", methods=["POST"])
def img():
    prompt = request.json["prompt"]
    return jsonify({
        "url": f"https://dummyimage.com/512x512/000/fff&text={prompt}"
    })

if __name__ == "__main__":
    app.run()
