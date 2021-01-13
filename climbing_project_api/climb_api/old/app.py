from flask import Flask, render_template, request, jsonify
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
    
    with app.app_context():

        @app.route('/')
        def root():
            return render_template('base.html')
        
        @app.route('/pyramid', methods=['POST'])
        def user_pyramid():
            print(request)
            data = request.get_json()
            print('type:', type(data))
            print(data)
            try:
                print('Trying')
                csv = data['csv']
                p = Pyramid(csv)
                pic_hash = p.show_pyramids() 
                result = {'pyramid': pic_hash}
                print(pic_hash)
                print('success')
                code =  200
            except:
                result = {'error':'error'}
                code = 400
                print('error')
            #return render_template('pyramid.html', pic_hash=pic_hash)
            return jsonify(result), code


        return app
