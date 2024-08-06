from flask import Flask, render_template, request,redirect,session, jsonify
import sqlite3
from bcrypt import gensalt,hashpw,checkpw
from cas import CASClient
from urllib.parse import quote_plus
from cryptography.fernet import Fernet
import os
from functools import cmp_to_key
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)

CAS_SERVER_URL="https://login.iiit.ac.in/cas/"
SERVICE_URL="http://10.2.135.148:5000/Get_Auth"
REDIRECT_URL="http://10.2.135.148:5000/Get_Auth"

UPLOAD_FOLDER_1 = './static/round1/'
UPLOAD_FOLDER_2 = './static/round2/'
UPLOAD_FOLDER_3 = './static/round3/'
UPLOAD_FOLDER_4 = './static/round4/'

app.config['UPLOAD_FOLDER_1'] = UPLOAD_FOLDER_1
app.config['UPLOAD_FOLDER_2'] = UPLOAD_FOLDER_2
app.config['UPLOAD_FOLDER_3'] = UPLOAD_FOLDER_3
app.config['UPLOAD_FOLDER_4'] = UPLOAD_FOLDER_4


if os.path.exists('r1.json'):
    with open('r1.json', 'r') as file:
        r1 = json.load(file)
else:
    r1 = []

if os.path.exists('r2.json'):
    with open('r2.json', 'r') as file:
        r2 = json.load(file)
else:
    r2 = []

if os.path.exists('r3.json'):
    with open('r3.json', 'r') as file:
        r3 = json.load(file)
else:
    r3 = []

if os.path.exists('r4.json'):
    with open('r4.json', 'r') as file:
        r4 = json.load(file)
else:
    r4 = []

if os.path.exists('selected_r1.json'):
    with open('selected_r1.json', 'r') as file:
        selected_r1 = json.load(file)
else:
    selected_r1 = []

if os.path.exists('selected_r2.json'):
    with open('selected_r2.json', 'r') as file:
        selected_r2 = json.load(file)
else:
    selected_r2 = []

if os.path.exists('selected_r3.json'):
    with open('selected_r3.json', 'r') as file:
        selected_r3 = json.load(file)
else:
    selected_r3 = []

if os.path.exists('selected_r4.json'):
    with open('selected_r4.json', 'r') as file:
        selected_r4 = json.load(file)
else:
    selected_r4 = []


cas_client = CASClient(
    version=3,
    service_url=f"{SERVICE_URL}?next={quote_plus(REDIRECT_URL)}",
    server_url=CAS_SERVER_URL,
)

#read rounds from file
if os.path.exists('rounds.json'):
    with open('rounds.json', 'r') as file:
        rounds = json.load(file)
else:
    rounds = [0,0,0,0]

#read voting from file
if os.path.exists('voting.json'):
    with open('voting.json', 'r') as file:
        voting = json.load(file)
else:
    voting = [0,0,0,0]

admins = ['adithya.kishor', 'krish.pandya', 'gautam.bhetanabhotla', 'vigneshvembar.m', 'saloni.goyal', 'virat.garg', 'manas.agrawal']

@app.route('/login')
def LogIn():
    return render_template('LogIn.html')


@app.route('/Get_Auth', methods=['POST', 'GET'])
def Get_Auth():
    if request.method == 'POST':
        cas_login_url = cas_client.get_login_url()
        return redirect(cas_login_url)
    else:
        ticket = request.args.get('ticket')
        if ticket:
            user, attributes, pgtiou = cas_client.verify_ticket(ticket)
            if user:
                roll = attributes['RollNo']
                email = attributes['E-Mail']
                first_name = attributes['FirstName']
                last_name = attributes['LastName']
                uid = attributes['uid']
                batch = ''
                gender = ''
                with open('key.key', 'rb') as file:
                    key = file.read()
                fernet = Fernet(key)
                attributes_json = json.dumps(attributes)
                token = fernet.encrypt(attributes_json.encode())
                session['token'] = token
    return redirect('/')

