from flask import Flask, jsonify, request
import subprocess

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"message": "✅ ProTek Chatbot is running. Hooray!"})

@app.route("/git-pull", methods=["POST"])
def git_pull():
    try:
        result = subprocess.run(["git", "pull"], capture_output=True, text=True, cwd="/opt/protek-chatbot")
        return jsonify({"status": "success", "output": result.stdout})
    except Exception as e:
        return jsonify({"status": "error", "output": str(e)})


@app.route('/git-pull', methods=['POST'])
def git_pull():
    try:
        output = subprocess.check_output(['git', 'pull'], cwd='/opt/protek-chatbot').decode('utf-8')

        # Restart Flask app
        subprocess.call(['systemctl', 'restart', 'protek-chatbot'])

        return jsonify({'status': 'success', 'output': output})
    except Exception as e:
        return jsonify({'status': 'error', 'output': str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
test auto-deploy: [hello world]
