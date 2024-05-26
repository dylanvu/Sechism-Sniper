import express, { Express, Request, Response } from "express";
import dotenv from "dotenv";
import multer from 'multer';

import { initializeApp, cert } from "firebase-admin/app";
import { getFirestore } from "firebase-admin/firestore";
import { getStorage } from 'firebase-admin/storage';

import serviceAccount from "../service_account.json";
import { error } from "console";

dotenv.config();

// setting up express backend appd and port
const app: Express = express();
const port = process.env.PORT || 3000;

// setting up firebase app
const firebaseConfig = {
  credential: cert(serviceAccount as any), // Use `as any` to fix type issues with the service account object
  storageBucket: process.env.FIREBASE_STORAGE_BUCKET
};
const fireBaseApp = initializeApp(firebaseConfig);
const db = getFirestore(fireBaseApp);
const bucket = getStorage().bucket();

// get form-data file
const upload = multer({ storage: multer.memoryStorage() });

// configure some middleware to parse JSON and URL-encoded bodies
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.get("/", (req: Request, res: Response) => {
  res.send("Express + TypeScript Server");
});

app.listen(port, () => {
  console.log(`[server]: Server is running at http://localhost:${port}`);
});

// route to get top score
// Request format:
// http://localhost:3000/topScore
app.get("/topScore", async (req: Request, res: Response) => {

  const retrievedData = await getTopScore()

  if (retrievedData == -1) {
    res.send({error: -1, note:"no users found"})
  }
  else {
    res.send(retrievedData)
  }

})


// route to get data from the database
// Request format:
// http://localhost:3000/getData?user_id={unique id insert here}
app.get("/getData", async (req: Request, res: Response) => {
  // Access the user_id from the query parameters
  const userID = req.query.user_id as string;

  // Check if user_id is provided
  if (!userID) {
    return res.status(400).send('No user_id provided.');
  }

  const retrievedData = await getDataFromFireStore(userID)

  // if the object is empty then send a response that there is no document with that user_id
  if (!retrievedData) {
    res.send({error: '-1', note: "there is no document with this user_id"})
  }
  else {
    console.log("Retrieved Data: ", retrievedData)
    res.send(retrievedData)
  }
})

// route to send data from jaysons ai thing to the database
// Request format:
// data {
//     user_id: ab123
//     image_file: <image_file>, // base64 encoded image as string 
//     score: 1,
// }
app.post("/sendData", upload.single('image_file'), async (req: Request, res:Response) => {
  if (!req.file) {
    return res.status(400).send('No file uploaded.');
  }

  // getting data from body
  const user_id = req.body.user_id
  const score = req.body.score
  const imageFile = req.file
  const blob = bucket.file(imageFile.originalname)
  const blobStream = blob.createWriteStream({
    metadata: {
      contentType: imageFile.mimetype,
    },
  });

  blobStream.on('error', (err) => {
    res.status(500).send(err.message);
  });

  // adding image to fire store
  blobStream.on('finish', async () => {
    const publicUrl = `https://storage.googleapis.com/${bucket.name}/${blob.name}`;
    
    // Save file metadata to Firestore
    await db.collection('image_files').add({
      unique_id: user_id,
      name: imageFile.originalname,
      url: publicUrl,
      size: imageFile.size,
      contentType: imageFile.mimetype,
      createdAt: new Date(),
    });

    try {
      await addtoFirestore(user_id, score, publicUrl)
    }
    catch(error) {
      console.log(error)
      res.send("Unable to add user_id and score to database")
    }
    
    res.status(200).send({user_id, score, fileName: imageFile.originalname, fileUrl: publicUrl });
  });

  blobStream.end(imageFile.buffer);
})

// route to update database
// Request format:
// data {
//     user_id: ab123
//     score_to_add: 1,
// }
app.put("/updateData",  async (req: Request, res: Response) => {
  console.log(req.body)
  // adding user_id and score to firestore
  const user_id = req.body.user_id
  const score = req.body.score_to_add

  // res.send("updating data")
  try {
    await updateScoreInFireStore(user_id, score)
    res.send("Score Updated")
  }
  catch (error) {
    res.send({error: -1, note: "add user to data base first, then call this route again"})
  }

})


// function to add text data to database
async function addtoFirestore(user_id: string,  score: number, public_url: string) {
  const docRef = db.collection('users').doc(user_id);

  await docRef.set({
    user_id: user_id,
    score: score,
    url: public_url
  });

  console.log('Document successfully written!');
}

// function to retrieve data from the database
async function getDataFromFireStore(user_id: string) {
  const list: {}[] = []
  // get collection of users
  try {
    const usersRef = db.collection('users')
    const snapshot = await usersRef.where('user_id', '==', user_id).get()
    if (snapshot.empty) {
      console.log("No matching documents")
      return null
    }
    else {
      snapshot.forEach(doc => {
        list.push({[doc.id] : doc.data()})
      })
      return list
    }

  }
  catch(error) {
    console.log(error)
    return -1
  }
}


async function getTopScore() {
  try {
    const usersRef = db.collection('users');
    const topUserQuery = await usersRef.orderBy('score', 'desc').limit(1).get();

    if (topUserQuery.empty) {
      return -1
    }

    let topUser = {};
    topUserQuery.forEach(doc => {
      topUser = doc.data();
    });

    return topUser
  } catch (error) {
    console.error('Error fetching top user: ', error);
    return -1
  }
}

const updateScoreInFireStore = async (userID: string, scoreToAdd: number) => {
  const userRef = db.collection('users').doc(userID);
  const doc = await userRef.get();
  
  // if the doc does not exist then add the user into the database
  if (!doc.exists) {
    throw error
  }
  else {
    if (doc.data()) {
      const currentScore = doc.data()?.score 
      const newScore = Number(currentScore) + scoreToAdd;
      await userRef.update({ score: newScore });
    }
  }
};

