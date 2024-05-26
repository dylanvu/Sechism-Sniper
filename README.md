
# venus-hacks-2024

HackAtUCI + WiCS = Venus Hacks 2024

## Send Data to Database
**/sendData**

*Request:*
- Header: form-data
- user_id: text
- image_file: File
- score: number

*Response:*
```json
{
"user_id": "ab123",
"score": 1,
"fileName": "baldgate.png",
"fileUrl": "https://storage.googleapis.com/venushacks2024-777a4.appspot.com/baldgate.png"
}
```

## Get Data from Database
**/getData**

*Request:*
- Header: application/json

```json
data {
"user_id": 1234abc
}
```


# Facial Recognition
pip install opencv-python

pip install deepface

pip install speechrecognition

pip install pyaudio
    - if missing dependencies do "brew install portaudio" and try command again

pip install pyttsx3