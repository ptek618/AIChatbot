from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
import subprocess

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"message": "✅ ProTek Chatbot is running. Hooray Walker you are cool!"})

@app.route("/git-pull", methods=["POST"])
def git_pull():
    try:
        result = subprocess.run(["git", "pull"], capture_output=True, text=True, cwd="/opt/protek-chatbot")
        output = result.stdout.strip()
        subprocess.run(["sudo", "systemctl", "restart", "protek-chatbot"])
        return jsonify({"output": output, "status": "success"})
    except Exception as e:
        return jsonify({"output": str(e), "status": "error"})

@app.route("/sms", methods=["POST"])
def sms_reply():
    incoming_msg = request.form.get("Body", "").strip()
    from_number = request.form.get("From", "")

    response = MessagingResponse()
    reply_text = f"You said: {incoming_msg}. We'll get back to you shortly!"  # Placeholder logic
    response.message(reply_text)
    return str(response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
