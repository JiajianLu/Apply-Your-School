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
	get_contents = requests.get("http://localhost:5001/get_"+table, params = params)
	contents = get_contents.json()
	return contents

@app.route('/search/<table>', methods = ['GET'])
def get_search(table):
	template = 'search_'+ table + '.html'
	return render_template(template)

@app.route('/index', methods = ['GET'])
def get_index():
	return render_template('Homepage.html')

@app.route('/search/schools', methods = ['POST'])
def post_search():
	name = request.form.get('school_name') #get form element according to name
	tuition1 = request.form.get('tuition_range1')
	tuition2 = request.form.get('tuition_range2')
	ar1 = request.form.get('ar_range1') 
	ar2 = request.form.get('ar_range2') 
	size1 = request.form.get('size_range1')
	size2 = request.form.get('size_range2')
	campus1 = request.form.get('campus_range1')
	campus2 = request.form.get('campus_range2')
	sat1 = request.form.get('sat_range1')
	sat2 = request.form.get('sat_range2')
	act1 = request.form.get('act_range1')
	act2 = request.form.get('act_range2')
	states = request.form.getlist('states')
	params = {'tuition2': tuition2, 'tuition1': tuition1, 'school_name':name, 'states': states, 'ar1':ar1, 'ar2':ar2, 'size1':size1, 'size2': size2, 'campus1':campus1, 'campus2': campus2,
	'sat1': sat1, 'sat2':sat2, 'act1':act1, 'act2': act2
	}
	get_schools = requests.get("http://localhost:5001/get_schools", params = params)
	schools = get_schools.json()
	return render_template("search_schools.html", contents = schools)

@app.route('/search/programs', methods = ['POST'])
def post_program_page():
	department_name = request.form.get('department') #get form element according to name
	school_name = request.form.get('school_name') #get form element according to name
	degree = request.form.get('degree')
	tuition1 = request.form.get('tuition_range1')
	tuition2 = request.form.get('tuition_range2')
	salary1 = request.form.get('salary_range1')
	salary2 = request.form.get('salary_range2')
	params = {'school_name': school_name,'salary1': salary1, 'salary2': salary2,'department_name':department_name, 'degree': degree, 'tuition1': tuition1, 'tuition2': tuition2}
	get_programs = requests.get("http://localhost:5001/get_programs", params = params)
	programs = get_programs.json()
	return render_template("search_programs.html", contents = programs)

@app.route('/search/rankings', methods = ['POST'])
def post_ranking_page():
	school_name = request.form.get('school_name')
	source = request.form.getlist('source')
	rank1 = request.form.get('ranking_range1')
	rank2 = request.form.get('ranking_range2')
	params = {'source': source, 'school_name': school_name}
	get_rankings = requests.get("http://localhost:5001/get_rankings", params = params)
	rankings = get_rankings.json()
	return render_template("search_rankings.html", contents = rankings)

@app.route('/search/cities', methods = ['POST'])
def post_cities_page():
	city_name = request.form.get('city_name') #get form element according to name
	states = request.form.getlist('states') #get form element according to name
	pop1 = request.form.get('pop_range1')
	pop2 = request.form.get('pop_range2')
	tem1 = request.form.get('tem_range1')
	tem2 = request.form.get('tem_range2')
	crime1 = request.form.get('crime_range1')
	crime2 = request.form.get('crime_range2')
	house1 = request.form.get('house_range1')
	house2 = request.form.get('house_range2')
	params = {'city_name': city_name, 'states': states, 'pop2': pop2, 'pop1': pop1,'tem2':tem2, 'tem1': tem1, 'crime2': crime2, 'crime1': crime1, 'house2': house2, 'house1': house1}
	get_cities = requests.get("http://localhost:5001/get_cities", params = params)
	cities = get_cities.json()
	return render_template("search_cities.html", contents = cities)

@app.route('/search/professors', methods = ['POST'])

