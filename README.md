# Android-Phone-Shadow-Cam
This project is a custom-built surveillance system that runs directly on the metal of your Android phone. Instead of relying on opaque third-party software, I used Termux API to bridge the Android Hardware Layer with a Linux environment.

> **"Why download a bloated, ad-filled IP Webcam app when you can engineer your own?"**

**Termux-Shadow-Cam** is a custom-built surveillance system that runs directly on the metal of your Android phone. Instead of relying on opaque third-party software, this project uses **Termux API** to bridge the Android Hardware Layer with a Linux environment, giving you full control over your device's camera.

## 🚀 Why I Built This
Most "CCTV" apps for Android are black boxes. They are often laggy, save data to storage (wearing it out), and don't tell you where that data goes.

I wanted a solution that was Transparent, pure code, no hidden trackers.

**The Solution:**
1.  **Termux** sends a command.
2.  **Termux:API** acts as the "Bridge/Translator," requesting permission from Android OS.
3.  **Android OS** grants access and returns the image data.
4.  **Python Script** captures the image into a RAM buffer and broadcasts the stream to your network.


## ⚙️ Prerequisites
You need an Android phone with:
- Termux setup which can serve requests for devices 
- [Checkout Repository where I set up termux and tailscale](https://github.com/Nikhil-Richhariya/Android-Phone-as-Server)

## 📦 Installation

1.  **Update Termux & Install Dependencies:**
    ```bash
    pkg update && pkg upgrade
    pkg install python ffmpeg termux-api
    ```

2.  **Install termux api Android Application**
    download from the same source where you downloaded termux. 
    if you downloaded termux from playstore then download termux api from playstore only 
    if you downloaded termus from f-droid then download termux api from f-droid only 

3.  **Grant Camera Permissions:**
    (Important: You must run this once on the phone screen to accept the prompt)
    ```bash
    termux-camera-photo -c 0 test.jpg
    ```

## 🖥️ Usage

1.  **Start the Server:**
    ```bash
    python camera_server.py
    ```

2.  **View the Feed:**
    Open a browser on any device in the same Wi-Fi network and visit:
    `http://<PHONE_IP>:8000`

**My Optimization:**
* **Resolution:** Downscaled to 480p for lower latency on the network.
* **In-Memory Processing:** Images are piped directly from the camera to Python's memory buffer.
* **Streaming Protocol:** Uses FFmpeg to create a continuous MJPEG stream instead of individual HTTP requests.

## Future Roadmap
* [ ] **Audio Surveillance:** Unlock the microphone for remote listening.
* [ ] **Two-Way Audio:** Use the phone's speakers to "scare" intruders.
* [ ] **Motion Detection:** Simple Python CV logic to record only when movement is detected.

## ⚠️ Disclaimer
This project is for **educational purposes only**. I am not responsible for how you use this software. Please respect privacy laws and do not use this to spy on people without their consent.

---
*Built with 💻 and ☕ by Nikhil!
