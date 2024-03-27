import firebase_admin
from firebase_admin import firestore
from dotenv import load_dotenv
import json,os

load_dotenv()

cred = firebase_admin.credentials.Certificate("creditentials.json")
firebase_admin.initialize_app(cred,{'databaseURL': os.getenv("DATABASE_URL")})
database = firebase_admin.firestore.client()



to_add = {"1":"111"}
to_add2= {"2":"222"}
doc_ref = 0
#database.collection("test").document("testDoc").set(to_add)
#database.collection("test").document("testDoc").update(to_add2)


theDataRessources = database.collection("resources").document("common")
allDictDatas = theDataRessources.get().to_dict()
print(allDictDatas)
#with open("resources.resources.json",'r',encoding="utf-8") as file:


#for elem in data: doc_ref.set({str(elem["id"]) : elem})

replaced_lines = []
with open("resources.gears.json",'r',encoding="utf-8") as file:
    dataSS = json.load(file)


for element in dataSS: #each element is a dict
    for component in element["recipe"]:
        componentName = component["name"]

        for id, ressourceContent in allDictDatas.items():
            if ressourceContent["name"] == componentName:
                component["id"] = id
            
with open("tempo.json",'w',encoding="utf-8") as resultFile:
    resultFile.write(str (dataSS))


#Lire chaque ligne de gears

#récupérer les objects

#Pour chaque objet, faire en sorte que l'id soit égale à l'id trouvée dans le ressources si le nom est le même



