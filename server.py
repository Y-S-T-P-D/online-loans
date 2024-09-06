# -*- coding: utf-8 -*-
"""
Created on Mon Aug 19 08:14:30 2024

@author: OMD
"""
# pour le SF
import os

# pour l'api
from flask import Flask, request, render_template,redirect, url_for
from oauthlib.oauth2 import WebApplicationClient
import requests
import json

# pour la securite
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField,IntegerField,FloatField, SubmitField,SelectField
from wtforms.validators import DataRequired, NumberRange

# pour les fonctions mathematiques
import math

# pour la bd
import sqlite3
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import column_property
from sqlalchemy import Table, MetaData

# pour le serveur en production
from waitress import serve


from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
import math

# Se positionner dans le meme dosssier que le projet
basedir = os.path.abspath(os.path.dirname(__file__))

# variable globale contenant un booleen du type de credit
type;
i=0
app = Flask(__name__)

#app.secret_key = 'YOUR_SECRET_KEY'


with app.app_context():
    
    # joindre la base de donnees database.db situer dans l'emplacement courant du fichier server
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///"+ os.path.join(basedir,"database.db")
    db = SQLAlchemy(app)
    
    # Charger les métadonnées
    metadata = MetaData()
    metadata.reflect(bind=db.engine)

# Charger la table existante
    enteprise2 = Table('enteprise2', metadata, autoload_with=db.engine)
    utilisateurs=Table('utilisateur',metadata,autoload_with=db.engine)
   # nombre=Table('comptage', metadata,autoload_with=db.engine)

class Utilisateur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    telephone = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
   
    
# pour la securite    
"""
class Enteprise2(db.Model):
    index = db.Column(db.Integer, primary_key=True)
    NOMS_DES_ENTREPRISES = db.Column(db.String(80), nullable=False)
    DUREE_MAX = column_property(db.Column(db.Float, nullable=False)) # Colonne que vous souhaitez récupérer
    Taux_Cresco=column_property(db.Column(db.Float, nullable=False))
    Taux_Amort=column_property(db.Column(db.Float, nullable=False))
"""
"""app.secret_key = 'm0t%d6%pa55e%1ndechifrabl6'
csrf = CSRFProtect(app)

class Monformulaire(FlaskForm):
    item = SelectField('Sélectionnez Votre entreprise', choices=[])
    montant = StringField('montant',validators=[DataRequired(), NumberRange(min=0)])
    annual_rate=FloatField('annual_rate', validators=[DataRequired(), NumberRange(min=0, max=99)])
    salary=FloatField('salary',validators=[DataRequired(), NumberRange(min=0)])
    month=IntegerField('month',validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Calculer')"""
    # login 
    
   
@app.route('/')
def home():
        return redirect(url_for('login'))
    
@app.route('/register1',methods=['GET'])
def register1():
  return render_template('register.html')   
  
@app.route('/login', methods=['GET', 'POST'])
def login():
     
        if request.method == 'POST':
                email = request.form['email']
                telephone= request.form['telephone']
                
                selected_item = db.session.query(utilisateurs).filter_by(email=email).first()

                selected_item1 = db.session.query(utilisateurs).filter_by(telephone=telephone).first()

                if selected_item and selected_item1 :
                    
                # Ajoutez ici la logique de validation des utilisateurs
                  return  render_template('type.html')
              
                else :
                    error="erreur"
                    return render_template('login.html',error=error)
        else:
                return render_template('login.html')


