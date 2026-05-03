import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.5/firebase-app.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/10.12.5/firebase-auth.js";
import {
  getAnalytics,
  isSupported,
} from "https://www.gstatic.com/firebasejs/10.12.5/firebase-analytics.js";

const firebaseConfig = {
  apiKey: "AIzaSyD2PIxbkHRBpkfWvul3IsQHPj0Suqlsp-0",
  authDomain: "crypto-predict-88c10.firebaseapp.com",
  projectId: "crypto-predict-88c10",
  storageBucket: "crypto-predict-88c10.firebasestorage.app",
  messagingSenderId: "278980815004",
  appId: "1:278980815004:web:bf8ba055c75f51a95b2559",
  measurementId: "G-TRWES3V19Y",
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

let analytics = null;
isSupported()
  .then((supported) => {
    if (supported) analytics = getAnalytics(app);
  })
  .catch(() => {});

export { app, auth, analytics };
