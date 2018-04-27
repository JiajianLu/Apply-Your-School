from flask import Flask, render_template, request
import pymysql
import requests
import json
import pandas as pd
import numpy as np

column_dict = {'school_name': 'SCHOOL_NAME=', 'rank1': 'rank>=', 'rank2': 'rank<=',
				 'states':'STATE_NAME in ', 
				 'degree': 'DEGREE =', 'tuition1': '`TUITION_($)` >=', 'tuition2': '`TUITION_($)` <=',
                 'salary1': '`AVERAGE_STARTING_SALARY_($)` >=', 'salary2': '`AVERAGE_STARTING_SALARY_($)` <=',
                 'department_name': 'DEPARTMENT=',
                 'sources': 'SOURCE IN ',
                 'city_name': 'CITY_NAME=', 'pop1': 'POPULATION >=', 'pop2': 'POPULATION <=', 'tem1': '`AVERAGE_TEMP_(°F)` >=', 'tem2': '`AVERAGE_TEMP_(°F)` <=',
                 'crime1': 'VIOLENT_CRIME_(PER_100,000_PEOPLE) <=', 'crime2': 'VIOLENT_CRIME_(PER_100,000_PEOPLE) >=',
                 'house2': 'MONTHLY_HOUSING_COSTS_($) <=', 'house1': 'MONTHLY_HOUSING_COSTS_($) >='}

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='123ace1994',
                             db='info257_database',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

def create_links_table():
    with connection.cursor() as cursor:
        cursor.execute("CREATE TABLE IF NOT EXISTS `ADMISSION_STATS` (`SCHOOL_NAME` varchar(50) NOT NULL,`YEAR` int(11) DEFAULT NULL,`ACCEPTANCE_RATE` float DEFAULT NULL,`25TH_PERCENTILE_SAT` float DEFAULT NULL,`50TH_PERCENTILE_SAT` float DEFAULT NULL,`75TH_PERCENTILE_SAT` float DEFAULT NULL,`25TH_PERCENTILE_ACT` float DEFAULT NULL,`50TH_PERCENTILE_ACT` float DEFAULT NULL,`75TH_PERCENTILE_ACT` float DEFAULT NULL,`SIZE` float DEFAULT NULL,PRIMARY KEY (`SCHOOL_NAME`))")
        cursor.execute("CREATE TABLE IF NOT EXISTS `CITY_STATS` (`CITY_NAME` varchar(50) NOT NULL,`STATE_NAME` varchar(10) DEFAULT NULL,`POPULATION` int(11) DEFAULT NULL,`AVERAGE_TEMP_(°F)` float DEFAULT NULL,`PRECIPITATION (INCHES)` float DEFAULT NULL,`VIOLENT_CRIME_(PER_100,000_PEOPLE)` float DEFAULT NULL,`PROPERTY_CRIME_(PER_100,000_PEOPLE)` float DEFAULT NULL,`TOTAL_CRIME_(PER_100,000_PEOPLE)` float DEFAULT NULL,`FATALITY_(PER_100,000_PEOPLE)` float DEFAULT NULL,`MONTHLY_HOUSING_COSTS($)` float DEFAULT NULL,PRIMARY KEY (`CITY_NAME`))")
        cursor.execute("CREATE TABLE IF NOT EXISTS `PROFESSOR_STATS` (`PROFESSOR_NAME` varchar(50) NOT NULL,`SCHOOL_NAME` varchar(50) DEFAULT NULL,`DEPARTMENT` varchar(50) DEFAULT NULL,`SPECIALTY` varchar(50) DEFAULT NULL,`RATINGS` float DEFAULT NULL,`TITLE` varchar(50) DEFAULT NULL,PRIMARY KEY (`PROFESSOR_NAME`))")
        cursor.execute("CREATE TABLE IF NOT EXISTS `PROGRAM_STATS` (`SCHOOL_NAME` varchar(50) NOT NULL,`DEPARTMENT` varchar(50) NOT NULL,`DEGREE` varchar(10) NOT NULL,`TUITION_($)` int(11) DEFAULT NULL,`AVERAGE_LENGTH_(YEAR)` int(11) DEFAULT NULL,`AVERAGE_STARTING_SALARY ($)` int(11) DEFAULT NULL,PRIMARY KEY (`SCHOOL_NAME`,`DEPARTMENT`,`DEGREE`))")
        cursor.execute("CREATE TABLE IF NOT EXISTS `RANKING` (`SOURCE` varchar(50) NOT NULL,`SCHOOL_NAME` varchar(50) NOT NULL,`WORLD_RANKING` int(11) DEFAULT NULL,`YEAR` int(11) DEFAULT NULL,PRIMARY KEY (`SOURCE`,`SCHOOL_NAME`))")
        cursor.execute("CREATE TABLE IF NOT EXISTS `SCHOOL_STATS` (`SCHOOL_NAME` varchar(50) NOT NULL,`AREA_SIZE_(ACRE)` float DEFAULT NULL,`CITY` varchar(50) DEFAULT NULL,`APPLICATION_FEE_($)` int(11) DEFAULT NULL,`EARLY_ACTION_DEADLINE` datetime DEFAULT NULL,`REGULAR_DEADLINE` datetime DEFAULT NULL,PRIMARY KEY (`SCHOOL_NAME`))")
    connection.commit()


