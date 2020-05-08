from flask import Flask, render_template, request
from .pyramid import Pyramid
import pandas as pd
import numpy as np
from math import floor
import io
import base64
from datetime import datetime as dt
import seaborn as sb
import matplotlib.pyplot as plt
sb.set(style='whitegrid')


def create_app():
    app = Flask(__name__)

    @app.route('/')
    def root():
        return render_template('base.html')
    
    @app.route('/pyramid', methods=['POST'])
    def user_pyramid():
        csv = request.values['csv']
        p = Pyramid(csv)
        pic_hash = p.show_pyramids() 
        return render_template('pyramid.html', pic_hash=pic_hash)
        # TODO: pass in url from url input in 'root'
        # edit pyramid class to return base64 encoded image


    return app