@app.route('/', methods=['GET'])
def index():
    if 'token' in session:
        token = session['token']
        with open('key.key', 'rb') as file:
            key = file.read()
        fernet = Fernet(key)
        attributes_json = fernet.decrypt(token).decode()
        attributes = json.loads(attributes_json)
        print(rounds)
        print(voting)
        return render_template('index.html', user=attributes['FirstName'], rounds=rounds, voting=voting)
    else:
        return redirect('/login')

@app.route('/round1', methods=['POST', 'GET'])
def round1():
    if rounds[0] == 0:
        return redirect('/')
    if request.method == 'POST':
        if 'file1' not in request.files:
            return 'there is no file1 in form!'
        file1 = request.files['file1']
        token = session['token']
        with open('key.key', 'rb') as file:
            key = file.read()
        fernet = Fernet(key)
        attribute_json = fernet.decrypt(token).decode()
        attributes = json.loads(attribute_json)
        uid = attributes['uid']+'.' + file1.filename.split('.')[-1]
        path = os.path.join(app.config['UPLOAD_FOLDER_1'], uid)
        file1.save(path)
        if path not in r1:
            r1.append(path)
        #save r1 in file
        with open('r1.json', 'w') as file:
            json.dump(r1, file)
        return render_template('round1.html')
    return render_template('round1.html')

@app.route('/round2', methods=['POST', 'GET'])
def round2():
    if rounds[1] == 0:
        return redirect('/')
    if request.method == 'POST':
        if 'file1' not in request.files:
            return 'there is no file1 in form!'
        file1 = request.files['file1']
        token = session['token']
        with open('key.key', 'rb') as file:
            key = file.read()
        fernet = Fernet(key)
        attribute_json = fernet.decrypt(token).decode()
        attributes = json.loads(attribute_json)
        uid = attributes['uid']+'.' + file1.filename.split('.')[-1]
        path = os.path.join(app.config['UPLOAD_FOLDER_2'], uid)
        file1.save(path)
        if path not in r2:
            r2.append(path)
        with open('r2.json', 'w') as file:
            json.dump(r2, file)
        return render_template('round2.html')
    return render_template('round2.html')

@app.route('/round3', methods=['POST', 'GET'])
def round3():
    if rounds[2] == 0:
        return redirect('/')
    if request.method == 'POST':
        if 'file1' not in request.files:
            return 'there is no file1 in form!'
        file1 = request.files['file1']
        token = session['token']
        with open('key.key', 'rb') as file:
            key = file.read()
        fernet = Fernet(key)
        attribute_json = fernet.decrypt(token).decode()
        attributes = json.loads(attribute_json)
        uid = attributes['uid']+'.' + file1.filename.split('.')[-1]
        path = os.path.join(app.config['UPLOAD_FOLDER_3'], uid)
        file1.save(path)
        if path not in r3:
            r3.append(path)
        with open('r3.json', 'w') as file:
            json.dump(r3, file)
        return render_template('round3.html')
    return render_template('round3.html')

@app.route('/round4', methods=['POST', 'GET'])
def round4():
    if rounds[3] == 0:
        return redirect('/')
    if request.method == 'POST':
        if 'file1' not in request.files:
            return 'there is no file1 in form!'
        file1 = request.files['file1']
        token = session['token']
        with open('key.key', 'rb') as file:
            key = file.read()
        fernet = Fernet(key)
        attribute_json = fernet.decrypt(token).decode()
        attributes = json.loads(attribute_json)
        uid = attributes['uid']+'.' + file1.filename.split('.')[-1]
        path = os.path.join(app.config['UPLOAD_FOLDER_4'], uid)
        file1.save(path)
        if path not in r4:
            r4.append(path)
        with open('r4.json', 'w') as file:
            json.dump(r4, file)
        return render_template('round4.html')
    return render_template('round4.html')

@app.route('/admin')
def admin():
    if 'token' in session:
        token = session['token']
        with open('key.key', 'rb') as file:
            key = file.read()
        fernet = Fernet(key)
        attributes_json = fernet.decrypt(token).decode()
        attributes = json.loads(attributes_json)
        if attributes['uid'] in admins:
            return render_template('admin.html')
        else:
            return redirect('/')
    else:
        return redirect('/login')
    
