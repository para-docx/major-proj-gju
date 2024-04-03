import numpy as np
import cv2
from keras.models import load_model
from collections import deque
import telepot
from datetime import datetime

bot = telepot.Bot('7146566573:AAHk7tR_ijTNU-uQ68kdv1rKguSZjRCA76U')  

def save_annotated_video(input_video, output_video, telegram_group_id):
    print("Loading model ...")
    model = load_model('modelnew.h5')
    Q = deque(maxlen=128)
    
    if isinstance(input_video, int):
        vs = cv2.VideoCapture(input_video)
        webcam = True
    else:
        vs = cv2.VideoCapture(input_video)
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
                bot.sendPhoto(telegram_group_id, open('alert_frame.jpg', 'rb'), caption=message)


        text = "Misbehavior: {}".format(label)
        FONT = cv2.FONT_HERSHEY_SIMPLEX

        cv2.putText(output, text, (35, 50), FONT, 1.25, text_color, 3)

        out.write(output)
        bot.sendVideo(telegram_group_id, open(output_video_file, 'rb'), caption="saved video")
        

        cv2.imshow("Crime Detection", output)

        key = cv2.waitKey(1) & 0xFF
        frame_count += 1

        if key == ord("q"):
            break

    print("[INFO] Cleaning up...")
    vs.release()
    out.release()  
    cv2.destroyAllWindows()

input_video = 'Yakuza.mp4'
output_video_file = 'saved_video.mp4'  
telegram_group_id = '-4123159653' 
save_annotated_video(input_video, output_video_file, telegram_group_id)