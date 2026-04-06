 from flask import Flask, render_template, request, jsonify, session, redirect
import json, os, random, datetime

app = Flask(__name__)
app.secret_key = "jarvis_secret"

DAILY_LIMIT = 69
OWNER_PASSWORD = "784176"

# ---------- HELPERS ----------
def load_json(file):
    if os.path.exists(file):
        return json.load(open(file))
    return {}

def save_json(file, data):
    json.dump(data, open(file, "w"))

otp_store = {}

# ---------- ROUTES ----------
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")

# ---------- OTP ----------
@app.route("/send-otp", methods=["POST"])
def send_otp():
    username = request.json["username"]
    otp = str(random.randint(1000,9999))
    otp_store[username] = otp
    print("OTP:", otp)
    return jsonify({"msg":"OTP sent (check console)"})

@app.route("/verify-otp", methods=["POST"])
def verify():
    username = request.json["username"]
    otp = request.json["otp"]

    if otp_store.get(username) == otp:
        session["user"] = username
        return jsonify({"success":True})
    return jsonify({"success":False})

# ---------- OWNER ----------
@app.route("/owner-login", methods=["POST"])
def owner():
    if request.json["password"] == OWNER_PASSWORD:
        session["user"] = "OWNER"
        return jsonify({"success":True})
    return jsonify({"success":False})

# ---------- CHAT ----------
@app.route("/chat", methods=["POST"])
def chat():
    user = session.get("user")
    msg = request.json["message"]

    # OWNER = unlimited
    if user == "OWNER":
        return jsonify({"reply": f"👑 OWNER MODE: {msg}"})

    # Load user daily data
    file = f"{user}_daily.json"
    data = load_json(file)

    today = str(datetime.date.today())

    # Reset if new day
    if data.get("date") != today:
        data = {
            "date": today,
            "count": 0
        }

    premium = load_json("premium.json")

    # Limit check
    if user not in premium and data["count"] >= DAILY_LIMIT:
        return jsonify({
            "reply": "🚫 Daily limit (69) finished. Come back tomorrow or go Premium 💎"
        })

    # AI response (simple for now)
    reply = f"Jarvis: {msg}"

    # Update count
    data["count"] += 1
    save_json(file, data)

    return jsonify({"reply": reply})

# ---------- PREMIUM ----------
@app.route("/make-premium", methods=["POST"])
def make_premium():
    username = request.json["username"]

    premium = load_json("premium.json")
    if username not in premium:
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
