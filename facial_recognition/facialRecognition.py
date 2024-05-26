import cv2
from deepface import DeepFace
import os
import random
import speech_recognition as sr
import numpy as np
import pyttsx3
import threading
import requests
import queue
import time
import requests

BACKEND_URL = 'http://localhost:3000'

# Path to the face database
facesPath = "facial_recognition/faces"
os.makedirs(facesPath, exist_ok=True)

# list of people
lock = threading.Lock()
count = len(os.listdir(facesPath))
people = {} # filename -> {redFlagCount, x-coord, y-coord, width, height}
text_results = {}

# test function (delete later)
def detect_faces(frame):
    gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray_image, 1.1, 5, minSize=(40, 40))
    
    # create box around the face
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 4)
    
    return faces

# identifies faces in webcam view
def recognize_faces(frame):
    gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray_image, 1.3, 7, minSize=(40, 40))

    # run this code if directory is not empty
    for (x, y, w, h) in faces:
        # Crop the face from the frame
        face = frame[y:y+h, x:x+w]

        try:
            # Check if the face database directory is empty
            if not os.listdir(facesPath):
                print("Face database is empty. Adding person automatically.")
                save_new_face(face)
            
            # Recognize the face using DeepFace
            result = DeepFace.find(face, db_path=facesPath, enforce_detection=False)
            
            # if we find existing person in existing directory
            if len(result[0]['identity']) != 0: # and result[0].iloc[0]['distance'] < 0.5
                # pulls id from known person (pandas.dataframe --> pandas.Series --> string)
                print("Face Exists")
                identity = result[0]['identity'][0]
                with lock:
                    people[identity] = {"redFlag" : random.randint(0, 10), "x" : x, "y" : y, "w" : w, "h" : h}

                # sets text and box frame around person
                # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 4)
                # cv2.putText(frame, identity.split("/")[-1], (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            
            # if we don't find existing person
            else:
                # saving new face
                print("Adding New Face")
                identity = save_new_face(face)
                with lock:
                    people[identity] = people[identity] = {"redFlag" : random.randint(0, 10), "x" : x, "y" : y, "w" : w, "h" : h}

                # sets text and box frame around person
                # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 4)
                # cv2.putText(frame, identity.split("/")[-1], (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        except Exception as e:
            print(f"Error recognizing face: {e}")
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 4)
            cv2.putText(frame, "Error", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

        if people:
            # find user with highest red flag count
            print(f"All people: {people}")
            redFlag = max(people, key=lambda p: people[p]['redFlag'])
            redFlag = people[redFlag]
            print(f"Red Flag: {redFlag}")

            # sets text and box frame around person
            cv2.rectangle(frame, (redFlag['x'], redFlag['y']), (redFlag['x'] + redFlag['w'], redFlag['y'] + redFlag['h']), (0, 0, 255), 4)
            cv2.putText(frame, "Red Flag", (redFlag['x'], redFlag['y'] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

    # people.clear()
    return faces

# add new face to database
def save_new_face(face):
    global count
    newFacePath = os.path.join(facesPath, f"person_{count}.jpg")
    count += 1
    cv2.imwrite(newFacePath, face)
    return newFacePath

# run webcame
def web_cam():
    print("Starting Facial Recognition")

    while True:

        # read frames from the video
        result, videoFrame = video_capture.read()  

        # terminate the loop if the frame is not read successfully
        if result is False:
            break 

        # apply the function we created to the video frame
        faces = recognize_faces(videoFrame) 
        # faces = detect_faces(videoFrame)

        # display the processed frame in a window named "My Face Detection Project"
        cv2.imshow("Amelio", videoFrame)  

        # quit process by pressing key "q"
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    print(f"Total People: {count}")
    video_capture.release()
    cv2.destroyAllWindows()

# convert text to speech
def speak_text(command):
    # Initialize the engine
    engine = pyttsx3.init()
    engine.say(command) 
    engine.runAndWait()

def speech_to_text():
    while True:    
        try:
            # Use the microphone as source for input
            with sr.Microphone() as source2:
                # Adjust the energy threshold based on the surrounding noise level
                r.adjust_for_ambient_noise(source2, duration=0.2)
                
                # Listen for the user's input 
                audio2 = r.listen(source2)
                
                # Using Google to recognize audio
                MyText = r.recognize_google(audio2)
                MyText = MyText.lower()

                print(f"Text Detected: {MyText}")

                # if speech recognized, associate it with the latest recognized face
                if people:
                    center_x, center_y = video_capture.get(cv2.CAP_PROP_FRAME_WIDTH) / 2, video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT) / 2
                    latest_person = max(people, key=lambda p: ((p['x'] + p['w'] / 2) - center_x) ** 2 + ((p['y'] + p['h'] / 2) - center_y) ** 2)
                    with lock:
                        text_results[latest_person] = MyText
                    print(f"Speech associated with person: {latest_person}")

                speak_text(MyText)

        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))
        except sr.UnknownValueError:
            print("Unknown error occurred")

if __name__ == "__main__":
    # initialize face classifier and webcam
    face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    video_capture = cv2.VideoCapture(0)

    # Initialize the recognizer 
    r = sr.Recognizer() 

    # Create threads for facial recognition and speech recognition
    # face_thread = threading.Thread(target=web_cam)
    speech_thread = threading.Thread(target=speech_to_text)

    # Start the threads
    # face_thread.start()
    speech_thread.start()

    # Wait for both threads to finish
    # face_thread.join()
    speech_thread.join()