@app.route('/adm_round1')
def adm_round1():
    if 'token' in session:
        token = session['token']
        with open('key.key', 'rb') as file:
            key = file.read()
        fernet = Fernet(key)
        attributes_json = fernet.decrypt(token).decode()
        attributes = json.loads(attributes_json)
        if attributes['uid'] in admins:
            return render_template('adm_round1.html', files=r1, selected_files=selected_r1)
        else:
            return redirect('/')
    else:
        return redirect('/login')
    
@app.route('/adm_round2')
def adm_round2():
    if 'token' in session:
        token = session['token']
        with open('key.key', 'rb') as file:
            key = file.read()
        fernet = Fernet(key)
        attributes_json = fernet.decrypt(token).decode()
        attributes = json.loads(attributes_json)
        if attributes['uid'] in admins:
            return render_template('adm_round2.html', files=r2, selected_files=selected_r2)
        else:
            return redirect('/')
    else:
        return redirect('/login')

@app.route('/adm_round3')
def adm_round3():
    if 'token' in session:
        token = session['token']
        with open('key.key', 'rb') as file:
            key = file.read()
        fernet = Fernet(key)
        attributes_json = fernet.decrypt(token).decode()
        attributes = json.loads(attributes_json)
        if attributes['uid'] in admins:
            return render_template('adm_round3.html', files=r3, selected_files=selected_r3)
        else:
            return redirect('/')
    else:
        return redirect('/login')

@app.route('/adm_round4')
def adm_round4():
    if 'token' in session:
        token = session['token']
        with open('key.key', 'rb') as file:
            key = file.read()
        fernet = Fernet(key)
        attributes_json = fernet.decrypt(token).decode()
        attributes = json.loads(attributes_json)
        if attributes['uid'] in admins:
            return render_template('adm_round4.html', files=r4, selected_files=selected_r4)
        else:
            return redirect('/')
    else:
        return redirect('/login')
    
@app.route('/select_r1/static/round1/<value>')
def select_r1(value):
    print(value)
    path = './static/round1/' + value
    if path in r1:
        r1.remove(path)
        selected_r1.append(path)
    with open('r1.json', 'w') as file:
        json.dump(r1, file)
    with open('selected_r1.json', 'w') as file:
        json.dump(selected_r1, file)
    return redirect('/adm_round1')

@app.route('/unselect_r1/static/round1/<value>')
def unselect_r1(value):
    print(value)
    path = './static/round1/' + value
    if path in selected_r1:
        selected_r1.remove(path)
        r1.append(path)
    print(selected_r1)
    with open('r1.json', 'w') as file:
        json.dump(r1, file)
    with open('selected_r1.json', 'w') as file:
        json.dump(selected_r1, file)
    return redirect('/adm_round1')

@app.route('/select_r2/static/round2/<value>')
def select_r2(value):
    print(value)
    path = './static/round2/' + value
    if path in r2:
        r2.remove(path)
        selected_r2.append(path)
    with open('r2.json', 'w') as file:
        json.dump(r2, file)
    with open('selected_r2.json', 'w') as file:
        json.dump(selected_r2, file)
    return redirect('/adm_round2')

@app.route('/unselect_r2/static/round2/<value>')
def unselect_r2(value):
    print(value)
    path = './static/round2/' + value
    if path in selected_r2:
        selected_r2.remove(path)
        r2.append(path)
    with open('r2.json', 'w') as file:
        json.dump(r2, file)
    with open('selected_r2.json', 'w') as file:
        json.dump(selected_r2, file)
    return redirect('/adm_round2')

@app.route('/select_r3/static/round3/<value>')
def select_r3(value):
    print(value)
    path = './static/round3/' + value
    if path in r3:
        r3.remove(path)
        selected_r3.append(path)
    with open('r3.json', 'w') as file:
        json.dump(r3, file)
    with open('selected_r3.json', 'w') as file:
        json.dump(selected_r3, file)
    return redirect('/adm_round3')

