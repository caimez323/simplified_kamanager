import firebase_admin
from firebase_admin import credentials,firestore,db
import json,os
from dotenv import load_dotenv

load_dotenv()

cred = credentials.Certificate("creditentials.json")
firebase_admin.initialize_app(cred,{'databaseURL': os.getenv("DATABASE_URL")})
db = firestore.client()



doc_ref = db.collection("gears").document("common1")
thedocDict = doc_ref.get().to_dict()

max = 0
for key, val in thedocDict.items():
    if int(key) > int(max):
        max = key
        print(key)


# == doc_ref.update(to_add)