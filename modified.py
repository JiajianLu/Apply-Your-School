from flask import Flask, render_template, request
import pymysql
import requests
import json

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='123ace1994',
                             db='new_database',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

app = Flask(__name__,static_url_path="/static")

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

@app.route('/import', methods = ['POST'])
def file_upload():
    with connection.cursor() as cursor:
    	#get the list of files
    	print('a')
    	uploaded_files = request.files.getlist("file[]")
    	print(uploaded_files)