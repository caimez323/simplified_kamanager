import firebase_admin
from firebase_admin import firestore
from dotenv import load_dotenv
import json,os

load_dotenv()

cred = firebase_admin.credentials.Certificate("creditentials.json")
firebase_admin.initialize_app(cred,{'databaseURL': os.getenv("DATABASE_URL")})
database = firebase_admin.firestore.client()



doc_ref = database.collection("resources").document("common")
with open("resources.resources.json",'r',encoding="utf-8") as file:

    data = json.load(file)
    for elem in data:
        id = str(elem["id"])
        to_add = {id : elem}

        print(to_add)
        #doc_ref.update(to_add)
    

#doc_ref.update(to_add)