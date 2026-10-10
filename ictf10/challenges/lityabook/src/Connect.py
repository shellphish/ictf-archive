from mechanize import Browser
import os

b = Browser()

res = b.open("http://127.0.0.1/find")

with open("flag2","r") as f:
  for line in f.readlines():
    flag = line.split()[0]

tovisit = []

r = res.read()

for entry in [x.split("</tr>")[0] for x in r.split("<tr>")[2:]]:
  username = entry.split("<a href")[1].split(">")[1].split("<")[0]
  try:
    gender = entry.split("Gender:</b>")[1].lstrip().split("<")[0].rstrip()
  except:
    gender = None
  try:
    year = int(entry.split("Birth Date:</b>")[1].split("</td><td>")[-1].split("<")[0])
  except:
    gender = None
  if gender and year and "snake.cali-art.de" not in r:
	  if gender == "Female" and year >= 1992 and year <= 1994:
	    tovisit.append(username)

if tovisit:
  os.chdir("java")
  for url in ["http://127.0.0.1/profile?username="+x for x in tovisit]:
    os.system("java CheckProfiles %s %s"%(flag,url))
  #os.system("java CheckProfiles %s %s"%(flag," ".join(["http://127.0.0.1/profile?username="+x for x in tovisit])))
