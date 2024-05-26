import time
import cv2
from deepface import DeepFace
import os
import speech_recognition as sr # do not forget pyaudio installation
import threading
import queue
import time
import requests
import gemini
import queue
from serial_interface import sendCommand
import serial
from PIL import Image
from io import BytesIO

BACKEND_URL = 'http://localhost:3000'

# Path to the face database
facesPath = "faces"
os.makedirs(facesPath, exist_ok=True)

# list of people
lock = threading.Lock()
count = len(os.listdir(facesPath))
people = {} # key : id, value: {name, score, x, y, w, h}
# text_results = {}
textQueue = queue.Queue()
personQueue = queue.Queue()

mostRecentFace = None # stores image path reference
publicEnemy = None # stores image path reference

# global event to signal thread termination
stop_event = threading.Event()

# set up serial interface
port = "COM9" # windows, TODO: FIXME

try:
    ser = serial.Serial(port=port, baudrate=115200, timeout=0.1)
except:
    ser = None
    
time.sleep(2)

# identifies faces in webcam view
def recognize_faces(frame):
    # TODO: Jayson needs to add a face that will be associated with the most recent audio
    # TODO: add it to the personQueue
    
    global people

    gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray_image, 1.3, 7, minSize=(40, 40))

    # center of webcam
    centerX, centerY = video_capture.get(cv2.CAP_PROP_FRAME_WIDTH) / 2, video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT) / 2

    # TODO: Jayson needs to add a face that will be associated with the most recent audio, add it to the personQueue
    # variables to help keep track of closest seen face
    closestFace = None
    closestDistance = None

    # locate public enemy
    find_public_enemy()

    # run this code if directory is not empty
    for (x, y, w, h) in faces:
        # Crop the face from the frame
        face = frame[y:y+h, x:x+w]

        try:
            # Check if the face database directory is empty
            if not os.listdir(facesPath):
                print("Face database is empty. Adding person automatically.")
                identity = save_new_face(face)
                print(identity)
                people[identity[0]] = {"name": identity[1], "score" : 0, "x" : x, "y" : y, "w" : w, "h" : h}
            
            # Recognize the face using DeepFace
            result = DeepFace.find(face, db_path=facesPath, enforce_detection=False)
            
            # if we find existing person in existing directory
            if len(result[0]['identity']) != 0: # and result[0].iloc[0]['distance'] < 0.5
                # pulls id from known person (pandas.dataframe --> pandas.Series --> string)
                print("Face Exists")
                identity = result[0]['identity'][0] # in path reference format
                print(identity)
                print(people)
                # updates latest position of face
                with lock:
                    # for actual use
                    people[identity]["x"] = x
                    people[identity]["y"] = y
                    people[identity]["w"] = w
                    people[identity]["h"] = h
                
                # see if face is public enemy
                if identity == publicEnemy:
                    print("Public Enemy in View!!!")
                    # check if the face is closest to the center of the webcam
                    # define a threshold for rough middle of the screen
                    threshold = 100
                    if abs(centerX - x) < threshold and abs(centerY - y) < threshold:
                        print("Public Enemy in the Center!!!")
                        # send command to the serial interface
                        sendCommand("0", ser)
                else: 
                    print(f"No go: {identity} vs {publicEnemy}")

            # if we don't find existing person
            else:
                print("Adding New Face")
                # saving new face into database
                identity = save_new_face(face)
                
                # saving face coordinates in local dictionary
                with lock:
                    people[identity[0]] = {"name" : identity[1], "score" : 0, "x" : x, "y" : y, "w" : w, "h" : h}
                
                # adding a new user to the database
                payload = {
                    "user_id" : identity[1],
                    "image_file" : identity[2],
                    "score" : 0
                }
                
                # post request to add user to the database
                try:
                    response = requests.post(BACKEND_URL + '/sendData', data=payload)
                    response.raise_for_status()
                except requests.exceptions.RequestException as e:
                    print(f"An error occurred: {e}")
                    
            # checks for face closest (assume they're the most recently connected to any audio)
            if closestDistance == None or find_closest_face(x,y, centerX, centerY) < closestDistance:
                closestFace = identity
                closestDistance = find_closest_face(x,y, centerX, centerY)
        
        except Exception as e:
            print(f"Error recognizing face: {e}")
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 4)
            cv2.putText(frame, "Error", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

    personQueue.put(closestFace)
    print(f"Closest Face: {closestFace}")

    return faces

# function to generate unique id
def generate_unique_id():
    # Get the current time in seconds since the epoch
    timestamp = time.time()
    # Convert to a string and remove the decimal point
    unique_id = str(timestamp).replace('.', '')
    return unique_id


# add new face to database
def save_new_face(face):
    global count
    name = generate_unique_id()
    newFacePath = os.path.join(facesPath, f"{name}.jpg")
    count += 1
    cv2.imwrite(newFacePath, face)
    return [newFacePath, name, name + ".jpg"]

# calculate (x,y) distance from center of webcam
def find_closest_face(x, y, centerX, centerY):
    return (centerX - x)**2 + (centerY - y)**2

# find person with the highest red flag
def find_public_enemy():
    global publicEnemy
    # find person with highest red flag
    if people:
        # find user with highest red flag count
        person = max(people, key=lambda p: people[p]['score'])
        redFlag = people[person]

        # only have public enemy if red flags detected
        if redFlag['score'] != 0:
            # keeps track of person with highest red flag
            publicEnemy = person
            print(f"Red Flag: {publicEnemy}")

            # sets text and box frame around person
            # cv2.rectangle(frame, (redFlag['x'], redFlag['y']), (redFlag['x'] + redFlag['w'], redFlag['y'] + redFlag['h']), (0, 0, 255), 4)
            # cv2.putText(frame, "Red Flag", (redFlag['x'], redFlag['y'] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

# run webcam
def web_cam():
    print("Starting Facial Recognition")

    while True:

        # read frames from the video
        result, videoFrame = video_capture.read()  

        # terminate the loop if the frame is not read successfully
        if result is False:
            print("Error reading frame from webcam. Exiting...")
            break 

        # apply the function we created to the video frame
        faces = recognize_faces(videoFrame) 

        # display the processed frame in a window
        cv2.imshow("Discrimination Decimator", videoFrame)  

        # quit process by pressing key "q"
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    print(f"Total People: {count}")
    video_capture.release()
    cv2.destroyAllWindows()

# convert speech to text
def speech_to_text():
    print("Listening")
    while not stop_event.is_set():    
        try:
            # Use the microphone as source for input
            with sr.Microphone() as source2:
                # Adjust the energy threshold based on the surrounding noise level
                r.adjust_for_ambient_noise(source2, duration=0.2)

                print("Say Something:")
                
                # Listen for the user's input 
                audio2 = r.listen(source2)
                
                print("Detected Speech")

                # Using Google to recognize audio
                MyText = r.recognize_google(audio2)
                MyText = MyText.lower()

                print(f"Converted Text: {MyText}")

                # add to the queue
                textQueue.put(MyText)

        except sr.WaitTimeoutError:
            print("Listening timed out, please speak again.")
        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))
        except sr.UnknownValueError:
            print("Unknown error occurred")

