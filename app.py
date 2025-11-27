from flask import Flask, Response, render_template_string, send_from_directory
import cv2
import time
import json
import datetime
from threading import Thread
import v4l2_controls

app = Flask(__name__)


v4l2_controls.power_line_freq(1)

# Camera class sa thread-om
class Camera:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.frame = None
        Thread(target=self.update, daemon=True).start()

    def update(self):
        while True:
            ret, frame = self.cap.read()
            if ret:
                self.frame = frame

    def get_frame(self):
        return self.frame

camera = Camera()
fgbg = cv2.createBackgroundSubtractorMOG2(history=200, varThreshold=25, detectShadows=True)

last_alarm = 0
ALARM_COOLDOWN = 3  # sekunde
events = []

IGNORE_FRAMES = 30
frame_count = 0

# HTML stranica sa video containerom
HTML_PAGE = """
<!doctype html>
<html>
<head>
    <title>SmartCam - Live Stream</title>
    <style>
        body { background: #111; color: white; text-align:center; font-family: Arial; }
        img { width: 90%; max-width: 640px; border: 3px solid #00ff00; border-radius: 10px; }
    </style>
</head>
<body>
    <h1>SmartCam Live Stream</h1>
    <img src="/video_feed" />
</body>
</html>
"""

def gen_frames():
    global last_alarm, frame_count
    while True:
        frame = camera.get_frame()
        if frame is None:
            continue

        frame_count += 1
        fgmask = fgbg.apply(frame)

        if frame_count <= IGNORE_FRAMES:
            continue

        thresh = cv2.threshold(fgmask, 244, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.erode(thresh, None, iterations=2)
        thresh = cv2.dilate(thresh, None, iterations=2)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        motion_detected = False
        for cnt in contours:
            if cv2.contourArea(cnt) < 1500:
                continue
            (x, y, w, h) = cv2.boundingRect(cnt)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            motion_detected = True

        if motion_detected and (time.time() - last_alarm > ALARM_COOLDOWN):
            last_alarm = time.time()
            print("Detektovan pokret")
            event = {"timestamp": datetime.datetime.now().isoformat(), "type": "motion"}
            events.append(event)
            with open("evidencija.json", "w") as f:
                json.dump(events, f, indent=4)

        # Encode frame to JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

@app.route("/video_feed")
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route("/evidencija.json")
def get_evidencija():
    return send_from_directory(".", "evidencija.json")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