@app.route('/unselect_r3/static/round3/<value>')
def unselect_r3(value):
    print(value)
    path = './static/round3/' + value
    if path in selected_r3:
        selected_r3.remove(path)
        r3.append(path)
    with open('r3.json', 'w') as file:
        json.dump(r3, file)
    with open('selected_r3.json', 'w') as file:
        json.dump(selected_r3, file)
    return redirect('/adm_round3')

@app.route('/select_r4/static/round4/<value>')
def select_r4(value):
    print(value)
    path = './static/round4/' + value
    if path in r4:
        r4.remove(path)
        selected_r4.append(path)
    with open('r4.json', 'w') as file:
        json.dump(r4, file)
    with open('selected_r4.json', 'w') as file:
        json.dump(selected_r4, file)
    return redirect('/adm_round4')

@app.route('/unselect_r4/static/round4/<value>')
def unselect_r4(value):
    print(value)
    path = './static/round4/' + value
    if path in selected_r4:
        selected_r4.remove(path)
        r4.append(path)
    with open('r4.json', 'w') as file:
        json.dump(r4, file)
    with open('selected_r4.json', 'w') as file:
        json.dump(selected_r4, file)
    return redirect('/adm_round4')

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'token' in session:
        token = session['token']
        with open('key.key', 'rb') as file:
            key = file.read()
        fernet = Fernet(key)
        attributes_json = fernet.decrypt(token).decode()
        attributes = json.loads(attributes_json)
        if attributes['uid'] in admins:
            return render_template('admin_dashboard.html', rounds=rounds, voting=voting)
        else:
            return redirect('/')
    else:
        return redirect('/login')

@app.route('/toggle_state/<string:type>/<int:index>', methods=['POST'])
def toggle_state(type, index):
    if type == 'round' and 0 <= index < len(rounds):
        rounds[index] = 1 - rounds[index]
        with open('rounds.json', 'w') as file:
            json.dump(rounds, file)
        return jsonify({'success': True})
    elif type == 'vote' and 0 <= index < len(voting):
        voting[index] = 1 - voting[index]
        with open('voting.json', 'w') as file:
            json.dump(voting, file)
        return jsonify({'success': True})
    return jsonify({'success': False}), 400

@app.route('/vote1', methods=['POST', 'GET'])    
def vote1():
    if request.method == 'POST':
        path = request.form['selectedImage']
        if 'token' not in session:
            return redirect('/login')
        token = session['token']
        with open('key.key', 'rb') as file:
            key = file.read()
        fernet = Fernet(key)
        attributes_json = fernet.decrypt(token).decode()
        attributes = json.loads(attributes_json)
        uid = attributes['uid']
        if os.path.exists('voter1.json'):
            with open('voter1.json', 'r') as file:
                voters1 = json.load(file)
        else:
            voters1 = []
        if uid not in voters1 and voting[0] == 1:
            if os.path.exists('round1.json'):
                with open('round1.json', 'r') as file:
                    votes_r1 = json.load(file)
            else:
                votes_r1 = {}
            if path not in votes_r1:
                votes_r1[path] = 1
            else:
                votes_r1[path] += 1
            with open('round1.json', 'w') as file:
                json.dump(votes_r1, file)
            voters1.append(uid)
            with open('voter1.json', 'w') as file:
                json.dump(voters1, file)
        return redirect('/')
    else:
        if 'token' not in session:
            return redirect('/login')
        token = session['token']
        with open('key.key', 'rb') as file:
            key = file.read()
        fernet = Fernet(key)
        attributes_json = fernet.decrypt(token).decode()
        attributes = json.loads(attributes_json)
        uid = attributes['uid']
        if os.path.exists('voter1.json'):
            with open('voter1.json', 'r') as file:
                voters1 = json.load(file)
        else:
            voters1 = []
        if uid in voters1 or voting[0] == 0:
            return redirect('/')
        return render_template('vote_round1.html', selected_files=selected_r1)  

