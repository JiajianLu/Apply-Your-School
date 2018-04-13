import json

from flask import Flask, render_template, request, session
import requests
import pymysql

app = Flask(__name__,static_url_path="/static")

api_address = 'https://0.0.0.0:5001/'

def get_schools(school_name = "ALL"):
	params = {'school_name': school_name}
	get_schools = requests.get("http://localhost:5001/get_schools", params = params)
	print(get_schools)
	schools = get_schools.json()
	return schools

def get_schools_by_rank_state(rank1=1, rank2=5, states = ['California']):
	params = {'rank1': rank1, 'rank2': rank2, 'states': states}
	get_schools = requests.get("http://localhost:5001/get_schools", params = params)
	#print(get_schools)
	schools = get_schools.json()
	return schools

@app.route('/', methods = ['GET'])
def get_homepage():
	return render_template("Users.html")

@app.route('/', methods = ['POST'])
def post_homepage():
	name = request.form.get('school_name') #get form element according to name
	if name: #if name is not empty
		schools = get_schools(name)
	else:
		rank1 = request.form.get('ranking_range1')
		rank2 = request.form.get('ranking_range2')
		states = request.form.getlist('states')
		#print(states)
		schools = get_schools_by_rank_state(rank1, rank2, states)
	#print(schools)
	return render_template("Users.html", contents = schools)

@app.route('/import', methods = ['GET'])
def get_import():
	return render_template('import.html')