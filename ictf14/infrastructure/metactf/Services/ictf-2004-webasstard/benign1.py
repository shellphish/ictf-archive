import random,sys
sys.path.insert(0,'.')
from utility import CtfUtil,pybrowse


class Benign():
  def execute(self,ip,port, flag_id='', token=''):
    mainpage=pybrowse.Browser("https://"+ip+":"+str(port))
    mainpage.open()
    mainpage.parse()

    user=CtfUtil.getRandomString(random.randint(16,20))
    password=CtfUtil.getRandomString(random.randint(16,20))
    operation=CtfUtil.getRandomString(random.randint(16,20))
    user=CtfUtil.getRandomString(random.randint(16,20))

    mainpage.forms[0].fields['user']=user
    mainpage.forms[0].fields['password']=password
    mainpage.forms[0].fields['operation']=operation

    repage=mainpage.forms[0].click(None)
    content = repage.page

    error_msg = ""
    error = 0
    if '<a href="index.html">Try again</a>' not in content:
        error_msg += "invalid content"
    if password not in content:
        error_msg += "invalid password"
    if error_msg != "":
        error = 42

    self.flag_id = ''
    self.token = ''
    self.error = error
    self.error_msg = error_msg


  def result(self):
    return {'FLAG_ID':self.flag_id,'TOKEN':self.token,'ERROR':self.error,'ERROR_MSG':self.error_msg}


if __name__ == "__main__":
    b = Benign()
    b.execute("192.168.48.93",4443)
    print repr(b.result())
        