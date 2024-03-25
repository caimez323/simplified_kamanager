import re

count = 0
replaced_lines = []
nextIsId = True
with open("./resources.gears.json","r",encoding="utf-8") as file:
    lines = file.readlines()
    for line in lines:
        if "quantity" in line:
            nextIsId = False
        if "X_X_X" in line:
            count+=1
        replaced_lines.append(line.replace("X_X_X","{},".format(count)))

with open("./resources.gears.json","w",encoding="utf-8") as file:
    [file.write(line) for line in replaced_lines]