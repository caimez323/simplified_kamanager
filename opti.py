import json

replaced_data = []
count = 0
with open("resources.gears.json",encoding="utf-8") as gearsFile:
    gearsData = json.load(gearsFile)
    for gear in gearsData:
        newGear = gear
        newGear["id"] = count+1
        replaced_data.append(newGear)
        count+=1

with open("datatest.json","w",encoding="utf-8") as file:
    json.dump(replaced_data, file, ensure_ascii=False, indent=4)
