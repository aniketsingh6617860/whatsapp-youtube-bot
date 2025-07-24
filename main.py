from flask import Flask, request, send_file, abort
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import yt_dlp
import os
import shutil

app = Flask(__name__)

account_sid = "AC08330adacb129878f4a7a52361fcb6bf"
auth_token = "c774cacc88f2c884dc09f4f816fd573d"
client = Client(account_sid, auth_token)

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.values.get('Body', '').strip()
    resp = MessagingResponse()
    msg = resp.message()

    try:
        if "youtube.com" in incoming_msg or "youtu.be" in incoming_msg:
            filename = "downloaded_video.mp4"
            old_folder = "old_downloads"

            # Create old_downloads folder if it doesn't exist
            if not os.path.exists(old_folder):
                os.makedirs(old_folder)

            # If current video exists, move it to old_downloads with incrementing filename
            if os.path.exists(filename):
                count = len(os.listdir(old_folder)) + 1
                new_name = os.path.join(old_folder, f"video_{count}.mp4")
                shutil.move(filename, new_name)

            # Download new video
            ydl_opts = {'format': 'mp4', 'outtmpl': filename}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([incoming_msg])

            if os.path.exists(filename):
                file_url = request.url_root + filename
                msg.body("Here is your downloaded video:")
                msg.media(file_url)
            else:
                msg.body("Download failed, please try again.")

            # Clean old_downloads folder after process completion
            for file in os.listdir(old_folder):
                file_path = os.path.join(old_folder, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        else:
            msg.body("Please send a valid YouTube Shorts link.")
    except Exception as e:
        msg.body(f"Error: {str(e)}")
    return str(resp)

@app.route('/<filename>')
def serve_file(filename):
    if os.path.exists(filename):
        return send_file(filename)
    else:
        abort(404)

if __name__ == "__main__":
    app.run(debug=True)