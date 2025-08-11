import customtkinter as ctk
import cv2
import os
from tkinter import messagebox
from utils.face_utils import save_face, encode_face, load_known_faces, delete_face
from main import recognize_faces
import face_recognition
from PIL import Image, ImageTk

def create_login_frame(root, on_success):
    frame = ctk.CTkFrame(root)
    frame.pack(expand=True, fill="both", padx=20, pady=20)

    ctk.CTkLabel(frame, text="Admin Login", font=("Arial", 20)).pack(pady=10)
    
    username_entry = ctk.CTkEntry(frame, placeholder_text="Username")
    username_entry.pack(pady=5)
    
    password_entry = ctk.CTkEntry(frame, placeholder_text="Password", show="*")
    password_entry.pack(pady=5)
    
    def check_login():
        if username_entry.get() == "admin" and password_entry.get() == "password":
            on_success()
        else:
            messagebox.showerror("Login Failed", "Invalid credentials! Please try again.")
    
    ctk.CTkButton(frame, text="Login", command=check_login).pack(pady=10)
    return frame

def create_dashboard_frame(root):
    frame = ctk.CTkFrame(root)
    frame.pack(expand=True, fill="both", padx=20, pady=20)

    ctk.CTkLabel(frame, text="Face Recognition Dashboard", font=("Arial", 20)).pack(pady=10)
    
    def add_face():
        # Open webcam
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Error", "Could not open webcam! Please check if webcam is connected.")
            return

        # Create a new window for webcam feed
        webcam_window = ctk.CTkToplevel()
        webcam_window.title("Add Face - Webcam")
        webcam_window.geometry("800x600")

        # Label to display status
        status_label = ctk.CTkLabel(webcam_window, text="Align your face in the frame", font=("Arial", 14))
        status_label.pack(pady=10)

        # Label to display the webcam feed
        video_label = ctk.CTkLabel(webcam_window, text="")  # Empty text to hold the video feed
        video_label.pack(pady=10)

        # Variable to control the webcam loop
        is_capturing = [True]  # Using a list to allow modification in nested function
        frame_count = [0]  # To control face detection frequency
        last_face_locations = []  # To store last detected face locations

        def on_closing():
            is_capturing[0] = False  # Stop the webcam loop
            cap.release()
            webcam_window.destroy()

        # Bind the "X" button to the on_closing function
        webcam_window.protocol("WM_DELETE_WINDOW", on_closing)

        def capture_face():
            ret, frame = cap.read()
            if ret:
                name = ctk.CTkInputDialog(text="Enter name:", title="Add Face").get_input()
                if name:
                    face_path = save_face(name, frame, "data/faces")
                    if encode_face(face_path):
                        status_label.configure(text=f"Face added for {name}", text_color="green")
                    else:
                        status_label.configure(text="Failed to encode face", text_color="red")
                    is_capturing[0] = False  # Stop the webcam loop
            else:
                status_label.configure(text="Failed to capture image", text_color="red")

        # Add a "Capture" button
        capture_button = ctk.CTkButton(webcam_window, text="Capture", command=capture_face)
        capture_button.pack(pady=10)

        # Adjusted webcam logic for Add Face
        while is_capturing[0]:
            ret, frame = cap.read()
            if not ret:
                messagebox.showerror("Error", "Failed to read frame from webcam! Closing window.")
                is_capturing[0] = False
                break

            frame_count[0] += 1

            # Detect faces every 5th frame to reduce load
            if frame_count[0] % 5 == 0:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                last_face_locations = face_recognition.face_locations(rgb_frame, model="hog", number_of_times_to_upsample=1)

            # Draw green boxes around detected faces
            for (top, right, bottom, left) in last_face_locations:
                color = (0, 255, 0)  # Always green for Add Face
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)

            # Convert the frame to a format suitable for customtkinter
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame_rgb)
            image = image.resize((640, 480), Image.Resampling.LANCZOS)  # Resize for better display
            photo = ImageTk.PhotoImage(image)
            
            # Update the video label with the new frame
            video_label.configure(image=photo)
            video_label.image = photo  # Keep a reference to avoid garbage collection

            # Process Tkinter events
            webcam_window.update()

        # Release the webcam when done
        cap.release()

    def delete_face_window():
        # Create a new window for deleting faces
        delete_window = ctk.CTkToplevel()
        delete_window.title("Delete Faces")
        delete_window.geometry("400x300")

        # Label for the window
        ctk.CTkLabel(delete_window, text="Select a face to delete", font=("Arial", 16)).pack(pady=10)

        # Create a scrollable frame for the list of faces
        scrollable_frame = ctk.CTkScrollableFrame(delete_window)
        scrollable_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Get the list of faces
        _, known_names = load_known_faces("data/faces")
        
        if not known_names:
            ctk.CTkLabel(scrollable_frame, text="No faces found!", font=("Arial", 14)).pack(pady=10)
            return

        # Add each face to the list with a delete button
        for name in known_names:
            face_frame = ctk.CTkFrame(scrollable_frame)
            face_frame.pack(fill="x", pady=5)

            ctk.CTkLabel(face_frame, text=name, font=("Arial", 14)).pack(side="left", padx=10)

            def create_delete_handler(face_name):
                def delete_handler():
                    delete_face(face_name)
                    messagebox.showinfo("Success", f"Face '{face_name}' deleted successfully!")
                    delete_window.destroy()
                    delete_face_window()  # Refresh the window
                return delete_handler

            delete_button = ctk.CTkButton(face_frame, text="Delete", fg_color="red", command=create_delete_handler(name))
            delete_button.pack(side="right", padx=10)

    # Variable to prevent multiple "Start Recognition" instances
    is_recognizing = [False]

    def start_recognition_wrapper():
        if not is_recognizing[0]:
            is_recognizing[0] = True
            recognize_faces()
            is_recognizing[0] = False

    ctk.CTkButton(frame, text="Add Face", command=add_face).pack(pady=5)
    ctk.CTkButton(frame, text="Start Recognition", command=start_recognition_wrapper).pack(pady=5)
    ctk.CTkButton(frame, text="Delete Face", command=delete_face_window).pack(pady=5)
    
    return frame