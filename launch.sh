#!/bin/bash
# 1. Go to project folder
cd /home/skpi/Sinine-kapp

# 2. Update code from Thor-V2 branch
git pull origin Thor-V2

# 3. Create a Virtual Camera at /dev/video1
sudo modprobe v4l2loopback video_nr=1 card_label="VirtualCam" exclusive_caps=1

# 4. Start sending real camera footage to Virtual Camera (in the background)
# We use & at the end to keep this running while the app starts
rpicam-vid -t 0 --inline --width 640 --height 480 --framerate 30 --codec yuv420 -o - | ffmpeg -loglevel quiet -re -i - -f v4l2 /dev/video1 &

# 5. Wait 2 seconds for camera to warm up
sleep 2

# 6. Run the App (Pointing to the Virtual Camera)
# We pass an environment variable so Kivy knows which camera to use
export KIVY_CAMERA=opencv
./venv/bin/python main.py
