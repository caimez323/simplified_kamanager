import firebase_admin
from firebase_admin import credentials,firestore,db
import json,os
from dotenv import load_dotenv
import math


def upload_data(DB,collection,document,buffer):
    #buffer = {id : {1 : data1, 2: data2}}
    doc_ref = DB.collection(collection).document(document)
    doc_ref.update(buffer)
    



if __name__ == "__main__":
    load_dotenv()

    cred = credentials.Certificate("creditentials.json")
    firebase_admin.initialize_app(cred,{'databaseURL': os.getenv("DATABASE_URL")})
    db = firestore.client()
    """  
    doc_ref = db.collection("resources").document("common")
    
    with open("resources_format.json",'r',encoding="utf-8") as file:
        data = json.load(file)

    doc_ref = db.collection("resources").document("common")
    for id,elem in data.items():
        to_add  = {id:elem}
        print(to_add)
        doc_ref.update(to_add)
        
  
    with open("gears_format.json",'r',encoding="utf-8") as file:
        data = json.load(file)

    for id,elem in data.items():
        docID = math.floor(int(id)/1000)
        doc_ref = db.collection("gears").document("common{}".format(docID))
        to_add = {id:elem}
        print(to_add)
        doc_ref.update(to_add)
    """
        
        
        
        
    """
    with open("resources.resources.json",'r',encoding="utf-8") as file:
        data = json.load(file)
    for elem in data:
        id = str(elem["id"])
        docID = math.floor(int(id)/1000)
        doc_ref = db.collection("gears").document("common{}".format(docID))
        to_add = {id : elem}
        doc_ref.update(to_add)
        print(to_add)
    """

    # == doc_ref.update(to_add)