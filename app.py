from flask import Flask, render_template, request, redirect, session, jsonify
from flask_socketio import SocketIO, emit
from cas import CASClient
from urllib.parse import quote_plus
from cryptography.fernet import Fernet
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app)
app.secret_key = os.urandom(24)

CAS_SERVER_URL = "https://login.iiit.ac.in/cas/"
SERVER_URL = os.getenv("SERVER_URL")
if not SERVER_URL:
    raise ValueError("SERVER_URL environment variable is not set.")
SERVICE_URL = SERVER_URL + "Get_Auth"
REDIRECT_URL = SERVER_URL + "Get_Auth"

cas_client = CASClient(
    version=3,
    service_url=f"{SERVICE_URL}?next={quote_plus(REDIRECT_URL)}",
    server_url=CAS_SERVER_URL,
)

class Round:
    def __init__(self, round_num):
        self.number = round_num
        self.upload_folder = f'./static/round{round_num}/'
        self.details_filepath = f'./round{self.number}.json'
        os.makedirs(self.upload_folder, exist_ok=True)
        self.voting_open = False
        self.active = False # Can participants submit to this round?
        self.selected_filepaths = []
        # self.unselected_filepaths = []
        self.votes = {} # A map from voter's uid to voted filepath
        try:
            with open(self.details_filepath, 'r') as f:
                details = json.loads(f.read())
                self.votes = details['votes']
                self.selected_filepaths = details['selected_filepaths']
                # self.unselected_filepaths = details['unselected_filepaths']
                self.active = details['active']
                self.voting_open = details['voting_open']
        except:
            pass
    
    def save(self):
        with open(self.details_filepath, 'w') as f:
            json.dump({
                "votes": self.votes,
                "selected_filepaths": self.selected_filepaths,
                # "unselected_filepaths": self.unselected_filepaths,
                "active": self.active,
                "voting_open": self.voting_open,
            }, f)
    
    def __repr__(self):
        return f"Round {self.number} - Active: {self.active}, Voting Open: {self.voting_open}, Selected Files: {len(self.selected_filepaths)}"

roundsList = [Round(n) for n in range(7)]

admins = [
    'adithya.kishor',
    'krish.pandya',
    'gautam.bhetanabhotla',
    'vigneshvembar.m',
    'saloni.goyal',
    'virat.garg',
    'manas.agrawal',
    'aishani.sood',
    'tatva.agarwal',
    'neharika.rajesh',
    'sanjana.punna',
    'nikhita.ravi',
    'kandagatla.akshith',
    'samarth.jain',
    'maithily.bhala',
]

def current_user_attributes():
    if 'token' in session:
        token = session['token']
        with open('key.key', 'rb') as file:
            key = file.read()
        fernet = Fernet(key)
        attributes_json = fernet.decrypt(token).decode()
        attributes = json.loads(attributes_json)
        return attributes
    return None

@app.template_filter('remove_first_dir')
def remove_first_dir(path):
    # Remove ./static/ prefix to work with Flask's url_for('static', ...)
    if path.startswith('./static/'):
        return path[9:]  # Remove './static/'
    elif path.startswith('static/'):
        return path[7:]  # Remove 'static/'
    return path

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
            user, attributes, _ = cas_client.verify_ticket(ticket)
            if not attributes:
                return "Invalid ticket"
            if user:
                for k, v in attributes.items():
                    print(k, ": ", v)
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
    attr = current_user_attributes()
    if attr:
        return render_template('index.html', user=attr['FirstName'], rounds=roundsList)
    else:
        return redirect('/login')

@app.route('/round/<int:round_number>', methods=['POST', 'GET'])
def round_handler(round_number):
    r: Round = roundsList[round_number]
    if not r.active: return redirect('/')
    if request.method == 'POST':
        # Handle submission for this round
        if 'file1' not in request.files:
            return 'No file attached!'
        file1 = request.files['file1']
        if not file1.filename:
            return 'Please enter a file name!'
        attributes = current_user_attributes()
        if not attributes: return redirect('/login')
        fname = attributes['uid']+'.' + file1.filename.split('.')[-1] # Example filename: gautam.bhetanabhotla.png
        # path = os.path.join(app.config[f'UPLOAD_FOLDER_{round_number}'], fname)
        path = os.path.join(r.upload_folder, fname)
        file1.save(path)
        r.save()
        return render_template(f'round_submission.html', number=r.number)
    # Otherwise get round submission form
    return render_template(f'round_submission.html', number=r.number)