@app.route('/type1')
def type1():
    return render_template('type.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
     
        if request.method == 'POST':
                username = request.form['username']
                telephone= request.form['telephone']
               
                email= request.form['email']
                        
                new_user = Utilisateur(username=username, telephone=telephone,  email=email)
                db.session.add(new_user)
                db.session.commit()
                return render_template('login.html')
                
                    #error="erreur"
                    #return render_template('register.html',error=error)
                     
               

                # Ajoutez ici la logique de validation des utilisateurs
                #return  render_template('type.html')
        else:
                return render_template('register.html')

    
@app.route('/type', methods=['GET','POST'])
def type():
    global type
    type=int(request.form['type'])
  
    with app.app_context():
     items= db.session.query(enteprise2).all()
   
    return render_template('credit.html', items=items)
      

def get_db_connection():
    #conn = sqlite3.connect('database.db')
    
     # Lire le fichier CSV
   # df = pd.read_excel('database2.xlsx')
     # Écrire le DataFrame dans une table SQLite
   # df.to_sql('enteprise2', db, if_exists='replace', index=True)

    #conn.row_factory = sqlite3.Row

    # Fermer la connexion
   # conn.close()

    return db

def simulate_credit(principal, salary, annual_rate, months):
    
    # Calcul du taux mensuel
    monthly_rate = annual_rate / 12
    # Nombre de paiements mensuels
    num_payments = months
    # Calcul du paiement mensuel
    monthly_payment = principal * (monthly_rate * (1 + monthly_rate) ** num_payments) / ((1 + monthly_rate) ** num_payments - 1)
    monthly_payment=int(monthly_payment)
    # Vérification de l'abordabilité
    affordable = monthly_payment <= (salary*45/100)
    
    return monthly_payment, affordable
   
def simulate_montant(salary,annual_rate,months):  
     
     # Calcul du montant maximal mensuel que le client peut rembourser
     monthly_payment=salary*(45/100)
     
     # Conversion du taux d'intérêt annuel en taux mensuel
     monthly_rate=annual_rate/12
    
     
     # Calcul du montant maximal mensuel que le client peut rembourser
     montant_max=monthly_payment/ (monthly_rate / (1 -( 1+ monthly_rate) ** (-months)))
     
                                   

     return monthly_payment,montant_max
 
    

def simulate_duree(salary, annual_rate, montant):         #monthly_payment, months =simulate_duree(salary, annual_rate, montant)

    monthly_rate = annual_rate / 12 
    monthly_payment_max = salary * 0.45
    monthly_payment = montant * monthly_rate / (1 - (1 + monthly_rate) ** (-12))
    
    if monthly_payment >monthly_payment_max :
        monthly_payment=monthly_payment_max
        
      
        
    months = math.log(1 - (montant * monthly_rate / monthly_payment)) / math.log(1 + monthly_rate)
    months=-months
    return monthly_payment, months


    def calculer_duree_et_mensualite(salaire, taux_annuel, montant):
    # Taux mensuel
     taux_mensuel = taux_annuel / 12 / 100
    
    # Paiement mensuel maximum basé sur 45% du salaire
     paiement_mensuel_max = salaire * 0.45
    
    # Formule pour calculer la mensualité
     mensualite = montant * taux_mensuel / (1 - (1 + taux_mensuel) ** -360)
    
    # Ajuster la mensualité si elle dépasse le paiement mensuel maximum
     if mensualite > paiement_mensuel_max:
            mensualite = paiement_mensuel_max
        
    # Formule pour calculer le nombre de mois
     nombre_de_mois = math.log(1 - (montant * taux_mensuel / mensualite)) / math.log(1 + taux_mensuel)
    
    # Convertir en nombre de mois positif
     nombre_de_mois = -nombre_de_mois
    
     return math.ceil(nombre_de_mois), mensualite
    
@app.route('/count_user')
def compte():
    
    count = db.session.query(func.count(Utilisateur.id)).scalar()
    print(f"Nombre d'enregistrements : {count}")
    return str(count)
 
@app.route('/count_simulation')
def compte1():
    
    #count = db.session.query(func.count(Utilisateur.id)).scalar()
    print(f"Nombre d'enregistrements : {i}")
    return str(i)
   

@app.route('/simulate', methods=['POST'])
def simulate():
     global type
     global i
     i+=1
     # recuperer les differentes valeurs du formulaire
     salary=float(request.form['salary'])   
     index= int(request.form['index'])
     
     if(request.form.get('months') and request.form.get('montant')) :  
        months = float(request.form['months'])
        montant=float(request.form['montant'])
        # selectionner dans la table l'enregistrement qui correspond a l'id index
        selected_item = db.session.query(enteprise2).filter_by(index=index).first() 
        if selected_item:
            
            # a la variable DUREE_MAX on affecte la duree maximale pouvant etre atteint par le client en fonction de son entreprise
            DUREE_MAX=selected_item.DUREE_MAX
            if type==1 :
              annual_rate = selected_item.Taux_Cresco  # Récupérer la valeur de la colonne souhaitée
            else :
              annual_rate=selected_item.Taux_Amort  
              
          
       # verifier si la duree qu'il a entrez ne depasse pas la valeur maximale
        abordable1=(DUREE_MAX >= months)
       
        monthly_payment,abordable= simulate_credit(montant,salary,annual_rate,months)
        
        return render_template('result.html', monthly_payment=monthly_payment,abordable=abordable,abordable_duree=abordable1)
     elif request.form.get('months') and (not request.form.get('montant')) : 
             months=float(request.form['months'])
             selected_item = db.session.query(enteprise2).filter_by(index=index).first()
             if selected_item:
                 DUREE_MAX=selected_item.DUREE_MAX
                 if type==1 :
                   annual_rate = selected_item.Taux_Cresco  # Récupérer la valeur de la colonne souhaitée
                 else :
                   annual_rate=selected_item.Taux_Amort  
             monthly_payment,montant_max=simulate_montant(salary,annual_rate,months)
             
             if DUREE_MAX>=months :
                 abordable_duree=True
                 return render_template('result.html',monthly_payment=monthly_payment,abordable_duree=abordable_duree)
             else :
                 return render_template('result.html',abordable_duree=abordable_duree)
 
                
         
     elif (not request.form.get('months') ) and (request.form.get('montant')):
              
                # selectionner dans la table l'enregistrement qui correspond a l'id index
                montant=float(request.form['montant'])
                selected_item = db.session.query(enteprise2).filter_by(index=index).first() 
                if selected_item:
                    
                    # a la variable DUREE_MAX on affecte la duree maximale pouvant etre atteint par le client en fonction de son entreprise
                    DUREE_MAX=selected_item.DUREE_MAX
                    if type==1 :
                      annual_rate = selected_item.Taux_Cresco  # Récupérer la valeur de la colonne souhaitée
                    else :
                      annual_rate=selected_item.Taux_Amort  
                      
                monthly_payment, months =simulate_duree(salary, annual_rate, montant)
                
                abordable1=(DUREE_MAX>=months)
                
               
                return render_template('result2.html',monthly_payment=int(monthly_payment),months=int(months),abordable1=int(abordable1))
                
                
     else :
                 selected_item = db.session.query(enteprise2).filter_by(index=index).first()
                 if selected_item:
                     months1=selected_item.DUREE_MAX
                     if type==1 :
                       annual_rate = selected_item.Taux_Cresco  # Récupérer la valeur de la colonne souhaitée
                     else :
                       annual_rate=selected_item.Taux_Amort  
                 
                     monthly_payment,montant_max=simulate_montant(salary,annual_rate,months1)
                     months1=int(montant_max//monthly_payment)
                 
                 return render_template('result1.html',monthly_payment=int(monthly_payment),montant_max=int(montant_max),months1=int(months1))
         
       
       
       
              
     





if __name__ == '__main__':
    app.run(debug=True)
    ##serve(app, host="0.0.0.0",port=5000)
    