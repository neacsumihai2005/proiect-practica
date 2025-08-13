from flask import Flask, request
import os

app = Flask(__name__)
UPLOAD_FOLDER = "/tmp/exfiltrated"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return "No file part", 400
    file = request.files["file"]
    file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, ssl_context=("cert.pem", "key.pem"))

