import os, socket
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient

app = Flask(__name__)
db = MongoClient(os.environ["MONGO_URL"], serverSelectionTimeoutMS=2000).emidb
pod = os.environ.get("HOSTNAME", "unknown")
ip = socket.gethostbyname(socket.gethostname())

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/emi", methods=["POST"])
def emi():
    d = request.get_json(silent=True) or {}
    try:
        p, rate, n = float(d["P"]), float(d["rate"]), int(d["n"])
    except (KeyError, ValueError, TypeError):
        return jsonify(error="Invalid input"), 400
    if p <= 0 or rate <= 0 or n <= 0:
        return jsonify(error="Values must be positive"), 400
    r = rate / 12 / 100
    e = p * r * (1 + r) ** n / ((1 + r) ** n - 1)
    db.calculations.insert_one({"principal": p, "rate": rate, "months": n, "emi": round(e, 2),
                                "servedBy": pod, "createdAt": datetime.now().isoformat(timespec="seconds")})
    return jsonify(emi=round(e, 2), totalPayment=round(e * n, 2), totalInterest=round(e * n - p, 2),
                   servedBy=pod, podIp=ip)

@app.route("/api/history")
def history():
    rows = db.calculations.find({}, {"_id": 0}).sort("_id", -1).limit(10)
    return jsonify(list(rows))

@app.route("/health")
def health():
    try:
        db.command("ping")
        return "ok"
    except Exception:
        return "db down", 503