if __name__ == "__main__":
    # get everything from the database and put it into a local path
    try:
        response = requests.get(BACKEND_URL + '/getAllData')
        data = response.json()
    
        # populating people dictionary and creating images in specified folder
        for obj in data:
            value = {'score': obj['score'], 'x': 0 , 'y': 0, 'w': 0, 'h': 0}
            file_dic = {obj['user_id'] : value}
            people.update(file_dic)
            
            img_url = obj['url']
            img_data = requests.get(img_url).content
            
            img = Image.open(BytesIO(img_data))
            
            save_path = os.path.join(facesPath, obj['user_id'] + '.png')
            
            img.save(save_path, format='PNG')
            print("Images saved")
        

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
      
    # initialize face classifier and webcam
    face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    video_capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    # local testing without threading
    # web_cam()

    # Initialize gemini to detect red flags
    gem = gemini.GeminiAPI()

    # Initialize the recognizer 
    r = sr.Recognizer() 

    # Create threads for facial recognition and speech recognition
    face_thread = threading.Thread(target=web_cam) # if running without thread use web_cam()
    speech_thread = threading.Thread(target=speech_to_text)

    # Start the threads
    face_thread.start()
    speech_thread.start()

    try:
        while True:
            # process text queue
            if not textQueue.empty():
                text = textQueue.get()
                print(f"Text: {text}")

                # someone has said something, associate it with the newest person in the person queue
                if personQueue.empty():
                    print("No person to associate text with.")
                else:
                    person = personQueue.get()
                    print("Analyzing:", text)

                    # TODO: Send text to Gemini API for red flag detection
                    # TODO: person said something bad increment a red flag, save to database, etc jayson will handle this
                    if gem.analyze_text(text):
                        print("Red Flag")
                        with lock:
                            # text_results[person] = text
                            print(f"Text associated with person: {person}")
                            # increase red flag score
                            people[person]["score"] += 1
                            
                            # increase the persons score in the database
                            payload = {
                                "user_id" : person,
                                "score_to_add": "1"
                            }
                            
                            # update the score on the database
                            # try:
                            response = requests.put(BACKEND_URL + '/updateData', json=payload)
                            response.status_code
                            # except:
                                
                                
                            
                    # fire the gun to deliver the justice javelin
                    if ser is not None:
                        sendCommand("0", ser)

            # Keep the main thread alive
            time.sleep(0.1) 

    except KeyboardInterrupt:
        print("Exiting...")

    finally:
        # Signal threads to stop
        stop_event.set()

        # Give threads time to exit (adjust timeout if needed)
        face_thread.join(timeout=2.0)
        speech_thread.join(timeout=2.0)

        print("Threads stopped.")