import firebase_admin
from firebase_admin import credentials,firestore,db
import json,os
from dotenv import load_dotenv

load_dotenv()

def load_config():
    cred = credentials.Certificate("creditentials.json")
    firebase_admin.initialize_app(cred,{'databaseURL': os.getenv("DATABASE_URL")})
    db = firestore.client()
    return db

def get_data(db,collection,document):
    doc_ref = db.collection(collection).document(document)
    thedocDict = doc_ref.get().to_dict()
    return thedocDict
