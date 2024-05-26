import express, { Express, Request, Response } from "express";
import dotenv from "dotenv";
import multer from 'multer';

import { initializeApp, cert } from "firebase-admin/app";
import { getFirestore } from "firebase-admin/firestore";
import { getStorage } from 'firebase-admin/storage';

import serviceAccount from "../service_account.json";

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

app.get("/", (req: Request, res: Response) => {
  res.send("Express + TypeScript Server");
});

app.listen(port, () => {
  console.log(`[server]: Server is running at http://localhost:${port}`);
});


// route to get data from the database
// Request format:
// data {
//     "user_id": 12345
// }
app.get("/getData", (req: Request, res: Response) => {

})


// route to send data from jaysons ai thing to the database
// Request format:
// data {
//     user_id: ab123
//     image_file: <image_file>, // base64 encoded image as string 
//     score: 1,
// }
app.post("/sendData", upload.single('image_file'), (req: Request, res:Response) => {
  if (!req.file) {
    return res.status(400).send('No file uploaded.');
  }

  // getting data from body
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

  
  // adding user_id and score to firestore
  const user_id = req.body.user_id
  const score = req.body.score

  try {
    addtoFirestore(user_id, score)
  }
  catch(error) {
    console.log(error)
    res.send("Unable to add user_id and score to database")
  }

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

    res.status(200).send({user_id, score, fileName: imageFile.originalname, fileUrl: publicUrl });
  });

  blobStream.end(imageFile.buffer);
})


// function to add text data to database
async function addtoFirestore(user_id: string,  score: number) {
  const docRef = db.collection('users').doc(user_id);

  await docRef.set({
    user_id: user_id,
    score: score,
  });

  console.log('Document successfully written!');
}

