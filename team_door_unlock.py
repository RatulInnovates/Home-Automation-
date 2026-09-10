import cv2
import face_recognition
import numpy as np
from picamera2 import Picamera2

# 1. Initialize the Syntax Terrorists team database
known_face_encodings = []
known_face_names = []

def load_team_member(file_path, name):
    try:
        image = face_recognition.load_image_file(file_path)
        encoding = face_recognition.face_encodings(image)[0]
        known_face_encodings.append(encoding)
        known_face_names.append(name)
        print(f"Successfully loaded profile for {name}.")
    except Exception as e:
        print(f"Error loading {file_path}. Ensure the image exists.")

print("Booting up security database...")
load_team_member("team_faces/ibtid.jpg", "Ibtid")
# load_team_member("team_faces/sourav.jpg", "Sourav")
# load_team_member("team_faces/supty.jpg", "Supty")
# load_team_member("team_faces/urbashi.jpg", "Urbashi")
# load_team_member("team_faces/sadika.jpg", "Sadika")

# 2. Configure PiCamera2
picam2 = Picamera2()
config = picam2.create_video_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()

print("\nCamera active. Look at the monitor window... Press 'q' to quit.")

try:
    while True:
        # Capture frame and strip the 4th Alpha channel
        frame = picam2.capture_array()
        frame = frame[:, :, :3].copy()
        
        # Convert BGR (OpenCV color space) to RGB (face_recognition color space)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Locate all faces and compute their encodings
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        # Loop through each face found in the frame
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Check if the face matches our team
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
            name = "Unknown"
            box_color = (0, 0, 255) # Red for unknown

            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                    box_color = (0, 255, 0) # Green for team members
                    print(f"[{name} Detected] -> SUCCESS: Opening the door...")

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), box_color, 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), box_color, cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Display the resulting image on your monitor
        cv2.imshow('Smart Edge Security - Syntax Terrorists', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("\nShutting down...")
finally:
    picam2.stop()
    cv2.destroyAllWindows()