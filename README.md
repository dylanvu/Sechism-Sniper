# venus-hacks-2024

HackAtUCI + WiCS = Venus Hacks 2024

## Send Data to Database

**/sendData**
Adds a user to the data base.

_POST Request:_

- Header: form-data
- user_id: text
- image_file: File
- score: number

_Response:_

```json
{
  "user_id": "ab123",
  "score": 1,
  "fileName": "baldgate.png",
  "fileUrl": "https://storage.googleapis.com/venushacks2024-777a4.appspot.com/baldgate.png"
}
```

_Error Response:_

- Sends error message no json

## Get Data from Database

**/getData**
Retrieves a user in the data base.

_GET Request:_

- http://localhost:3000/getData?user_id=1234
- API URL/getData?user_id={unique id for each user}

_Response:_

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

_Error Response:_

```json
{
  "error": "-1",
  "note": "there is no document with this user_id"
}
```

## Update Data from Database

**/updateData**
Updates an existing user in the database. Returns a -1 in error, when this happens call the route to /sendData and then call this route /updateData again.

_PUT Request:_

```json
{
    "user_id": "ab123",
    "score_to_add:" "1"
}
```

_Response:_

- String: "Score Updated"
- Check in database if update worked

_Error Response:_

```json
{
  "error": "-1",
  "note": "add user to data base first, then call this route again"
}
```

## Get Top Score From Database

**/topScore**
Retrieves the user data for who has the top score so far.

_GET Request:_

- http://localhost:3000/topScore
- API URL/topScore

_Response:_

```
json
{
    "score": "1",
    "user_id": "ab123",
    "url": "https://storage.googleapis.com/venushacks2024-777a4.appspot.com/baldgate.png"
}
```

_Error Response:_

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

_GET Request:_

- http://localhost:3000/getAllData
- API URL/getAllData

_Response:_

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

_Error Response:_

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

pip install pyaudio - if missing dependencies do "brew install portaudio" and try command again

pip install pyttsx3
