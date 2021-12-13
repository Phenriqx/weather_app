import requests
import os
from flask import Flask, render_template, request, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

API_KEY = os.getenv('API_KEY')

db = SQLAlchemy(app)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
 
 
def get_weather_data(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={ city }&units=metric&appid={ API_KEY }'
    r = requests.get(url).json()
    return r   


@app.route('/', methods=['POST'])
def index_post():
    new_city = request.form.get('city')
    
    if new_city:
        existing_city = City.query.filter_by(name=new_city).first()
        
        if not existing_city:
            city_data = get_weather_data(new_city)
            if city_data['cod'] == 200:
                new_city_obj = City(name=new_city)

                db.session.add(new_city_obj)
                db.session.commit()
            
            else:
                error = 'City does not exist'
                
        else:
            error = 'City already exists!'
            
        
    return redirect(url_for('index_get'))


@app.route('/')
def index_get():
    cities = City.query.all()

    weather_data = []

    for city in cities:

        r = get_weather_data(city.name)
        print(r)

        weather = {
            'city' : city.name,
            'temperature' : round(r['main']['temp']),
            'description' : r['weather'][0]['description'],
            'icon' : r['weather'][0]['icon'],
        }

        weather_data.append(weather)

    return render_template('weather.html', weather_data=weather_data)

@app.route('/delete/<name>')
def delete_city(name):
    city = City.query.filter_by(name=name).first()
    db.session.delete(city)
    db.session.commit()
    return redirect(url_for('index_get'))

if __name__ == '__main__':
    app.run(debug=True)