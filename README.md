# NewUI

The file app.py is the file that runs

Before running app.py, you will need to install these python packages in your environment:

from flask import Flask, render_template, request, redirect, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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