app = Flask(__name__,static_url_path="/static")
create_links_table()
@app.route('/get_table_names', methods = ['GET'])
def get_table_names():
    with connection.cursor() as cursor:
        sql = 'SELECT table_name FROM information_schema.tables where table_schema="info257_database"'
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
        sql = 'SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = "info257_database" AND TABLE_NAME = %s'
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
        tuition1 = ['tuition1', request.args.get('tuition1')]
        tuition2 = ['tuition2', request.args.get('tuition2')]
        ar1 = ['ar1', request.args.get('ar1')]
        ar2 = ['ar2', request.args.get('ar2')]
        size1 = ['size1', request.args.get('size1')]
        size2 = ['size2', request.args.get('size2')]
        campus1 = ['campus1', request.args.get('campus1')]
        campus2 = ['campus2', request.args.get('campus2')]
        sat1 = ['sat1', request.args.get('sat1')]
        sat2 = ['sat2', request.args.get('sat2')]
        act1 = ['act1', request.args.get('sat2')]
        act2 = ['act2', request.args.get('act2')]
        states_list = request.args.getlist('states')
        if len(states_list)==1:
        	states_list = "('" + str(states_list[0])+"')"
        else:
        	states_list = tuple(states_list)
        states = ['states', states_list]
        conditions = [school_name, rank1, rank2, states, tuition1, tuition2, ar1, ar2, size1, size2, campus1, campus2, sat1, sat2,act1,act2]
        not_empty_conditions = []
        for condition in conditions:
        	if condition[1]:
        		not_empty_conditions.append(condition)
        sql = "SELECT * FROM SCHOOL_STATS INNER JOIN ADMISSION_STATS ON SCHOOL_STATS.SCHOOL_NAME = ADMISSION_STATS.SCHOOL_NAME WHERE "
        
        for condition in not_empty_conditions:
        	if condition[1]:
        		if isinstance(condition[1],str) and condition[1][0] != '(':
        			condition[1] = "'"+condition[1]+"'"
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
        department_name = ['department_name', request.args.get('department_name')]
        degree = ['degree', request.args.get('degree')]
        tuition1 = ['tuition1', request.args.get('tuition1')]
        tuition2 = ['tuition2', request.args.get('tuition2')]
        salary1 = ['salary1', request.args.get('salary1')]
        salary2 = ['salary2', request.args.get('salary2')]
        school_name = ['school_name', request.args.get('school_name')]
        #if condtion is not empty, then append sql
        conditions = [department_name, school_name, salary1, salary2, rank1, rank2, degree, tuition1, tuition2]
        not_empty_conditions = []
        for condition in conditions:
            if condition[1]:
                not_empty_conditions.append(condition)
        sql = "SELECT * FROM PROGRAM_STATS WHERE "
        
        for condition in not_empty_conditions:
            if condition[1]:
                if isinstance(condition[1],str) and condition[1][0] != '(':
                    condition[1] = "'"+condition[1]+"'"
                sql += column_dict[condition[0]] + str(condition[1]) + ' '
                if condition != not_empty_conditions[-1]:
                    sql += 'AND '
        print(sql)
        cursor.execute(sql)

        results = cursor.fetchall()
        programs = list()
        for i in range(len(results)):
            program = results[i]
            programs.append(program)
        #print(schools)
        return json.dumps(programs)
