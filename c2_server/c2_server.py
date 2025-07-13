# c2_server/c2_server.py

from flask import Flask, request
import os

app = Flask(__name__)

UPLOAD_FOLDER = "/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return "No file part", 400

    file = request.files["file"]
    if file.filename == "":
        return "No selected file", 400

    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(save_path)
    print(f"[+] File received and saved to {save_path}")
    return "OK", 200

app.run(host="0.0.0.0", port=5000)

