# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 08:14:30 2024

@author: OMD
"""

from flask import Flask, request, render_template
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField,IntegerField,FloatField, SubmitField,SelectField
from wtforms.validators import DataRequired, NumberRange

import math
import sqlite3
import pandas as pd
from waitress import serve

app = Flask(__name__)
"""app.secret_key = 'm0t%d6%pa55e%1ndechifrabl6'
csrf = CSRFProtect(app)

class Monformulaire(FlaskForm):
    item = SelectField('Sélectionnez Votre entreprise', choices=[])
    montant = StringField('montant',validators=[DataRequired(), NumberRange(min=0)])
    annual_rate=FloatField('annual_rate', validators=[DataRequired(), NumberRange(min=0, max=99)])
    salary=FloatField('salary',validators=[DataRequired(), NumberRange(min=0)])
    month=IntegerField('month',validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Calculer')"""
@app.route('/')
def home():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM entreprise').fetchall()
    conn.close()
    
    return render_template('index.html', items=items)    

def get_db_connection():
    conn = sqlite3.connect('database.db')
    
     # Lire le fichier CSV
    df = pd.read_excel('database2.xlsx')
     # Écrire le DataFrame dans une table SQLite
    df.to_sql('enteprise2', conn, if_exists='replace', index=True)

    conn.row_factory = sqlite3.Row

    # Fermer la connexion
   # conn.close()

    return conn

def simulate_credit(principal, salary, annual_rate, months):
    # Calcul du taux mensuel
    monthly_rate = annual_rate / 100 / 12
    # Nombre de paiements mensuels
    num_payments = months
    # Calcul du paiement mensuel
    monthly_payment = principal * (monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)
    monthly_payment=int(monthly_payment)
    # Vérification de l'abordabilité
    affordable = monthly_payment <= (salary / 3)
    
    return monthly_payment, affordable
   

   

@app.route('/simulate', methods=['POST'])
def simulate():
    montant = float(request.form['montant'])
    annual_rate = float(request.form['annual_rate'])
    months = int(request.form['months'])
    salary=float(request.form['salary'])
    
    monthly_payment,abordable= simulate_credit(montant,salary,annual_rate,months)
    
    return render_template('result.html', monthly_payment=monthly_payment,abordable=abordable)

if __name__ == '__main__':
   # app.run(debug=True)
    serve(app, host="0.0.0.0",port=5000)