@app.route('/admin')
def admin():
    attr = current_user_attributes()
    if attr:
        if attr['uid'] in admins:
            print(roundsList)
            return render_template('admin.html', rounds=roundsList, user=attr['FirstName'])
        else:
            return redirect('/')
    else:
        return redirect('/login')

@app.route('/admin/round/<int:round_num>')
def adm_round(round_num):
    attr = current_user_attributes()
    if not attr: return redirect('/login')
    r: Round = roundsList[round_num]
    if attr['uid'] in admins:
        return render_template(
            f'round_selection.html',
            files=[os.path.join(r.upload_folder, fname) for fname in os.listdir(r.upload_folder)],
            selected_files=r.selected_filepaths,
            user=attr['FirstName'],
            round_number=r.number,
        )
    else:
        return redirect('/')

@app.route('/select/<int:round_number>')
def select_submission(round_number):
    path = request.args.get('path')
    if not path: return redirect('/admin')
    r: Round = roundsList[round_number]
    if path not in r.selected_filepaths:
        r.selected_filepaths.append(path)
        r.save()
    return redirect(f'/admin/round/{round_number}')

@app.route('/unselect/<int:round_number>')
def unselect(round_number):
    path = request.args.get('path')
    if not path: return redirect('/admin')
    r: Round = roundsList[round_number]
    if path in r.selected_filepaths:
        r.selected_filepaths.remove(path)
        r.save()
    return redirect(f'/admin/round/{round_number}')

@app.route('/admin_dashboard')
def admin_dashboard():
    attributes = current_user_attributes()
    if attributes:
        if attributes['uid'] in admins:
            return render_template('admin_dashboard.html', rounds=roundsList)
        else:
            return redirect('/')
    else:
        return redirect('/login')

@app.route('/toggle_state/<string:type>/<int:index>', methods=['POST'])
def toggle_state(type, index):
    if type == 'round' and 0 <= index < len(roundsList):
        r: Round = roundsList[index]
        r.active = not r.active
        r.save()
        return jsonify({'success': True})
    elif type == 'vote' and 0 <= index < len(roundsList):
        r: Round = roundsList[index]
        r.voting_open = not r.voting_open
        r.save()
        return jsonify({'success': True})
    return jsonify({'success': False}), 400

@app.route('/vote/<int:round_number>', methods=['POST', 'GET'])
def vote(round_number):
    attr = current_user_attributes()
    if not attr: return redirect('/login')
    r: Round = roundsList[round_number]
    if not r.voting_open: return redirect('/')
    if request.method == 'POST':
        path = request.form['selectedImage']
        uid = attr['uid']
        r.votes[uid] = path
        r.save()
        return redirect('/')
    return render_template('vote.html', selected_files=r.selected_filepaths, round_number=r.number)  

@socketio.on('livevote')
def handle_live_vote(data):
    attr = current_user_attributes()
    r: Round = roundsList[data['round_number']]
    if not attr: return
    r.votes[attr['uid']] = data['path']
    r.save()
    emit('update_livevote', data['path'], broadcast=True)

@app.route('/result/<int:round_number>')
def result(round_number):
    r: Round = roundsList[round_number]
    attr = current_user_attributes()
    if not attr: return redirect('/login')
    uid = attr['uid']
    # if uid in admins:
    #     max_votes = max(votes_r1.values(), default=1) 
    #     return render_template('round_result.html', votes=votes_r1, max_votes=max_votes)
    return redirect('/')

if __name__ == '__main__':
    key = Fernet.generate_key()
    with open('key.key', 'wb') as file:
        file.write(key)
    # app.run(debug=True, host='0.0.0.0')
    socketio.run(app, '0.0.0.0', debug=True)
