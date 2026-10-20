import sys,ftplib,os
import hmac
sys.path.insert(0,'.')
from utility import CtfUtil
class SetFlag():
        
  def execute(self,ip,port,flag):
    #token is same as flag
    token = flag
    flag_id = CtfUtil.getRandomString(12)
    filename = flag
    
    ftp=ftplib.FTP()
    ftp.connect(ip,port)
    ftp.login()
    ftp.cwd("/var/ctf/simpleftp/incoming")
    file=open(filename,'w')
    file.write(flag_id)
    file.close()
    ftp.storlines("stor "+filename,open(filename,'r'))
    ftp.close()
    os.remove(filename)
    self.token=token    
    self.flag_id=flag_id;
    self.error=0;
    self.error_msg=""
  def result(self):
    return {'FLAG_ID':self.flag_id,'TOKEN':self.token,'ERROR':self.error,'ERROR_MSG':self.error_msg}
