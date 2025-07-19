from flask import Flask, jsonify, request
import subprocess

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"message": "✅ ProTek Chatbot is running."})

@app.route("/git-pull", methods=["POST"])
def git_pull():
    try:
        result = subprocess.run(["git", "pull"], capture_output=True, text=True, cwd="/opt/protek-chatbot")
        return jsonify({"status": "success", "output": result.stdout})
    except Exception as e:
        return jsonify({"status": "error", "output": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
