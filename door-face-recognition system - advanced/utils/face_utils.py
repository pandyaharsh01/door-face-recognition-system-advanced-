import os
import face_recognition
import cv2
import numpy as np

def save_face(name, frame, save_dir="data/faces"):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    face_path = os.path.join(save_dir, f"{name}.jpg")
    cv2.imwrite(face_path, frame)
    return face_path

def encode_face(image_path):
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)
    if encodings:
        encoding_path = image_path.replace(".jpg", ".npy")
        np.save(encoding_path, encodings[0])
        return True
    return False

def load_known_faces(save_dir="data/faces"):
    known_faces = []
    known_names = []
    for filename in os.listdir(save_dir):
        if filename.endswith(".npy"):
            name = filename.replace(".npy", "")
            encoding = np.load(os.path.join(save_dir, filename))
            known_faces.append(encoding)
            known_names.append(name)
    return known_faces, known_names

def delete_face(name, save_dir="data/faces"):
    # Delete the face image and encoding files
    image_path = os.path.join(save_dir, f"{name}.jpg")
    encoding_path = os.path.join(save_dir, f"{name}.npy")
    
    if os.path.exists(image_path):
        os.remove(image_path)
    if os.path.exists(encoding_path):
        os.remove(encoding_path)
    
    return True