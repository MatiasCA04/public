# middleware.py
from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)
DATA_FILE = "users.json"

# garantir que o ficheiro existe
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

def load_users():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=2)

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    ip = data.get("ip")

    if not username or not ip:
        return jsonify({"status": "error", "message": "Missing username or ip"}), 400

    users = load_users()
    users[username] = ip
    save_users(users)

    return jsonify({"status": "ok", "message": f"{username} registado com ip {ip}"})

@app.route("/get_ip/<username>", methods=["GET"])
def get_ip(username):
    users = load_users()
    if username in users:
        return jsonify({"status": "ok", "ip": users[username]})
    else:
        return jsonify({"status": "error", "message": "User not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
