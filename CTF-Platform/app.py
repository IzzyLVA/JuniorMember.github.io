from flask import Flask, render_template, request, make_response, session, redirect, url_for
import base64
import sqlite3
import os

# ===== SETUP =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

app = Flask(__name__)
app.secret_key = "supersecretkey"


# ===== HOME =====
@app.route("/")
def index():
    return render_template("index.html", solved=session.get("solved", {}))


# ===== PORTAL CHALLENGE (SQLi) =====
@app.route("/challenge/portal", methods=["GET", "POST"])
def portal():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    message = ""

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Intentionally vulnerable query (for CTF)
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        result = cursor.execute(query).fetchone()

        if result:
            message = "ACCESS GRANTED :: JMCTF{1s_1t_r3al_L1fe_0r_ju5t_5q1i_1nject10n}"
        else:
            message = "ACCESS DENIED"

    conn.close()
    return render_template("portal.html", message=message)


# ===== COOKIE CHALLENGE =====
@app.route("/challenge/cookies")
def cookies():
    role_cookie = request.cookies.get("role")

    try:
        decoded = base64.b64decode(role_cookie).decode() if role_cookie else "user"
    except:
        decoded = "invalid"

    if decoded == "admin":
        message = "ACCESS GRANTED :: JMCTF{0nly_Ch0co1at3_ch1p_c00kies_ar3_g00d}"
    else:
        message = f"ACCESS DENIED :: role = {decoded}"

    # Reset cookie every time (important for challenge)
    encoded = base64.b64encode("user".encode()).decode()

    resp = make_response(render_template("cookies.html", message=message))
    resp.set_cookie("role", encoded)

    return resp


# ===== COOKIE CHECK ENDPOINT =====
@app.route("/challenge/cookies/check")
def cookie_check():
    role_cookie = request.cookies.get("role")

    try:
        decoded = base64.b64decode(role_cookie).decode()
    except:
        decoded = "invalid"

    if decoded == "admin":
        return "<h2>ACCESS GRANTED</h2><p>JMCTF{0nly_Ch0co1at3_ch1p_c00kies_ar3_g00d}</p>"
    else:
        return f"<h2>ACCESS DENIED</h2><p>Current role: {decoded}</p>"


# ===== FLAGS =====
FLAGS = {
    "portal": "JMCTF{1s_1t_r3al_L1fe_0r_ju5t_5q1i_1nject10n}",
    "cookies": "JMCTF{0nly_Ch0co1at3_ch1p_c00kies_ar3_g00d}",
    "vault": "JMCTF{vault_breaker}"  # optional, matches your UI
}


# ===== FLAG SUBMISSION =====
@app.route("/submit_flag", methods=["POST"])
def submit_flag():
    flag = request.form.get("flag")
    challenge = request.form.get("challenge")

    if "solved" not in session:
        session["solved"] = {}

    if FLAGS.get(challenge) == flag:
        session["solved"][challenge] = True
        session.modified = True
        return "", 200  # ✅ success

    return "fail", 400  # ❌ failure

    return redirect(url_for("index"))


# ===== RESET =====
@app.route("/reset")
def reset():
    session.clear()
    return redirect(url_for("index"))


# ===== RUN =====
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)