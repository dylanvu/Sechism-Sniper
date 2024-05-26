
# venus-hacks-2024

HackAtUCI + WiCS = Venus Hacks 2024

## Send Data to Database
**/sendData**
Adds a user to the data base.

*POST Request:*
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
*Error Response:*
- Sends error message no json

## Get Data from Database
**/getData**
Retrieves a user in the data base. 

*GET Request:*
- http://localhost:3000/getData?user_id=1234
- API URL/getData?user_id={unique id for each user}

*Response:*
```json
[
    {
        "ab123": {
            "score": "1",
            "user_id": "ab123",
            "url": "https://storage.googleapis.com/venushacks2024-777a4.appspot.com/baldgate.png"
        }
    }
]
```
*Error Response:* 
```json
{
    "error": "-1",
    "note": "there is no document with this user_id"
}
```

## Update Data from Database
**/updateData**
Updates an existing user in the database. Returns a -1 in error, when this happens call the route to /sendData and then call this route /updateData again.

*PUT Request:*
```json
{
    "user_id": "ab123",
    "score_to_add:" "1"
}
```

*Response:*
- String: "Score Updated"
- Check in database if update worked

*Error Response:*
```json
{
    "error": "-1",
    "note": "add user to data base first, then call this route again"
}
```

## Get Top Score From Database
**/topScore**
Retrieves the user data for who has the top score so far.

*GET Request:*
- http://localhost:3000/topScore
- API URL/topScore

*Response:*
```
json
{
    "score": "1",
    "user_id": "ab123",
    "url": "https://storage.googleapis.com/venushacks2024-777a4.appspot.com/baldgate.png"
}
```

*Error Response:*
```
json
{
    "error": "-1",
    "note": "no users found"
}
```
## Get All Data From Database
**/topScore**
Retrieves the every user data

*GET Request:*
- http://localhost:3000/getAllData
- API URL/getAllData

*Response:*
```
json
[
    {
        "id": "ab123",
        "score": "1",
        "user_id": "ab123",
        "url": "https://storage.googleapis.com/venushacks2024-777a4.appspot.com/baldgate.png"
    },
    {
        "id": "alovelace",
        "last": "Lovelace",
        "born": 1815,
        "first": "Ada"
    }
]
```

*Error Response:*
```
json 
{
   "error": "-1",
    "note": "database is empty"
}
```

```
json
{
    "error": "-2",
    "note": "unable to get data from database but it's not empty"
}
```

## Facial Recognition
pip install opencv-python

pip install deepface

pip install speechrecognition

pip install pyaudio
    - if missing dependencies do "brew install portaudio" and try command again

pip install pyttsx3