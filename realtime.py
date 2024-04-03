import numpy as np
import argparse
import cv2
from keras.models import load_model
from collections import deque
import telepot
import time
from datetime import datetime

# bot = telepot.Bot('6679358098:AAFmpDc7o4MwqDywDahyAK0Qq89IVZqNr04')  

def save_annotated_video(rtsp_cam, output_video, telegram_group_id):
    print("Loading model ...")
    model = load_model('modelnew.h5')
    Q = deque(maxlen=128)
    
    if isinstance(rtsp_cam, int):
        vs = cv2.VideoCapture(rtsp_cam)
        webcam = True
    else:
        vs = cv2.VideoCapture(rtsp_cam)
        webcam = False
    
    (W, H) = (None, None)
    violence_detected = False
    violence_start_frame = None
    frame_count = 0
    

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_video, fourcc, 30.0, (1280, 720)) 

    smoothing_window = 10  
    prediction_history = deque(maxlen=smoothing_window)

    while True:
        (grabbed, frame) = vs.read()

        if not grabbed:
            break

        if W is None or H is None:
            (H, W) = frame.shape[:2]

        output = frame.copy()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (128, 128)).astype("float32")
        frame = frame.reshape(128, 128, 3) / 255

        preds = model.predict(np.expand_dims(frame, axis=0))[0]
        Q.append(preds)

        results = np.array(Q).mean(axis=0)
        i = (preds > 0.50)[0]
        prediction_history.append(i)

        smoothed_prediction = np.mean(prediction_history) > 0.5
        label = smoothed_prediction

        text_color = (0, 255, 0) 

        if label:
            text_color = (0, 0, 255)
            
            if not violence_detected:
                violence_detected = True
                violence_start_frame = frame_count
                
        else:
            violence_detected = False

        if violence_detected and frame_count == violence_start_frame + 30:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            message = f"Violence detected at {current_time}"
            with open('alert_frame.jpg', 'wb') as f:
                cv2.imwrite('alert_frame.jpg', frame * 255)
                # bot.sendPhoto(telegram_group_id, open('alert_frame.jpg', 'rb'), caption=message)

        text = "Misbehaviour: {}".format(label)
        FONT = cv2.FONT_HERSHEY_SIMPLEX

        cv2.putText(output, text, (35, 50), FONT, 1.25, text_color, 3)

        out.write(output)

        cv2.imshow("Crime Detection", output)

        key = cv2.waitKey(1) & 0xFF
        frame_count += 1

        if key == ord("q"):
            break

    print("[INFO] Cleaning up...")
    vs.release()
    out.release()  
    cv2.destroyAllWindows()

def toggle_input_source():
        rtsp_cam = input("Enter 'v' for video or 'c' for live camera feed: ")
        if rtsp_cam == 'v':
            return 'Yakuza.mp4'  # Replace with your video file path
        elif rtsp_cam == 'c':
            return 1  # Use webcam (usually device ID 0)
        else:
            print("Invalid input. Please enter 'v' or 'c'.")
            return toggle_input_source()


rtsp_cam = toggle_input_source()
output_video_file = 'annotated_video.avi'  
telegram_group_id = '-949413618' 
save_annotated_video(rtsp_cam, output_video_file, telegram_group_id)