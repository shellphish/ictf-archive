import ftplib
class GetFlag():
  def getflagid(self,line):
    self.flagid=line
  def execute(self,ip,port,flag_id,token):
    ftp=ftplib.FTP()
    ftp.connect(ip,port)
    ftp.login()
    ftp.cwd("/var/ctf/simpleftp/incoming")
    ftp.retrlines("RETR "+token,self.getflagid)
    ftp.close()
    self.error=0;self.error_msg=""
    if self.flagid == flag_id:
        self.flag = token
    else:
        self.flag = ''
        self.error = -1
        self.error_msg = 'Different flag id from file'
  def result(self):
    return {'FLAG':self.flag,'ERROR':self.error,'ERROR_MSG':self.error_msg}
