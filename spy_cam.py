import time
import os
import subprocess
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# --- CONFIGURATION ---
PORT = 8080
TEMP_FILE = "temp_capture.jpg"  # We write to disk to avoid Pipe hanging
CAMERA_ID = "0"                 # 0 = Back, 1 = Front

# --- GLOBAL STATE ---
frame_condition = threading.Condition()
current_frame = None

# --- PRODUCER: CAMERA WORKER ---
def camera_producer():
    global current_frame
    print("[*] Camera Producer started (File-Based Mode).")

    while True:
        try:
            # 1. CAPTURE TO FILE (Blocking)
            # We force overwrite so we don't fill up storage
            subprocess.run(
                ["termux-camera-photo", "-c", CAMERA_ID, TEMP_FILE],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # 2. CHECK IF FILE EXISTS & HAS DATA
            if os.path.exists(TEMP_FILE) and os.path.getsize(TEMP_FILE) > 0:

                # 3. COMPRESS WITH FFMPEG (Read file -> Compress -> RAM)
                # We read the temp file, resize to 640px, and output to STDOUT (RAM)
                ffmpeg_cmd = [
                    "ffmpeg",
                    "-y",
                    "-i", TEMP_FILE,       # Input the temp file
                    "-vf", "scale=640:-1", # Resize width to 640
                    "-q:v", "15",          # JPEG Quality (Low)
                    "-f", "image2",        # Output format
                    "-"                    # Output to STDOUT
                ]

                result = subprocess.run(
                    ffmpeg_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL
                )

                compressed_data = result.stdout

                # 4. BROADCAST TO WEB CLIENTS
                if compressed_data:
                    with frame_condition:
                        current_frame = compressed_data
                        frame_condition.notify_all()

            else:
                print("[!] Camera took no photo. Check permissions.")
                time.sleep(2)

        except Exception as e:
            print(f"[!] Error: {e}")
            time.sleep(1)

# --- CONSUMER: WEB SERVER ---
class MJPEGHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()

            try:
                while True:
                    with frame_condition:
                        # Wait for the next frame (Max 10s timeout to prevent hanging)
                        notified = frame_condition.wait(timeout=10.0)

                        if not notified:
                            # If camera is slow, send a 'ping' to keep connection alive
                            continue

                        frame_data = current_frame

                    if frame_data:
                        self.wfile.write(b"--jpgboundary\r\n")
                        self.send_header('Content-type', 'image/jpeg')
                        self.send_header('Content-length', str(len(frame_data)))
                        self.end_headers()
                        self.wfile.write(frame_data)
                        self.wfile.write(b"\r\n")

            except (BrokenPipeError, ConnectionResetError):
                pass

# --- MAIN ---
if __name__ == '__main__':
    # Clean up old file
    if os.path.exists(TEMP_FILE): os.remove(TEMP_FILE)

    t = threading.Thread(target=camera_producer, daemon=True)
    t.start()

    print(f"[*] Stream running @ http://0.0.0.0:{PORT}")
    try:
        server = ThreadingHTTPServer(('0.0.0.0', PORT), MJPEGHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[!] Stopping...")
