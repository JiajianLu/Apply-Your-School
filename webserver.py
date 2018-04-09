import json

from flask import Flask, render_template, request, session
import requests
import pymysql

app = Flask(__name__,static_url_path="/statice")

api_address = 'https://0.0.0.0:5001/'

def get_schools(school_name = "ALL"):
	params = {'school_name': school_name}
	get_schools = requests.get("http://localhost:5001/get_schools", params = params)
	print(get_schools)
	schools = get_schools.json()
	return schools

@app.route('/', methods = ['GET'])
def get_homepage():
	return render_template("Users.html")

@app.route('/', methods = ['POST'])
def post_homepage():
	name = request.form.get('school_name')
	schools = get_schools(name)
	print(schools)
	return render_template("Users.html", contents = schools)

@app.route('/import', methods = ['GET'])
def get_import():
	return render_template('import.html')