@app.route('/vote2', methods=['POST', 'GET'])    
def vote2():
    if request.method == 'POST':
        path = request.form['selectedImage']
        if 'token' not in session:
            return redirect('/login')
        token = session['token']
        with open('key.key', 'rb') as file:
            key = file.read()
        fernet = Fernet(key)
        attributes_json = fernet.decrypt(token).decode()
        attributes = json.loads(attributes_json)
        uid = attributes['uid']
        if os.path.exists('voter2.json'):
            with open('voter2.json', 'r') as file:
                voters2 = json.load(file)
        else:
            voters2 = []
        if uid not in voters2 and voting[1] == 1:
            if os.path.exists('round2.json'):
                with open('round2.json', 'r') as file:
                    votes_r2 = json.load(file)
            else:
                votes_r2 = {}
            if path not in votes_r2:
                votes_r2[path] = 1
            else:
                votes_r2[path] += 1
            with open('round2.json', 'w') as file:
                json.dump(votes_r2, file)
            voters2.append(uid)
            with open('voter2.json', 'w') as file:
                json.dump(voters2, file)
        return redirect('/')
    else:
        if 'token' not in session:
            return redirect('/login')
        token = session['token']
        with open('key.key', 'rb') as file:
            key = file.read()
        fernet = Fernet(key)
        attributes_json = fernet.decrypt(token).decode()
        attributes = json.loads(attributes_json)
        uid = attributes['uid']
        if os.path.exists('voter2.json'):
            with open('voter2.json', 'r') as file:
                voters2 = json.load(file)
        else:
            voters2 = []
        if uid in voters2 or voting[1] == 0:
            return redirect('/')
        return render_template('vote_round2.html', selected_files=selected_r2)  

@app.route('/vote3', methods=['POST', 'GET'])    
def vote3():
    if request.method == 'POST':
        path = request.form['selectedImage']
        if 'token' not in session:
            return redirect('/login')
        token = session['token']
        with open('key.key', 'rb') as file:
            key = file.read()
        fernet = Fernet(key)
        attributes_json = fernet.decrypt(token).decode()
        attributes = json.loads(attributes_json)
        uid = attributes['uid']
        if os.path.exists('voter3.json'):
            with open('voter3.json', 'r') as file:
                voters3 = json.load(file)
        else:
            voters3 = []
        if uid not in voters3 and voting[2] == 1:
            if os.path.exists('round3.json'):
                with open('round3.json', 'r') as file:
                    votes_r3 = json.load(file)
            else:
                votes_r3 = {}
            if path not in votes_r3:
                votes_r3[path] = 1
            else:
                votes_r3[path] += 1
            with open('round3.json', 'w') as file:
                json.dump(votes_r3, file)
            voters3.append(uid)
            with open('voter3.json', 'w') as file:
                json.dump(voters3, file)
        return redirect('/')
    else:
        if 'token' not in session:
            return redirect('/login')
        token = session['token']
        with open('key.key', 'rb') as file:
            key = file.read()
        fernet = Fernet(key)
        attributes_json = fernet.decrypt(token).decode()
        attributes = json.loads(attributes_json)
        uid = attributes['uid']
        if os.path.exists('voter3.json'):
            with open('voter3.json', 'r') as file:
                voters3 = json.load(file)
        else:
            voters3 = []
        if uid in voters3 and voting[2] == 0:
            return redirect('/')
        return render_template('vote_round3.html', selected_files=selected_r3)  

