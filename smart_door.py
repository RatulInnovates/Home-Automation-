import os
os.environ["GPIOZERO_PIN_FACTORY"] = "lgpio"

import cv2
import face_recognition
import numpy as np
import time
from picamera2 import Picamera2
from gpiozero import MotionSensor

from door_state import record_activity

# 1. Initialize the Syntax Terrorists database
known_face_encodings = []
known_face_names = []
base_dir = "team_faces"

print("Booting up security database...")
for filename in os.listdir(base_dir):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        filepath = os.path.join(base_dir, filename)
        person_name = os.path.splitext(filename)[0].capitalize() 
        try:
            image = face_recognition.load_image_file(filepath)
            encodings = face_recognition.face_encodings(image)
            if len(encodings) > 0:
                known_face_encodings.append(encodings[0])
                known_face_names.append(person_name)
                print(f"Successfully loaded profile for {person_name}")
        except Exception as e:
            print(f"Error reading {filename}: {e}")

print(f"Total biometric profiles loaded: {len(known_face_encodings)}")

# 2. Configure Hardware (PIR on GPIO 27 & Picamera2)
pir = MotionSensor(27)

picam2 = Picamera2()
config = picam2.create_video_configuration(main={"size": (640, 480)})
picam2.configure(config)

print("\nSystem Armed. Waiting for motion... (Press Ctrl+C to quit)")

try:
    while True:
        # Step 1: Wait quietly for PIR motion
        pir.wait_for_motion()
        print("\nMotion Detected! Booting camera for facial scan...")
        picam2.start()
        
        # Step 2: 30-second evaluation window for unknown/uncertain faces
        scan_start_time = time.time()
        known_detected = False
        
        while (time.time() - scan_start_time) < 30.0:
            # Capture frame, strip Alpha channel, force memory copy
            frame = picam2.capture_array()
            frame = frame[:, :, :3].copy()
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.45)
                name = "Unknown"
                box_color = (0, 0, 255) # Red for strangers

                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]
                        box_color = (0, 255, 0) # Green for team members
                        print(f"[{name} Detected] -> SUCCESS: Opening the door!")
                        record_activity("entry", f"{name} entered through the smart door.", person=name)
                        known_detected = True
                        break # Break face loop on successful match

                # Draw bounding boxes and text labels
                cv2.rectangle(frame, (left, top), (right, bottom), box_color, 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), box_color, cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

            cv2.imshow('Smart Edge Security - Syntax Terrorists', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                raise KeyboardInterrupt

            # If a known person was successfully recognized, exit the 30-second loop immediately
            if known_detected:
                break

        # Step 3: Shutdown camera and re-arm PIR
        print("Closing camera and re-arming PIR sensor...")
        picam2.stop()
        cv2.destroyAllWindows()
        
        if not known_detected:
            print("Scan window ended. No authorized team member confirmed. Door remains locked.")
            
        print("\nSystem Re-armed. Waiting for motion...")

except KeyboardInterrupt:
    print("\nShutting down system...")
finally:
    picam2.stop()
    cv2.destroyAllWindows()