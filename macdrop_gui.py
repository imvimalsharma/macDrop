import webview
import threading
import socket
import qrcode
from flask import Flask, request
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>

<title>MacDrop</title>

<style>

body{
font-family: Arial;
text-align:center;
margin-top:60px;
}

progress{
width:300px;
height:20px;
}

</style>

</head>

<body>

<h2>MacDrop</h2>

<h3>Send Files or Folder to Mac</h3>

<input type="file" id="fileInput" webkitdirectory directory multiple>

<br><br>

<button onclick="upload()">Upload</button>

<br><br>

<progress id="progressBar" value="0" max="100"></progress>

<p id="status"></p>

<script>

async function upload(){

let files = document.getElementById("fileInput").files

let total = files.length
let count = 0

for(let file of files){

let formData = new FormData()

let path = file.webkitRelativePath || file.name

formData.append("file", file, path)

let xhr = new XMLHttpRequest()

xhr.upload.onprogress = function(e){

if(e.lengthComputable){

let percent = (e.loaded/e.total)*100
document.getElementById("progressBar").value = percent

}

}

await new Promise(resolve => {

xhr.onload = resolve
xhr.open("POST","/upload")
xhr.send(formData)

})

count++

document.getElementById("status").innerText =
"Uploaded "+count+" / "+total

}

alert("Upload complete")

}

</script>

</body>
</html>
"""


@app.route("/")
def home():
    return HTML_PAGE


@app.route("/upload", methods=["POST"])
def upload():

    file = request.files["file"]

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    file.save(filepath)

    return "ok"


def get_ip():

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    s.connect(("8.8.8.8",80))

    ip = s.getsockname()[0]

    s.close()

    return ip


def start_server():
    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":

    ip = get_ip()

    url = f"http://{ip}:5000"

    img = qrcode.make(url)

    img.save("qr.png")

    print("QR code saved as qr.png")

    threading.Thread(target=start_server).start()

    webview.create_window("MacDrop", url)

    webview.start()

