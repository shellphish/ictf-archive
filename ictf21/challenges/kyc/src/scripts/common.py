import io
import pytesseract
import random
import string

from fpdf import FPDF
import PyPDF2
import pdf2image

WORDS = ['banner', 'deposit', 'term', 'stone', 'advice', 'usual', 'dynamic', 'attitude', 'route', 'basic', 'kind', 'peace', 'shrug', 'day', 'excess', 'aisle', 'glue', 'reject', 'viable', 'wash', 'image', 'lizard', 'topic', 'height', 'agent', 'frog', 'tree', 'near', 'author', 'noble', 'certain', 'two', 'milk', 'offer', 'immune', 'cave', 'scan', 'scheme', 'initial', 'treat', 'twenty', 'smooth', 'vocal', 'ancient', 'song', 'ask', 'lesson', 'potato', 'theory', 'muscle', 'orphan', 'nominee', 'access', 'dose', 'nut', 'until', 'text', 'mango', 'liar', 'soft', 'smoke', 'bottom', 'daughter', 'found', 'erode', 'unique', 'useful', 'pyramid', 'cancel', 'stay', 'sing', 'drum', 'gossip', 'cube', 'strike', 'taste', 'mind', 'trade', 'rice', 'sail', 'nurse', 'whisper', 'shrimp', 'balcony', 'object', 'junk', 'series', 'sniff', 'attract', 'welcome', 'roof', 'around', 'already', 'another', 'idle', 'craft']


def gen_username():
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(32))

def gen_password():
    return ' '.join(random.choice(WORDS) for _ in range(5))

def register(session, ip, port, username, password):    
    r = session.post('http://%s:%s/register' % (ip, port), data={'username': username, 'password': password})
    assert(r.status_code == 200)
    
def login(session, ip, port, username, password):    
    r = session.post('http://%s:%s/login' % (ip, port), data={'username': username, 'password': password})
    assert(r.status_code == 200)
    
def kyc(session, ip, port, filename, image):
    r = session.post('http://%s:%s/kyc' % (ip, port), files={'idcard': (filename, image)})
    assert(r.status_code == 200)
        
def idcard(session, ip, port):
    r = session.get('http://%s:%s/idcard' % (ip, port))
    assert(r.status_code == 200)    
    return r.content

# getflag
def pdf_to_string(pdf):
    pdf  = PyPDF2.PdfFileReader(io.BytesIO(pdf))
    page = pdf.getPage(0)
    return page.extractText()


# setflag
def string_to_pdf(string):
    document = FPDF()
    document.add_page()
    document.set_font('helvetica', size=12)
    document.cell(txt=string)
    return document.output()

# exploit
def pdf_to_image(pdf):
    images = pdf2image.convert_from_bytes(pdf)
    return images[0]

def image_to_string(image):
    return pytesseract.image_to_string(image)
