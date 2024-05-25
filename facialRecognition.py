import cv2
from deepface import DeepFace
import os

# Path to the face database
facesPath = "faces"
os.makedirs(facesPath, exist_ok=True)

# local list of people
people = [files for files in os.listdir(facesPath)]

def detect_faces(frame):
    gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray_image, 1.1, 5, minSize=(40, 40))
    
    # create box around the face
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 4)
    
    return faces

def recognize_faces(frame):
    gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray_image, 1.1, 5, minSize=(40, 40))

    # Check if the face database directory is empty
    if not os.listdir(facesPath):
        print("Face database is empty. Adding person automatically.")
        for (x, y, w, h) in faces:
            # Save unrecognized face
            face = frame[y:y+h, x:x+w]
            identity = save_new_face(face)
            people.append(identity)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 4)
            cv2.putText(frame, identity.split("/")[-1], (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        
        return faces

    # run this code if directory is not empty
    for (x, y, w, h) in faces:
        # Crop the face from the frame
        face = frame[y:y+h, x:x+w]
        try:
            # Recognize the face using DeepFace
            result = DeepFace.find(face, db_path=facesPath, enforce_detection=False)
            
            # if we find existing person
            if len(result[0]['identity']) != 0:
                # pulls id from known person (pandas.dataframe --> pandas.Series --> string)
                print("Face Exists")
                # print(len(result[0]['identity']))
                # print(result[0]['identity'])
                identity = result[0]['identity'][0]
                people.append(identity)
                # sets text and box frame around person
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 4)
                cv2.putText(frame, identity.split("/")[-1], (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            # saving new face
            else:
                print("Adding New Face")
                identity = save_new_face(face)
                people.append(identity)
                # sets text and box frame around person
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 4)
                cv2.putText(frame, identity.split("/")[-1], (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        except Exception as e:
            print(f"Error recognizing face: {e}")
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 4)
            cv2.putText(frame, "Error", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

    return faces

def save_new_face(face):
    count = len(people) + 1
    newFacePath = os.path.join(facesPath, f"person_{count}.jpg")
    cv2.imwrite(newFacePath, face)
    return newFacePath


face_classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
video_capture = cv2.VideoCapture(0)

print("Starting Facial Recognition")

while True:

    # read frames from the video
    result, videoFrame = video_capture.read()  

    # terminate the loop if the frame is not read successfully
    if result is False:
        break 

    # apply the function we created to the video frame
    faces = recognize_faces(videoFrame) 

    # display the processed frame in a window named "My Face Detection Project"
    cv2.imshow("Amelio", videoFrame)  

    # quit process by pressing key "q"
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

print(f"Total People: {len(people)}")
video_capture.release()
cv2.destroyAllWindows()