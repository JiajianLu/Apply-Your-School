from flask import Flask, render_template, request
import pymysql
import requests
import json
import pandas as pd
import numpy as np

column_dict = {'school_name': 'school=', 'rank1': 'rank>=', 'rank2': 'rank<=',
				 'states':'state in ', 'program_name': 'program_name =', 
				 'degree': 'degree =', 'tuition1': 'tuition >=', 'tuition2': 'tuition <='}

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='123ace1994',
                             db='new_database',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

app = Flask(__name__,static_url_path="/static")

@app.route('/get_table_names', methods = ['GET'])
def get_table_names():
    with connection.cursor() as cursor:
        sql = 'SELECT table_name FROM information_schema.tables where table_schema="new_database"'
        cursor.execute(sql)
        results = cursor.fetchall()
        table_names = list()
        for i in range(len(results)):
            table_name = results[i]
            table_names.append(table_name)
        return json.dumps(table_names)

@app.route('/get_table_columns', methods = ['GET'])
def get_table_columns():
    with connection.cursor() as cursor:
        table = request.args.get('table')
        sql = 'SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = "new_database" AND TABLE_NAME = %s'
        cursor.execute(sql, (table,))
        results = cursor.fetchall()
        column_names = list()
        for i in range(len(results)):
            column_name = results[i]
            column_names.append(column_name)
        return json.dumps(column_names)

@app.route('/get_schools', methods = ['GET'])
def get_school():
    with connection.cursor() as cursor:
    # Read a single record
    	#get school_name from the passed parameters
        school_name = ['school_name', request.args.get('school_name')]
        rank1 = ['rank1', request.args.get('rank1')]
        rank2 = ['rank2', request.args.get('rank2')]
        states_list = request.args.getlist('states')
        if len(states_list)==1:
        	states_list = "('" + str(states_list[0])+"')"
        else:
        	states_list = tuple(states_list)
        states = ['states', states_list]
        conditions = [school_name, rank1, rank2, states]
        not_empty_conditions = []
        for condition in conditions:
        	if condition[1]:
        		not_empty_conditions.append(condition)
        sql = "SELECT * FROM new_schools WHERE "
        
        for condition in not_empty_conditions:
        	if condition[1]:
        		#if isinstance(condition[1])
        		sql += column_dict[condition[0]] + str(condition[1]) + ' '
        		if condition != not_empty_conditions[-1]:
        			sql += 'AND '
        print(sql)
        cursor.execute(sql)

        results = cursor.fetchall()
        schools = list()
        for i in range(len(results)):
            school = results[i]
            schools.append(school)
        #print(schools)
        return json.dumps(schools)

@app.route('/get_programs', methods = ['GET'])
def get_programs():
    with connection.cursor() as cursor:
        program_name = request.args.get('program_name')
        rank1 = request.args.get('rank1')
        rank2 = request.args.get('rank2')
        degree = request.args.get('degree')
        tuition1 = request.args.get('tuition1')
        tuition2 = request.args.get('tuition2')
        conditions = [rank1, rank2, states]
        #if condtion is not empty, then append sql
        conditions = [program_name, rank1, rank2, degree, tuition1, tuition2]
        not_empty_conditions = []
        for condition in conditions:
        	if condition[1]:
        		not_empty_conditions.append(condition)
        sql = "SELECT * FROM programs WHERE "
        
        for condition in not_empty_conditions:
        	if condition[1]:
        		#if isinstance(condition[1])
        		sql += column_dict[condition[0]] + str(condition[1]) + ' '
        		if condition != not_empty_conditions[-1]:
        			sql += 'AND '
        print(sql)
        cursor.execute(sql)

        results = cursor.fetchall()
        programs = list()
        for i in range(len(results)):
            program = results[i]
            schools.append(program)
        #print(schools)
        return json.dumps(programs)
#API for uploading json files

@app.route('/import', methods = ['POST'])
def file_upload():
    with connection.cursor() as cursor:
        print(request.files)
        print(request.files['csv_file'])
        table = request.args.get('table')
        print(table)
        uploaded_files = pd.read_csv(request.files['csv_file'])

        results = list()
        column_names = uploaded_files.columns.values.tolist()
        #read every row in the json files and insert it into the corresponding table
        num_string = ','.join(['%s'] * len(column_names))
        num_rows = ','.join(['('+num_string + ')'] * len(uploaded_files))
        sql = "INSERT INTO " + table + " (%s) "
        sql = sql % (num_string,)
        columns = tuple()
        for column_name in column_names:
            columns += (column_name,) #add table column names
        print(sql)
        print(columns)
        sql = sql % columns
        sql +=   "VALUES %s"
        sql = sql % (num_rows,)
        value = tuple()
        for i in range(len(uploaded_files)):
            row_values = uploaded_files.loc[i].tolist()
            for row_value in row_values:#add values in each row
                if isinstance(row_value, np.int64):
                    value+= (int(row_value),)
                else:
                    value+= (row_value,)
        print(sql)
        print(value)
        cursor.execute(sql, value)
    connection.commit()
    return "Data imported!"