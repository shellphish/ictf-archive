import os,time

f = open("secbook_accounts","r")

for line in f.readlines():
  os.system("java RequestChecker %s %s "%(line.split("|")[0],line.split("|")[1].rstrip("\n")))
  time.sleep(67)
f.close()
