import firebase_admin
from firebase_admin import credentials,firestore,db
import json,os
from dotenv import load_dotenv

load_dotenv()

cred = credentials.Certificate("creditentials.json")
firebase_admin.initialize_app(cred,{'databaseURL': os.getenv("DATABASE_URL")})
db = firestore.client()



doc_ref = db.collection("resources").document("common")
with open("resources.resources.json",'r',encoding="utf-8") as file:

    data = json.load(file)
    for elem in data:
        id = str(elem["id"])
        to_add = {id : elem}

        print(to_add)
        #doc_ref.update(to_add)
    

#doc_ref.update(to_add)