from flask import Flask, render_template, request
import pymysql
import requests
import json
import pandas as pd
import numpy as np
# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='123ace1994',
                             db='new_database',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

app = Flask(__name__,static_url_path="/static")

@app.route('/get_table_names', methods = ['GET'])
def get_talbe_names():
    with connection.cursor() as cursor:
        sql = 'SELECT table_name FROM information_schema.tables where table_schema="new_database"'
        cursor.execute(sql)
        results = cursor.fetchall()
        table_names = list()
        for i in range(len(results)):
            table_name = results[i]
            table_names.append(table_name)
        return json.dumps(table_names)

@app.route('/get_schools', methods = ['GET'])
def get_school():
    with connection.cursor() as cursor:
    # Read a single record
    	#get school_name from the passed parameters
        school_name = request.args.get('school_name')
        if school_name:
            sql = "SELECT * FROM new_schools where school=%s"
            cursor.execute(sql, (school_name,))
            
        else:
            rank1 = request.args.get('rank1')
            rank2 = request.args.get('rank2')
            states = request.args.getlist('states')
            format_strings = ','.join(['%s'] * len(states))
            sql = "SELECT * FROM new_schools where rank>=%s and rank <=%s and state in (%s)"
            sql = sql % ('%s','%s',format_strings) 
            value = (int(rank1), int(rank2))
            for state in states:
                value += (state,)
            print(value)
            cursor.execute(sql, value)
            #not enough arguement for format_strings
        results = cursor.fetchall()
        schools = list()
        for i in range(len(results)):
            school = results[i]
            schools.append(school)
        #print(schools)
        return json.dumps(schools)

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
        sql = "INSERT INTO %s (%s) VALUES %s"
        sql = sql % ('%s', num_string, num_rows)
        value = (table,) #add table name

        for column_name in column_names:
            value += (column_name,) #add table column names

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