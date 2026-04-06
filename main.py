from flask import Flask, render_template, request, jsonify, session, redirect
import sqlite3, os
from groq import Groq

app = Flask(__name__)
app.secret_key = "jarvis_secret"

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users(
        username TEXT PRIMARY KEY,
        otp TEXT,
        messages INTEGER
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS chats(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        role TEXT,
        message TEXT
    )""")

    conn.commit()
    conn.close()

init_db()

# ================= ROUTES =================

@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")
    return render_template("index.html", username=session["user"])

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/send-otp", methods=["POST"])
def send_otp():
    username = request.json.get("username")

    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("INSERT OR REPLACE INTO users VALUES (?, ?, ?)",
              (username, "1234", 0))

    conn.commit()
    conn.close()

    return jsonify({"status": "OTP SENT"})

@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    username = request.json.get("username")
    otp = request.json.get("otp")

    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username=? AND otp=?",
              (username, otp))

    user = c.fetchone()
    conn.close()

    if user:
        session["user"] = username
        return jsonify({"status": "SUCCESS"})
    return jsonify({"status": "FAILED"})

@app.route("/chat", methods=["POST"])
def chat():
    if "user" not in session:
        return jsonify({"reply": "Login required"})

    username = session["user"]
    msg = request.json.get("message")

    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("SELECT messages FROM users WHERE username=?", (username,))
    messages = c.fetchone()[0]

    if messages >= 10:
        return jsonify({"reply": "LIMIT"})

    c.execute("UPDATE users SET messages = messages + 1 WHERE username=?", (username,))
    conn.commit()

    # SAVE USER MESSAGE
    c.execute("INSERT INTO chats (username, role, message) VALUES (?, ?, ?)",
              (username, "user", msg))

    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": f"You are Jarvis AI. User is {username}. Be smart and helpful."},
                {"role": "user", "content": msg}
            ]
        )
        reply = completion.choices[0].message.content
    except:
        reply = "AI error ⚠️"

    # SAVE BOT REPLY
    c.execute("INSERT INTO chats (username, role, message) VALUES (?, ?, ?)",
              (username, "bot", reply))

    conn.commit()
    conn.close()

    return jsonify({"reply": reply})

@app.route("/history")
def history():
    if "user" not in session:
        return jsonify([])

    username = session["user"]

    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("SELECT role, message FROM chats WHERE username=?", (username,))
    chats = c.fetchall()

    conn.close()

    return jsonify(chats)

@app.route("/unlock", methods=["POST"])
def unlock():
    username = session.get("user")

    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("UPDATE users SET messages=0 WHERE username=?", (username,))
    conn.commit()
    conn.close()

    return jsonify({"status": "unlocked"})

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run()
