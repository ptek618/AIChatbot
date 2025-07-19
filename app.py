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

# the below code was pasted for the chat portion

import { useState } from "react";

export default function ChatWidget() {
  const [messages, setMessages] = useState([
    { from: "bot", text: "👋 Hi! How can I help you today?" }
  ]);
  const [input, setInput] = useState("");

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { from: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");

    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: input })
    });

    const data = await res.json();
    setMessages((prev) => [...prev, { from: "bot", text: data.reply }]);
  };

  return (
    <div className="w-full max-w-md p-4 shadow-xl rounded-2xl bg-white border mx-auto">
      <div className="h-64 overflow-y-auto space-y-2 mb-4">
        {messages.map((msg, i) => (
          <div key={i} className={`text-sm ${msg.from === "bot" ? "text-left" : "text-right"}`}>
            <span className={`inline-block px-3 py-2 rounded-xl ${msg.from === "bot" ? "bg-gray-200" : "bg-blue-500 text-white"}`}>
              {msg.text}
            </span>
          </div>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          className="flex-1 border rounded-xl px-3 py-2"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
        />
        <button className="px-4 py-2 bg-blue-600 text-white rounded-xl" onClick={sendMessage}>
          Send
        </button>
      </div>
    </div>
  );
}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