@app.route('/vote4', methods=['POST', 'GET'])    
def vote4():
    if request.method == 'POST':
        path = request.form['selectedImage']
        if 'token' not in session:
            return redirect('/login')
        token = session['token']
        with open('key.key', 'rb') as file:
            key = file.read()
        fernet = Fernet(key)
        attributes_json = fernet.decrypt(token).decode()
        attributes = json.loads(attributes_json)
        uid = attributes['uid']
        if os.path.exists('voter4.json'):
            with open('voter4.json', 'r') as file:
                voters4 = json.load(file)
        else:
            voters4 = []
        if uid not in voters4 and voting[3] == 1:
            if os.path.exists('round4.json'):
                with open('round4.json', 'r') as file:
                    votes_r4 = json.load(file)
            else:
                votes_r4 = {}
            if path not in votes_r4:
                votes_r4[path] = 1
            else:
                votes_r4[path] += 1
            with open('round4.json', 'w') as file:
                json.dump(votes_r4, file)
            voters4.append(uid)
            with open('voter4.json', 'w') as file:
                json.dump(voters4, file)
        return redirect('/')
    else:
        if 'token' not in session:
            return redirect('/login')
        token = session['token']
        with open('key.key', 'rb') as file:
            key = file.read()
        fernet = Fernet(key)
        attributes_json = fernet.decrypt(token).decode()
        attributes = json.loads(attributes_json)
        uid = attributes['uid']
        if os.path.exists('voter4.json'):
            with open('voter4.json', 'r') as file:
                voters4 = json.load(file)
        else:
            voters4 = []
        if uid in voters4 and voting[3] == 0:
            return redirect('/')
        return render_template('vote_round4.html', selected_files=selected_r4)  
          
@app.route('/result1')
def result1():
    if 'token' not in session:
        return redirect('/login')
    if os.path.exists('round1.json'):
        with open('round1.json', 'r') as file:
            votes_r1 = json.load(file)
    else:
        votes_r1 = {}

    token = session['token']
    with open('key.key', 'rb') as file:
        key = file.read()
    fernet = Fernet(key)
    attributes_json = fernet.decrypt(token).decode()
    attributes = json.loads(attributes_json)
    uid = attributes['uid']

    if uid in admins:
        max_votes = max(votes_r1.values(), default=1) 
        return render_template('result_round1.html', votes=votes_r1, max_votes=max_votes)
    
    return redirect('/')

@app.route('/result2')
def result2():
    if 'token' not in session:
        return redirect('/login')
    if os.path.exists('round2.json'):
        with open('round2.json', 'r') as file:
            votes_r2 = json.load(file)
    else:
        votes_r2 = {}

    token = session['token']
    with open('key.key', 'rb') as file:
        key = file.read()
    fernet = Fernet(key)
    attributes_json = fernet.decrypt(token).decode()
    attributes = json.loads(attributes_json)
    uid = attributes['uid']

    if uid in admins:
        max_votes = max(votes_r2.values(), default=1) 
        return render_template('result_round2.html', votes=votes_r2, max_votes=max_votes)
    
    return redirect('/')

@app.route('/result3')
def result3():
    if 'token' not in session:
        return redirect('/login')
    if os.path.exists('round3.json'):
        with open('round3.json', 'r') as file:
            votes_r3 = json.load(file)
    else:
        votes_r3 = {}

    token = session['token']
    with open('key.key', 'rb') as file:
        key = file.read()
    fernet = Fernet(key)
    attributes_json = fernet.decrypt(token).decode()
    attributes = json.loads(attributes_json)
    uid = attributes['uid']

    if uid in admins:
        max_votes = max(votes_r3.values(), default=1) 
        return render_template('result_round3.html', votes=votes_r3, max_votes=max_votes)
    
    return redirect('/')

@app.route('/result4')
def result4():
    if 'token' not in session:
        return redirect('/login')
    if os.path.exists('round4.json'):
        with open('round4.json', 'r') as file:
            votes_r4 = json.load(file)
    else:
        votes_r4 = {}

    token = session['token']
    with open('key.key', 'rb') as file:
        key = file.read()
    fernet = Fernet(key)
    attributes_json = fernet.decrypt(token).decode()
    attributes = json.loads(attributes_json)
    uid = attributes['uid']

    if uid in admins:
        max_votes = max(votes_r4.values(), default=1) 
        return render_template('result_round4.html', votes=votes_r4, max_votes=max_votes)
    
    return redirect('/')

if __name__ == '__main__':
    key = Fernet.generate_key()
    with open('key.key', 'wb') as file:
        file.write(key)
    app.run(debug=True, host='0.0.0.0')
