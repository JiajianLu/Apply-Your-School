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

def get_table_columns(table):
	params = {'table': table}
	columns = requests.get("http://localhost:5001/get_table_columns", params = params)

def get_detail_content(table, entry):
	params = {'table': table, 'entry': entry}
	get_programs = requests.get("http://localhost:5001/get_schools", params = params)
	programs = get_programs.json()
	return programs

@app.route('/search/<table>', methods = ['GET'])
def get_search(table):
	template = 'search_'+ table + '.html'
	return render_template(template)

@app.route('/search/schools', methods = ['POST'])
def post_search():
	name = request.form.get('school_name') #get form element according to name
	rank1 = request.form.get('ranking_range1')
	rank2 = request.form.get('ranking_range2')
	states = request.form.getlist('states')
		#print(states)
	params = {'school_name':name, 'rank1': rank1, 'rank2': rank2, 'states': states}
	get_schools = requests.get("http://localhost:5001/get_schools", params = params)
	#print(get_schools)
	schools = get_schools.json()
	#print(schools)
	return render_template("Users.html", contents = schools)

@app.route('/search/programs', methods = ['POST'])
def post_program_page():
	name = request.form.get('program_name') #get form element according to name
	rank1 = request.form.get('ranking_range1')
	rank2 = request.form.get('ranking_range2')
	degree = request.form.get('degree')
	tuition1 = request.form.get('tuition_range1')
	tuition2 = request.form.get('tuition_range2')
	params = {'program_name':name, 'rank1': rank1, 'rank2': rank2, 'degree': degree, 'tuition1': tuition1, 'tuition2': tuition2}
	get_programs = requests.get("http://localhost:5001/get_programs", params = params)
	programs = get_programs.json()
	return render_template("find_program.html", contents = programs)

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


@app.route('/<table>/<entry>', methods = ['GET'])
def show_details(table, entry):
	columns = get_table_columns(table)
	pcontents = get_detail_content(table, entry)
	return render_template("Details.html", table = table, columns = columns, contents = contents)