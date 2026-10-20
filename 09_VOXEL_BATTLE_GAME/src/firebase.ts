import { initializeApp, type FirebaseApp } from "firebase/app";
import { getDatabase, type Database } from "firebase/database";

// ────────────────────────────────────────────────────────────────────────────
// Firebase の設定をここに貼り付けてください（手順は README.md の「オンライン対戦の
// セットアップ」を参照）。
//
// ⚠️ ここに入る apiKey / appId などは Firebase Web では「公開前提の識別子」であり、
//    Firebase用APIへの利用制限を設定したうえで公開できます。
//    実際のアクセス制御は Realtime Database の「セキュリティルール」で行います
//    （README.md にルール例を記載）。
//
// 未設定のままでも「ローカル対戦（同じPCの2タブ）」は動作します。
// ────────────────────────────────────────────────────────────────────────────
const firebaseConfig = {
  apiKey: "PASTE_API_KEY",
  authDomain: "PASTE_AUTH_DOMAIN",
  databaseURL: "PASTE_DATABASE_URL",
  projectId: "PASTE_PROJECT_ID",
  storageBucket: "PASTE_STORAGE_BUCKET",
  messagingSenderId: "PASTE_MESSAGING_SENDER_ID",
  appId: "PASTE_APP_ID",
};

/** 設定がプレースホルダのままかどうかを判定する。 */
export function isFirebaseConfigured(): boolean {
  return (
    !firebaseConfig.apiKey.startsWith("PASTE") &&
    !firebaseConfig.databaseURL.includes("PASTE")
  );
}

let app: FirebaseApp | undefined;
let db: Database | undefined;

export function getDb(): Database {
  if (!isFirebaseConfigured()) {
    throw new Error(
      "Firebaseが未設定です。src/firebase.ts に firebaseConfig を貼り付けてください。",
    );
  }
  if (!db) {
    app = initializeApp(firebaseConfig);
    db = getDatabase(app);
  }
  return db;
}
