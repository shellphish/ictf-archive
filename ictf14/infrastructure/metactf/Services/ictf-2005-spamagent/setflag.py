import sys,random,socket,httplib
from utility import CtfUtil
sys.path.insert(0,'.')

def encode_multipart_formdata(field,value):
    BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = '\r\n'
    L = []
    L.append('--' + BOUNDARY)
    L.append('Content-Disposition: form-data; name="%s"' % field)
    L.append('')
    L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body

def post_multipart(host, selector, content_type, body):
    h = httplib.HTTP(host)
    h.putrequest('POST', selector)
    h.putheader('content-type', content_type)
    h.putheader('content-length', str(len(body)))
    h.endheaders()
    h.send(body)
    errcode, errmsg, headers = h.getreply()
    return h.file.read()

class SetFlag():
  def execute(self,ip,port,flag):
    name=CtfUtil.getRandomString(random.randint(6,8))
    password=CtfUtil.getRandomAlphaNum(8)
    
    query = '<agent><sender><user>'+name+'</user><password>'+password+'</password></sender><code>store set flag "'+flag+'"; results set "Flag was set"</code></agent>'
    
    content_type, body = encode_multipart_formdata('script',query)
    host = ip+":"+str(port)
    selector = '/cgi-bin/spamagent'
    result = post_multipart(host, selector, content_type, body)

    self.flag_id=name
    self.token=password
    self.error=0
    self.error_msg=""
  def result(self):
    return {'FLAG_ID':self.flag_id,'TOKEN':self.token,'ERROR':self.error,'ERROR_MSG':self.error_msg}
