import cv2
import numpy as np
import time
from tflite_runtime.interpreter import Interpreter
from picamera2 import Picamera2

# Load the TFLite model and allocate tensors
interpreter = Interpreter(model_path="/home/pi/Ratul/detect.tflite")
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]

# Initialize Picamera2 natively (No OpenCV VideoCapture)
picam2 = Picamera2()
config = picam2.create_video_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()

print("Starting AI Person Detection... Press Ctrl+C to quit.")

try:
    while True:
        # Capture frame directly from the Pi 5 camera stack
        frame = picam2.capture_array()

        # Strip the 4th Alpha channel (keep only the first 3 channels)
        frame = frame[:, :, :3]

        # Pre-process the frame for the TFLite model
        resized_frame = cv2.resize(frame, (width, height))
        input_data = np.expand_dims(resized_frame, axis=0)

        # Run local AI inference
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()

        # Retrieve detection results
        classes = interpreter.get_tensor(output_details[1]['index'])[0]
        scores = interpreter.get_tensor(output_details[2]['index'])[0]

        # Check all detected objects in the current frame
        for i in range(len(scores)):
            if scores[i] > 0.6: # 60% confidence threshold
                # Class 0 in the standard COCO dataset is 'person'
                if int(classes[i]) == 0:
                    print("Intruder Detected: Person found in frame!")
                    break
        
        time.sleep(0.5) # Pause briefly to prevent console spam

except KeyboardInterrupt:
    print("\nExiting...")
finally:
    picam2.stop()