from flask import Flask, request, jsonify
import subprocess
from twilio.twiml.messaging_response import MessagingResponse

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
    incoming_msg = request.form.get('Body', '').strip().lower()
    resp = MessagingResponse()

    if "hello" in incoming_msg:
        resp.message("Hey there 👋! This is the ProTek Chatbot.")
    elif "help" in incoming_msg:
        resp.message("Here are some things you can ask me:\n- 'Outage'\n- 'Speed test'\n- 'Billing'")
    else:
        resp.message("Sorry, I didn’t understand that. Try texting 'help'.")

    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
