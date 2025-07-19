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
        error_output = result.stderr.strip()
        print("Git stdout:", output)
        print("Git stderr:", error_output)

        #subprocess.run(["sudo", "systemctl", "restart", "protek-chatbot"])
        return jsonify({"output": output or error_output, "status": "success"})
    except Exception as e:
        print("Exception occurred in /git-pull:", str(e))
        return jsonify({"output": str(e), "status": "error"})

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
