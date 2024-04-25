import json

replaced_data = {}
idUsed = []
idToRemove = []
count = 0

with open("gears_format.json",encoding="utf-8") as gearsFile:
    gearsData = json.load(gearsFile)
    
    for id,res in gearsData.items():
        recipe = res["recipe"]
        for compo in recipe:
            idUsed.append(compo["id"])
        
with open("resources_format.json",encoding="utf-8") as resourcesFile:
    resourcesData = json.load(resourcesFile)
    
    for id,res in resourcesData.items():
        if id not in idUsed:
            print("Will remove {}".format(id))
        else:
            replaced_data[id]=res


with open("resources_format.json","w",encoding="utf-8") as file:
    json.dump(replaced_data, file, ensure_ascii=False, indent=4)

