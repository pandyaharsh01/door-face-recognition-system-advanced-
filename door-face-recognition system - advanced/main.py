import cv2
import face_recognition
import numpy as np
import os
from datetime import datetime
from utils.face_utils import load_known_faces, encode_face
from logger import log_access

def recognize_faces():
    known_faces, known_names = load_known_faces("data/faces")
    
    # Try different webcam indices
    video_capture = None
    for index in range(3):  # Try indices 0, 1, 2
        video_capture = cv2.VideoCapture(index)
        if video_capture.isOpened():
            break
    if not video_capture or not video_capture.isOpened():
        print("Error: Could not open webcam!")
        return

    # Remove resolution setting temporarily to debug
    # video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    # video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    window_name = "Face Recognition - Press 'q' to quit"
    frame_count = 0
    last_face_locations = []
    last_face_encodings = []
    last_names = []

    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("Error: Failed to read frame from webcam!")
            break

        frame_count += 1

        # Detect faces and encode every 5th frame to reduce load
        if frame_count % 5 == 0:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            last_face_locations = face_recognition.face_locations(rgb_frame, model="hog", number_of_times_to_upsample=1)
            last_face_encodings = face_recognition.face_encodings(rgb_frame, last_face_locations)
            
            # Recognize faces
            last_names = []
            for face_encoding in last_face_encodings:
                matches = face_recognition.compare_faces(known_faces, face_encoding)
                name = "Unknown"
                if True in matches:
                    first_match_index = matches.index(True)
                    name = known_names[first_match_index]
                    log_access(name, "Access Granted")
                else:
                    log_access("Unknown", "Access Denied")
                last_names.append(name)

        # Draw boxes and names using the last detected data
        for (top, right, bottom, left), name in zip(last_face_locations, last_names):
            color = (0, 0, 255)  # Red by default (unrecognized)
            if name != "Unknown":
                color = (0, 255, 0)  # Green if recognized (door unlock)

            # Draw a box around the face with appropriate color
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        cv2.imshow(window_name, frame)

        # Check for 'q' key or window close event
        key = cv2.waitKey(30) & 0xFF
        if key == ord("q") or cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            break

    video_capture.release()
    cv2.destroyAllWindows()