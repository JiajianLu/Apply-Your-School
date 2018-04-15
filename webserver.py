import json

from flask import Flask, render_template, request, session
import requests
import pymysql
import pandas as pd

app = Flask(__name__,static_url_path="/static")

api_address = 'https://0.0.0.0:5001/'

def get_tables():
	get_tables = requests.get("http://localhost:5001/get_table_names")
	tables = get_tables.json()
	return tables

def get_schools(school_name = "ALL"):
	params = {'school_name': school_name}
	get_schools = requests.get("http://localhost:5001/get_schools", params = params)
	schools = get_schools.json()
	return schools

def get_schools_by_rank_state(rank1=1, rank2=5, states = ['California']):
	params = {'rank1': rank1, 'rank2': rank2, 'states': states}
	get_schools = requests.get("http://localhost:5001/get_schools", params = params)
	#print(get_schools)
	schools = get_schools.json()
	return schools

def get_programs_by_schoolname(school_name):
	params = {'school_name': school_name}
	get_programs = requests.get("http://localhost:5001/get_schools", params = params)
	programs = get_programs.json()
	return programs

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
	tables = get_tables()
	return render_template('import.html', tables = tables)

@app.route('/import', methods = ['POST'])
def post_data():
	uploaded_files = request.files['file[]']
	table = request.form.get("table")
	print(table)
	print(uploaded_files)
	columns = pd.read_csv(uploaded_files,nrows=1,header=None).loc[0].tolist()
	print(columns)
	files = {'csv_file': uploaded_files}
	print(files)
	params = {'table': table}
	tables = get_tables()
	contents = requests.post("http://localhost:5001/import", files= files, params=params)
	print(contents)
	return render_template('import.html', tables = tables, columns = columns, contents = contents)


@app.route('/<schoolname>', methods = ['GET'])
def program_in_school(schoolname):
	programs = get_programs_by_schoolname(schoolname)
	return render_template("programs.html", contents = programs)