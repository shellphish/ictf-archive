import os
import sys
import subprocess


from flask import Flask, render_template, redirect, url_for, request, session, send_file
from os.path import join as joinpath
from os.path import normpath

app = Flask(__name__)
app.secret_key = os.environ['SECRET']
app.config['MAX_CONTENT_LENGTH'] = 2**18
DATABASE = '/home/chall/service/rw'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/logout')
def logout():
    session.clear()
    return render_template('index.html')


# We had to tweak some configurations in /etc/ImageMagick-6/policy.xml, because our clients were complaining..
def convert(userroot, filename):
    owd = os.getcwd()
    os.chdir(userroot)

    p = subprocess.call([
        'convert',
        '-density', '300',
        os.path.basename(filename),
        'idcard.pdf'
    ])
    os.chdir(owd)

    return p == 0

# Filesystem DB FTW, no SQLI is possible <3
def init_user(username, password):
    userroot = joinpath(DATABASE, username)
    database = joinpath(userroot, 'database')

    os.mkdir(userroot)
    os.mkdir(database)

    with open(joinpath(database, 'password'), 'w') as f:
        f.write(password)

    os.sync()

def load_password(userroot):
    database = joinpath(userroot, 'database')
    with open(joinpath(database, 'password'), 'r') as f:
        return f.read()


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method != 'POST':
        return redirect(url_for('index'))

    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return render_template('index.html', msg='No username or password!')

    if not username.isalpha():
        return render_template('index.html', msg='Username must contain only letters')

    # Passwords must contain only spaces and lowercase ascii.
    # It is easier to OCR, just in case we decide to print our full
    # database on paper (for backup purposes).
    if not all(c.islower() or c.isspace() for c in password):
        return render_template('index.html', msg='Passwords must contain only lowercase letters or spaces')

    userroot = joinpath(DATABASE, username)

    if os.path.isdir(userroot):
        return render_template('index.html', msg='This user already exists, go away!')

    init_user(username, password)
    return render_template('index.html', msg='Registration succeded!')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('userroot'):
        return redirect(url_for('kyc'))

    if request.method != 'POST':
        return render_template('login.html')

    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password or not username.isalpha():
        return render_template('login.html', msg='Invalid credentials, try again!')

    userroot = joinpath(DATABASE, username)

    if not os.path.isdir(userroot):
        return render_template('login.html', msg='User not registered.')

    if load_password(userroot) == password:
        session['userroot'] = userroot
        session['username'] = username
        session['idcard']   = os.path.isfile(joinpath(userroot, 'idcard.pdf'))
        return redirect(url_for('kyc'))

    return render_template('login.html', msg='Wrong password.')


@app.route('/idcard', methods=['GET'])
def idcard():
    userroot = session.get('userroot')
    if userroot is None:
        return 'You are not authenticated..'

    idcard = joinpath(userroot, 'idcard.pdf')
    if not os.path.isfile(idcard):
        return 'No ID found, please go to /kyc and upload a valid ID'

    return send_file(idcard, as_attachment=False)


@app.route('/kyc', methods=['GET', 'POST'])
def kyc():
    userroot = session.get('userroot')
    if userroot is None:
        return 'You are not authenticated..'

    if request.method == 'GET':
        return render_template('kyc.html')

    idcard = request.files.get('idcard')
    if idcard is None or idcard.filename == '':
        return 'Invalid ID!'

    filename = normpath(joinpath(userroot, idcard.filename))
    if not filename.startswith(DATABASE):
        return 'Hacking attempt detect, you are banned from the blockchain.'

    if filename.endswith('.pdf'):
        idcard.save(joinpath(userroot, 'idcard.pdf'))
    else:
        idcard.save(filename)
        if not convert(userroot, filename):
            session['idcard'] = False
            return render_template('kyc.html', msg='Holy smoke! What can of ID card are you uploading?!')

    session['idcard'] = True

    return render_template('kyc.html')


if __name__ == '__main__':
    app.run()
