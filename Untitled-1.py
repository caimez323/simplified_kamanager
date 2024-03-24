import re

count = 0
replaced_lines = []
with open("./resources.resources.json","r",encoding="utf-8") as file:
    lines = file.readlines()
    for line in lines:
        if "id" in line:
            count+=1
        replaced_lines.append(line.replace("X_X_X","{},".format(count)))

with open("./resources.resources.json","w",encoding="utf-8") as file:
    [file.write(line) for line in replaced_lines]