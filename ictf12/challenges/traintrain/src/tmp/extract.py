import sys

count = 0   
print "[",

while True:
    line = sys.stdin.readline()
    if line == "":
        break
    #print line
    parts = line.split()
    city = parts[0][9:]
    if city == "Y-O":
        break
    index = 1
    while True:
        if parts[index].isdigit():
            break
        if parts[index] == "CDP":
            break
        if parts[index] == "town":
            break
        if parts[index] == "city":
            break
        if parts[index] == "village":
            break
        if parts[index] == "borough":
            break
        
        city = city + " " + parts[index]
        index = index + 1
    count = count + 1
    if count % 100 == 0:
        print """ "%s",""" % city,
print "]"    