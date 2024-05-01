from flask import Flask, request, jsonify

app = Flask(__name__)
db = {}

@app.route("/worker", methods=["POST"])
def register():
    """Saving worker information on the database"""
    data = request.json
    required_fields = ["id", "ip", "ram", "cpu", "status"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    worker_id = data["id"]
    db[worker_id] = {
        "ip": data["ip"],
        "ram": data["ram"],
        "cpu": data["cpu"],
        "status": data["status"],
    }
    return jsonify({"status": "ok", "id": worker_id}), 200

@app.route("/worker", methods=["GET"])
def get_workers():
    """List of all registered workers"""
    return jsonify(list(db.keys())), 200

@app.route("/worker/<worker_id>", methods=["GET"])
def get_worker(worker_id):
    """List of requested worker information"""
    if worker_id not in db:
        return jsonify({"error": "Worker not found"}), 404
    return jsonify(db[worker_id]), 200

if __name__ == "__main__":
    app.run(debug=True)