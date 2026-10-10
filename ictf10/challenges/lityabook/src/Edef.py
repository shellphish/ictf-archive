from mechanize import Browser
import time

def login(b,username,password):
  #try:
    b.form = list(b.forms())[0]
    b.form["username"] = username
    b.form["password"] = password
    b.submit()
  #except:
  #  return

if __name__ == "__main__":
  b = Browser()
  b.open("http://10.14.0.3")
  for link in b.links():
    b.open(link.url.replace("?","/?"))
    print b.title()
    if b.title() == "lityabook":
      login(b,"edeo","iworkforpapi")
      print b.title()