def post_professors_page():
	school_name = request.form.get('school_name') #get form element according to name
	specialty = request.form.get('specialty')
	department_name = request.form.get('department_name')
	states = request.form.getlist('states')
	params = {'school_name': school_name, 'specialty': specialty, 'department_name': department_name, 'states': states}
	print(params)
	get_professors = requests.get("http://localhost:5001/get_professors", params = params)

	professors = get_professors.json()
	return render_template("search_professors.html", contents = professors)

@app.route('/import', methods = ['GET'])
def get_import():
	tables = get_tables()
	return render_template('import.html', tables = tables)

@app.route('/import', methods = ['POST'])
def post_data():
	uploaded_files = request.files['file[]']
	table = request.form.get("table")
	columns = pd.read_csv(uploaded_files,nrows=1,header=None).loc[0].tolist()
	uploaded_files.read()
	uploaded_files.seek(0)
	files = {'csv_file': uploaded_files}
	print(files)
	params = {'table': table}
	tables = get_tables()
	contents = requests.post("http://localhost:5001/import", files= files, params=params)
	contents = contents.json()
	print(contents)
	return render_template('import.html', tables = tables, contents = contents)

@app.route('/search/advanced', methods = ['POST'])
def advanced_search():
	interest = request.form['optradio'] #get value from radio tag
	school_name = request.form.get('school_name') #get form element according to name
	specialty = request.form.get('specialty')
	department_name = request.form.get('department_name')
	city_name = request.form.get('city_name') #get form element according to name
	states = request.form.getlist('states') #get form element according to name
	pop1 = request.form.get('pop_range1')
	pop2 = request.form.get('pop_range2')
	tem1 = request.form.get('tem_range1')
	tem2 = request.form.get('tem_range2')
	crime1 = request.form.get('crime_range1')
	crime2 = request.form.get('crime_range2')
	house1 = request.form.get('house_range1')
	house2 = request.form.get('house_range2')
	source = request.form.getlist('source')
	rank1 = request.form.get('ranking_range1')
	rank2 = request.form.get('ranking_range2')
	degree = request.form.get('degree')
	tuition1 = request.form.get('tuition_range1')
	tuition2 = request.form.get('tuition_range2')
	salary1 = request.form.get('salary_range1')
	salary2 = request.form.get('salary_range2')
	ar1 = request.form.get('ar_range1') 
	ar2 = request.form.get('ar_range2') 
	size1 = request.form.get('size_range1')
	size2 = request.form.get('size_range2')
	campus1 = request.form.get('campus_range1')
	campus2 = request.form.get('campus_range2')
	sat1 = request.form.get('sat_range1')
	sat2 = request.form.get('sat_range2')
	act1 = request.form.get('act_range1')
	act2 = request.form.get('act_range2')
	attributes = request.form.getlist('attributes')
	params = {'interest' : interest,
			'city_name': city_name, 'states': states, 
			'pop2': pop2, 'pop1': pop1,'tem2':tem2, 'tem1': tem1, 'crime2': crime2, 'crime1': crime1, 'house2': house2, 'house1': house1,
			'school_name': school_name, 'specialty': specialty, 'department_name': department_name, 
			'ar1':ar1, 'ar2':ar2, 'size1':size1, 'size2': size2, 'campus1':campus1, 'campus2': campus2,
			'sat1': sat1, 'sat2':sat2, 'act1':act1, 'act2': act2,
			'salary1': salary1, 'salary2': salary2, 'degree': degree, 'tuition1': tuition1, 'tuition2': tuition2, 'attributes': attributes}
	contents= requests.post("http://localhost:5001/search/advanced", params=params)
	contents = contents.json()
	content = contents[0]
	def_columns = contents[1]
	sel_columns = contents[2]
	revised_sels = []
	for sel_col in sel_columns:
		if sel_col[0] == '`':
			revised_sel = sel_col[1:-1]
			revised_sels.append(revised_sel)
		else:
			revised_sels.append(sel_col)
	print(revised_sels)
	return render_template("search_advanced.html", contents = content, def_columns = def_columns, sel_columns= revised_sels)