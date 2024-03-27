import firebase_admin
from firebase_admin import firestore
from dotenv import load_dotenv
import json,os

load_dotenv()

cred = firebase_admin.credentials.Certificate("creditentials.json")
firebase_admin.initialize_app(cred,{'databaseURL': os.getenv("DATABASE_URL")})
database = firebase_admin.firestore.client()




