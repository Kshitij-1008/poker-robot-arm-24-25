import os
import subprocess
import time
from datetime import datetime
from ultralytics import YOLO
import torch

Wifi = False
Phone_IPs = {"Kshitij": "10.205.87.179", "Alif": "10.205.12.186", "Joon": "10.205.225.100", "Saif": "10.205.110.243"}
if Wifi:
    # Replace with your phone's IP
    PHONE_IP = Phone_IPs["Alif"]
    ADB_PORT = "5555"

    def connect_wifi_adb():
        subprocess.run(rf".\adb connect {PHONE_IP}:{ADB_PORT}", shell=True)

    # Add this at the start of your script
    connect_wifi_adb()

# Config
PHOTOS_DIR_ON_PHONE = "/sdcard/DCIM/Camera/"  # Default Samsung camera folder
SAVE_FOLDER_ON_PC = "D:\\platform-tools\\AndroidCamera\\"   # Your desired save location

# Create save folder if it doesn't exist
os.makedirs(SAVE_FOLDER_ON_PC, exist_ok=True)

def take_and_save_photo():
    # 1. Simulate volume key press (capture photo)
    subprocess.run([r".\adb", "shell", "input keyevent KEYCODE_VOLUME_DOWN"], shell=True)
    
    # Wait for the phone to save the image (adjust delay if needed)
    time.sleep(2)  
    
    # 2. Get the latest file in the phone's camera folder
    latest_photo = subprocess.run(
        [r".\adb", "shell", f"ls -t {PHOTOS_DIR_ON_PHONE} | head -n 1"],
        capture_output=True, text=True, shell=True
    ).stdout.strip()
    
    if latest_photo:
        # 3. Generate a unique filename (prevents overwrites)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pc_filename = f"photo_{timestamp}.jpg"
        
        # 4. Pull the photo to the PC
        subprocess.run([
            r".\adb", "pull", 
            f"{PHOTOS_DIR_ON_PHONE}{latest_photo}", 
            f"{SAVE_FOLDER_ON_PC}{pc_filename}"
        ], shell=True)
        print(f"Saved: {SAVE_FOLDER_ON_PC}{pc_filename}")

        # 5. Free up phone space
        subprocess.run([r".\adb", "shell", f"rm {PHOTOS_DIR_ON_PHONE}{latest_photo}"], shell=True)
    else:
        print("Error: No photo found!")

# Trigger on spacebar press (using `keyboard` lib)
import keyboard
keyboard.add_hotkey('space', callback=take_and_save_photo)
print("Press SPACE to take a photo. Press ESC to exit.")
keyboard.wait('esc')  # Exit on ESC key


device = 'cuda' if torch.cuda.is_available() else 'cpu'
# Model inference
model = YOLO("D:\\HDD Data\\Computer Vision\\yolov8_large_segment\\runs\\segment\\train\\weights\\best.pt")

image_folder = r"D:\platform-tools\AndroidCamera"
image_name = os.listdir(image_folder)[-1]
image_path = os.path.join(image_folder, image_name)
result = model.predict(source=image_path, 
                       conf=0.7, iou=0.8, imgsz=1280,
                       save=True, device=device) 