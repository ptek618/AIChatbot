from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
import subprocess

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"message": "✅ ProTek Chatbot is running. I hope this works!"})

@app.route("/git-pull", methods=["POST"])
def git_pull():
    try:
        result = subprocess.run(["git", "pull"], capture_output=True, text=True, cwd="/opt/protek-chatbot")
        output = result.stdout.strip()
        error_output = result.stderr.strip()

        def restart_service():
            subprocess.run(["sudo", "systemctl", "restart", "protek-chatbot"])

        threading.Thread(target=restart_service).start()

        return jsonify({
            "output": output or error_output,
            "status": "success"
        }), 200

    except Exception as e:
        return jsonify({"output": str(e), "status": "error"}), 500

@app.route("/sms", methods=["POST"])
def sms_reply():
    incoming_msg = request.form.get("Body", "").strip().lower()
    resp = MessagingResponse()

    # Basic logic example
    if "hi" in incoming_msg or "hello" in incoming_msg:
        resp.message("👋 Hello! This is the ProTek Chatbot. How can I help you today?")
    elif "help" in incoming_msg:
        resp.message("🛠️ Sure! You can ask me about your service, report an outage, or check your account.")
    else:
        resp.message("🤖 Sorry, I didn’t understand that. Try saying 'help' or 'hello'.")

    return str(resp)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
