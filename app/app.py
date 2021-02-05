from flask import Flask, render_template, request, redirect, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np
import soundfile as sf
import sounddevice as sd


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)    # creating database

# MODEL (store user-input in database)
class Todo(db.Model):
    id = db.Column (db.Integer, primary_key=True)
    # exp_name = db.Column(db.String(100), nullable=False)
    # round_num = db.Column(db.String(50), nullable=False)
    field = db.Column(db.String(20), nullable=False)
    content = db.Column(db.String(50), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    # specifying what to return each time there is new entry
    def __repr__(self):
       return '<Value %r>' % self.content

# CONTROLLERS (post info to view (html), and add user-input to model (database))

@app.route('/', methods=['POST', 'GET'])    # get data from UI & send data to database
def index():
    if request.method == 'POST':    # if submit button was pressed
        return redirect('/design/')
    else:
        return render_template('index.html', values=get_values(), exp_name=get_exp_name(), round_num=get_round_num())    # displays the html file


@app.route('/create/', methods=['POST', 'GET'])    # get data from UI & send data to database
def create():
    if request.method == 'POST':    # if submit button was pressed
        entries = ['low_freq', 'hi_freq', 'fs', 'nfft']
        remove_add(entries)
        calculate_filters()
        return redirect('/create/')
    else:
        return render_template('create.html', values=get_values(), exp_name=get_exp_name(), round_num=get_round_num())    # displays the html file

@app.route('/design/', methods=['POST', 'GET'])
def design():
    if request.method == 'POST':    # if submit button was pressed
        entries = ['exp_name', 'round_num', 'ch_file_1', 'ch_peak_1', 'ch_file_2', 'ch_peak_2', 'ch_file_3', 'ch_peak_3', 'ch_file_4', 'ch_peak_4', 'ch_file_5', 'ch_peak_5', 'ch_file_6', 'ch_peak_6', 'ch_file_7', 'ch_peak_7', 'ch_file_8', 'ch_peak_8']
        remove_add(entries)
        return redirect('/design/')
    else:
        return render_template('design.html', values=get_values(), exp_name=get_exp_name(), round_num=get_round_num())    # displays the html file

@app.route('/calibrate/', methods=['POST', 'GET'])
def calibrate():
    if request.method == 'POST':    # if submit button was pressed
        entries = ['ch_num']
        remove_add(entries)
        return redirect('/calibrate/')
    else:
        return render_template('calibrate.html', values=get_values(), exp_name=get_exp_name(), round_num=get_round_num())    # displays the html file

@app.route('/exemplars/', methods=['POST', 'GET'])
def exemplars():
    if request.method == 'POST':    # if submit button was pressed
        entries = []
        remove_add(entries)
        return redirect('/exemplars/')
    else:
        return render_template('exemplars.html', values=get_values(), exp_name=get_exp_name(), round_num=get_round_num())    # displays the html file


@app.route('/playback/', methods=['POST', 'GET'])
def playback():
    if request.method == 'POST':    # if submit button was pressed
        entries = ['ch_file_1', 'ch_peak_1', 'ch_file_2', 'ch_peak_2', 'ch_file_3', 'ch_peak_3', 'ch_file_4', 'ch_peak_4', 'ch_file_5', 'ch_peak_5', 'ch_file_6', 'ch_peak_6', 'ch_file_7', 'ch_peak_7', 'ch_file_8', 'ch_peak_8', 'stim_len', 'cycle_len', 'tot_dur']
        remove_add(entries)
        # play_rec()
        export_db()
        return redirect('/playback/')
    else:
        return render_template('playback.html', values=get_values(), exp_name=get_exp_name(), round_num=get_round_num())    # displays the html file

@app.route('/help/', methods=['POST', 'GET'])
def help():
    if request.method == 'POST':    # if submit button was pressed
        entries = []
        remove_add(entries)
        return redirect('/help/')
    else:
        return render_template('help.html', values=get_values(), exp_name=get_exp_name(), round_num=get_round_num())    # displays the html file

# SETTERS

def remove_add(entries):
    print("remove_add")
    for entry in entries:
        value_content = request.form[entry] # new value
        if len(value_content) > 0:  # if the field has a value, then remove the existing value and add the new one
            # delete existing values with the same field
            existing_values = Todo.query.filter(Todo.field.contains(entry)).all()
            for value in existing_values:
                db.session.delete(value)
                db.session.commit()
            # add new value
            new_value = Todo(field=entry, content=value_content)
            try:
                db.session.add(new_value)
                db.session.commit()
            except:
                return 'There was an issue adding your value to the database'


# GETTERS

def get_exp_name():
    print("get_exp_name")
    parts = str(db.session.query(Todo.content).filter_by(field='exp_name').first()).split("'")
    if parts == ['None']:
        exp_name = 'ENTER EXPERIMENT NAME'
    else:
        exp_name = parts[1]
    return exp_name

def get_round_num():
    print("get_round_num")
    parts = str(db.session.query(Todo.content).filter_by(field='round_num').first()).split("'")
    if parts == ['None']:
        round_num = 'ENTER ROUND NUMBER'
    else:
        round_num = parts[1]
    return round_num

def get_values():
    return Todo.query.order_by(Todo.date_created).all()

def getter(field):
    parts = str(db.session.query(Todo.content).filter_by(field=field).first()).split("'")
    if parts == ['None']:
        return
    else:
        value = parts[1]
    return value

# CREATE #############################################

def calculate_filters():
    print("generating filters")

    # GET VALUES FROM DATABASE
    fs = int(getter("fs"))
    nfft = int(getter("nfft"))

    # MAKE RANDOM NOISE
    pb8 = random_noise(fs)

    # SAVE THE NOISE
    pb8ch = pb8     # for testing I dont have 8 channels > FIX LATER
    sf.write('Noise_8ch.wav', pb8ch, fs)  # create wave file & save the random noise in it
    file_reader, sample_rate = sf.read('Noise_8ch.wav')  # open & read random noise file
    
    # FOR TESTING AT HOME I AM GOING TO USE 1 channel
    print("AVAILABLE CHANNELS: \n" + str(sd.query_devices()))
    print("USING THESE CHANNELS: " + str(sd.default.device))

    # RECORDING
    # record to wave file source: https://python-sounddevice.readthedocs.io/en/0.4.1/usage.html#recording
    # possible source for APO: https://python-sounddevice.readthedocs.io/en/0.3.11/#sounddevice.AsioSetting
    print("RECORDING...")
    audio_recorded = sd.playrec(file_reader, fs, channels=1)  # playing and recording simultaneously & saving audio as NumPy array
    sd.wait()  # wait for the recording to finish before moving on
    sf.write('pre-rec.wav', audio_recorded, fs)  # write the audio recorded to file
    
    # ADJUSTING THE AMP
    pre_rec, sample_rate = sf.read('pre-rec.wav')   # open the recorded file
    if max(abs(pre_rec)) > 0.2:                     # still need to figure out what this is doing
        print("exceeds max amp")
        adjust = 0.2 / max(abs(pre_rec))
        pb8ch = adjust * pb8ch
        sf.write('Noise_8ch.wav', pb8ch, fs)
    else:
        print("below max amp")

    fig_files = [plot(pb8)] # will be filters not this one
    return fig_files

# GETTERS

# DOERS
def random_noise(fs):
    # CREATE RANDOM NOISE
    pb = np.random.rand(2 * fs) - 0.5  # generate 2 sec of random noise (vector of evenly spaced random nums)
    win = np.ones(len(pb))  # array of 1s that is the length of the random noise
    ramp = np.linspace(0, np.pi, round(fs/5))   # creates a vector = linspace(min(x), max(x), #points)
    win[0:len(ramp)] = 0.5*np.sin(ramp-np.pi/2) + 0.5   # gradually taper at the beginning
    win[len(win) - len(ramp) : len(win)] = 0.5 * np.cos(ramp) + 0.5  # gradually taper at the end
    pb = pb * win

    # ADDING PADDING TO THE RANDOM NOISE
    padding = np.zeros(round(fs/6))  # array of 0s that is 1/6 of the length of the window
    pb8 = []
    pb8 = np.append(pb8, padding)
    pb8 = np.append(pb8, pb)
    pb8 = np.append(pb8, padding)
    pb8 = np.append(pb8, padding)
    pb8 = np.append(pb8, padding)
    return pb8

@app.route('/plot.png')
def plot(figure):
    # Generate the figure **without using pyplot**.
    fig = Figure(figsize=(8, 2))
    ax = fig.subplots()
    ax.set_ylabel('amp')
    ax.set_xlabel('freq')
    ax.plot(figure)
    file = "static/images/figure.png"
    fig.savefig(file)
    return file


# PLAYBACK #########################################

def play_rec():

    play_file = getter("ch_file_1")
    rec_file = 'new.wav'

    try:
        play_array, sample_rate = sf.read(play_file)
    except FileNotFoundError:
        print(play_file + " is not readable")

    print("PLAYING " + play_file + ". RECORDING " + rec_file + "...")
    rec_array = sd.playrec(play_array, sample_rate, channels=1)
    print("Done recording " + rec_file)
    sd.wait()
    sf.write(rec_file, rec_array, sample_rate)

@app.route('/export_db/')
def export_db():
    try:
        file = open("exp_" + get_exp_name() + "_" + get_round_num() + ".txt", "x")
        values = get_values()
        for value in values:
            file.write(str(value.field) + ": " + str(value.content) + "\n")
        file.close()
    except:
        print("could not create file")
    return redirect('/playback/')

if __name__ == '__main__':
    app.run(debug=True)
