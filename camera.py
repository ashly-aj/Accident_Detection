import os

# Set environment variable explicitly in Python
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"



import cv2
from detection import AccidentDetectionModel
import numpy as np
import os
import winsound
import threading
import time
import tkinter as tk

from PIL import Image, ImageTk  # Import PIL modules for image handling

emergency_timer = None
alarm_triggered = False  # Flag to track if an alarm has been triggered

model = AccidentDetectionModel("model.json", "model_weights.keras")
font = cv2.FONT_HERSHEY_SIMPLEX

def save_accident_photo(frame):
    try:
        current_date_time = time.strftime("%Y-%m-%d-%H%M%S")
        directory = "accident_photos"
        if not os.path.exists(directory):
            os.makedirs(directory)
        filename = f"{directory}/{current_date_time}.jpg"
        cv2.imwrite(filename, frame)
        print(f"Accident photo saved as {filename}")
    except Exception as e:
        print(f"Error saving accident photo: {e}")

        



def show_alert_message():
   

    # Play the beep sound
    frequency = 2500  
    duration = 2000  
    winsound.Beep(frequency, duration)

    alert_window = tk.Tk()
    alert_window.title("Alert")
    alert_window.geometry("500x250")  # Adjust window size to fit the GIF and message box
    alert_label = tk.Label(alert_window, text="Alert: Accident Detected!\n\nIs the Accident Critical?", fg="black", font=("Helvetica", 16))
    alert_label.pack()

    # Load and display the GIF
    gif_path = "red-alert.gif" # Replace with the actual path to your GIF
    gif = Image.open(gif_path)
    resized_gif = gif.resize((150, 100), Image.BICUBIC)  # Use Image.BICUBIC for resizing

    try:
        global gif_image  # Create a global variable to hold the reference to the image object
        gif_image = ImageTk.PhotoImage(resized_gif)
        gif_label = tk.Label(alert_window, image=gif_image)
        gif_label.pack()
    except Exception as e:
        print(f"Error loading GIF: {e}")



    cancel_button = tk.Button(alert_window, text="Cancel", command=alert_window.destroy)
    cancel_button.pack()

    alert_window.mainloop()
    
def start_alert_thread():
    alert_thread = threading.Thread(target=show_alert_message)
    alert_thread.daemon = True  # Set the thread as daemon so it doesn't block the main thread
    alert_thread.start()

def startapplication():
    global alarm_triggered  # Use global variable for tracking alarm status
    video = cv2.VideoCapture("test_video3.mp4") 
    while True:
        ret, frame = video.read()
        if not ret:
            print("No more frames to read")
            break
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        roi = cv2.resize(gray_frame, (250, 250))

        pred, prob = model.predict_accident(roi[np.newaxis, :, :])
        if pred == "Accident" and not alarm_triggered:
            prob = round(prob[0][0] * 100, 2)
            print(prob)
            
            if prob >99.5:
                # frequency = 2500  
                # duration = 2000  
                # winsound.Beep(frequency, duration)
                save_accident_photo(frame)
                alarm_triggered = True  # Set the alarm_triggered flag to True
                start_alert_thread()  # Start the alert message thread

            cv2.rectangle(frame, (0, 0), (280, 40), (0, 0, 0), 1)
            cv2.putText(frame, pred + " " + str(prob), (20, 30), font, 1, (255,255,255), 2)

        if cv2.waitKey(33) & 0xFF == ord('q'):
            return
        cv2.imshow('Video', frame)  



startapplication()