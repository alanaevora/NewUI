# NewUI

HOW THE FILES INTERACT WITH EACH OTHER
The file app.py is the file that runs
Template directory = html files (creates the elements of the UI)
Static / css directory = the style sheet (changes the layout of the UI)
Static / images directory = where the figure images that are created will be stored

GETTING STARTED
Before running app.py, you will need to install these python packages in your environment:

from flask import Flask, render_template, request, redirect, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import numpy as np
import soundfile as sf
import sounddevice as sd


Then you need to initialize the database, type this in the terminal 
(if you are using a python interpreter lower than 3.0, then just type python instead of python3)

python3
from app import db
db.create_all()

To run the app.py file (and make the UI appear in your default browser), type this in the terminal
(again, if you are using a python interpreter lower than 3.0, type python instead of python3)

python3 app.py

If you make significant changes to the code in the app.py file, you may need to re-run app.py
In order to do this, just retype python3 app.py in the terminal


READ BELOW ONCE YOU LOOK OVER THE CODE IN APP.PY
The Todo class stores the user entries in the database
The controllers communicate between the model/database and the view/hmtl files
The controllers might also call functions at the bottom of the file that "do" a certain action (which is why I called them doers). Examples of this are the function to create the filters and playback the tracks. 

SOME ADDITIONAL NOTES
Since the compensation code isn't fully complete, it may be hard to read/understand right now. But if you have questions let me know!
