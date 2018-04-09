from flask import Flask, render_template, request
import pymysql
import requests
import json

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='123Ace1994@',
                             db='new_database',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

app = Flask(__name__,static_url_path="/static")

@app.route('/get_schools', methods = ['GET'])
def get_school():
    with connection.cursor() as cursor:
    # Read a single record
        school_name = request.args.get('school_name')
        sql = "SELECT * FROM schools where school=%s"
        cursor.execute(sql, (school_name,))
        results = cursor.fetchall()
        schools = list()

        for i in range(len(results)):
            school = results[i]
            schools.append(school)
        #print(schools)
        return json.dumps(schools)

# def file_upload():
#     with connection.cursor() as cursor:
