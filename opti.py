import json

replaced_data = []
count = 0
with open("resources.gears.json",encoding="utf-8") as gearsFile:
    gearsData = json.load(gearsFile)
    for gear in gearsData:
        if gear["recipe"] == []:
            pass
        else:
            replaced_data.append(gear)


with open("datatest.json","w",encoding="utf-8") as file:
    json.dump(replaced_data, file, ensure_ascii=False, indent=4)