#API for uploading json files

@app.route('/get_rankings', methods = ['GET'])
def get_rankings():
    with connection.cursor() as cursor:
        school_name = ['school_name', request.args.get('school_name')]
        source = request.args.getlist('source')
        #if condtion is not empty, then append sql
        if len(source)==1:
            source = "('" + str(source[0])+"')"
        else:
            source = tuple(source)
        sources = ['sources', source]
        conditions = [sources, school_name]
        not_empty_conditions = []
        for condition in conditions:
            if condition[1]:
                not_empty_conditions.append(condition)
        sql = "SELECT * FROM RANKING WHERE "
        
        for condition in not_empty_conditions:
            if condition[1]:
                if isinstance(condition[1],str) and condition[1][0] != '(':
                    condition[1] = "'"+condition[1]+"'"
                sql += column_dict[condition[0]] + str(condition[1]) + ' '
                if condition != not_empty_conditions[-1]:
                    sql += 'AND '
        print(sql)
        cursor.execute(sql)
        results = cursor.fetchall()
        rankings = list()
        for i in range(len(results)):
            ranking = results[i]
            rankings.append(ranking)
        #print(schools)
        return json.dumps(rankings)

@app.route('/get_cities', methods = ['GET'])
def get_cities():
    with connection.cursor() as cursor:
        city_name = ['city_name', request.args.get('city_name')]
        states_list = request.args.getlist('states')
        if len(states_list)==1:
            states_list = "('" + str(states_list[0])+"')"
        else:
            states_list = tuple(states_list)
        states = ['states', states_list]
        pop1 = ['pop1', request.args.get('pop1')]
        pop2 = ['pop2', request.args.get('pop2')]
        tem1 = ['tem1', request.args.get('tem1')]
        tem2 = ['tem2', request.args.get('tem2')]
        crime1 = ['crime1', request.args.get('crime1')]
        crime2 = ['crime2', request.args.get('crime2')]
        house1 = ['house1', request.args.get('house1')]
        house2 = ['house2', request.args.get('house2')]
        conditions = [city_name, states, pop1, pop2, tem1, tem2, crime1, crime2, house1, house2]
        not_empty_conditions = []
        for condition in conditions:
            if condition[1]:
                not_empty_conditions.append(condition)
        sql = "SELECT * FROM CITY_STATS WHERE "
        
        for condition in not_empty_conditions:
            if condition[1]:
                if isinstance(condition[1],str) and condition[1][0] != '(':
                    condition[1] = "'"+condition[1]+"'"
                sql += column_dict[condition[0]] + str(condition[1]) + ' '
                if condition != not_empty_conditions[-1]:
                    sql += 'AND '
        print(sql)
        cursor.execute(sql)

        results = cursor.fetchall()
        cities = list()
        for i in range(len(results)):
            city = results[i]
            cities.append(city)
        #print(schools)
        return json.dumps(cities)

@app.route('/import', methods = ['POST'])
def file_upload():
    with connection.cursor() as cursor:
        table = request.args.get('table')
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
            column_name = '`'+column_name+'`'
            columns += (column_name,) #add table column names
        sql = sql % columns
        sql +=   "VALUES %s"
        sql = sql % (num_rows,)
        value = tuple()
        for i in range(len(uploaded_files)):
            row_values = uploaded_files.loc[i].tolist()
            for row_value in row_values:#add values in each row
                if isinstance(row_value, np.int64):
                    value+= (int(row_value),)
                elif isinstance(row_value, np.float64):
                    value+= (float(row_value),)
                else:
                    value+= (row_value,)
        print(sql)
        cursor.execute(sql, value)
    connection.commit()
    return "%s rows of Data were imported!" % (i+1)