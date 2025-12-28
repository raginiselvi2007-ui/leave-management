from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pyrebase
import uuid

app = Flask(__name__)
CORS(app)

# ---------------- Firebase configuration ----------------
firebaseConfig = {
    "apiKey": "AIzaSyD683qsiVdBgQBoNrfx9wXBUNKy0W3QBkg",
    "authDomain": "leave-management-823ee.firebaseapp.com",
    "databaseURL": "https://leave-management-823ee-default-rtdb.firebaseio.com",
    "projectId": "leave-management-823ee",
    "storageBucket": "leave-management-823ee.appspot.com",
    "messagingSenderId": "362533814868",
    "appId": "1:362533814868:web:e2f7ec84a8f373f3b963c1",
    "measurementId": "G-41BGS1MJNK"
}

firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

# ---------------- Manager credentials ----------------
MANAGER_USER = "hrmanager"
MANAGER_PASS = "hospital123"

# ---------------- Routes ----------------
@app.route("/")
def home():
    return render_template("index.html")

# Submit leave
@app.route("/api/leaves", methods=["POST"])
def add_leave():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Invalid JSON"}), 400

    required_fields = ["name", "department", "type", "leave_date", "reason"]
    if not all(field in data and data[field] for field in required_fields):
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    leave_id = str(uuid.uuid4())
    leave = {
        "id": leave_id,
        "name": data["name"],
        "department": data["department"],
        "type": data["type"],
        "leave_date": data["leave_date"],
        "reason": data["reason"],
        "status": "Pending"
    }

    db.child("leaves").child(leave_id).set(leave)
    return jsonify({"success": True, "message": "Leave submitted successfully", "leave_id": leave_id}), 200

# Get all leaves
@app.route("/api/leaves", methods=["GET"])
def get_leaves():
    leaves = db.child("leaves").get().val() or {}
    return jsonify(list(leaves.values())), 200

# Update leave status
@app.route("/api/leaves/<leave_id>", methods=["PUT"])
def update_leave(leave_id):
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Invalid JSON"}), 400

    status = data.get("status")
    if status not in ["Approved", "Rejected"]:
        return jsonify({"success": False, "message": "Invalid status"}), 400

    leave = db.child("leaves").child(leave_id).get().val()
    if not leave:
        return jsonify({"success": False, "message": "Leave not found"}), 404

    db.child("leaves").child(leave_id).update({"status": status})
    return jsonify({"success": True, "message": f"Leave {status} successfully"}), 200

# Manager login
@app.route("/api/manager/login", methods=["POST"])
def manager_login():
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "message": "Invalid JSON"}), 400

    username = data.get("username")
    password = data.get("password")

    if username == MANAGER_USER and password == MANAGER_PASS:
        return jsonify({"success": True, "message": "Login successful"}), 200

    return jsonify({"success": False, "message": "Invalid credentials"}), 401

# ---------------- Run Flask app ----------------
if __name__ == "__main__":
    app.run(debug=True)
