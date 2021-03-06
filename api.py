from flask import Flask, render_template, request
import pymysql
import requests
import json
import pandas as pd
import numpy as np
import datetime

column_dict = {'school_name': 'SCHOOL_NAME LIKE ', 'rank1': 'WORLD_RANKING>=', 'rank2': 'WORLD_RANKING<=',
                 'states':'STATE in ', 
                 'degree': 'DEGREE LIKE ', 'tuition1': '`TUITION_($)` >=', 'tuition2': '`TUITION_($)` <=',
                 'salary1': '`AVERAGE_STARTING_SALARY_($)` >=', 'salary2': '`AVERAGE_STARTING_SALARY_($)` <=',
                 'department_name': 'DEPARTMENT=',
                 'sources': 'SOURCE IN ',
                 'city_name': 'CITY_NAME=', 'pop1': 'POPULATION >=', 'pop2': 'POPULATION <=', 'tem1': '`AVERAGE_TEMP_(°F)` >=', 'tem2': '`AVERAGE_TEMP_(°F)` <=',
                 'crime1': '`VIOLENT_CRIME_(PER_100,000_PEOPLE)` <=', 'crime2': '`VIOLENT_CRIME_(PER_100,000_PEOPLE)` >=',
                 'house2': '`MONTHLY_HOUSING_COSTS_($)` <=', 'house1': '`MONTHLY_HOUSING_COSTS_($)` >=',
                 'specialty': 'SPECIALTY = ', 'size1': 'SIZE >=', 'size2': 'SIZE <=', 'ar1': 'ACCEPTANCE_RATE >=',
                 'ar2': 'ACCEPTANCE_RATE <=', 'campus1': '`AREA_SIZE_(ACRE)` >=', 'campus2' :'`AREA_SIZE_(ACRE)` <=', 
                 'sat1':'50TH_PERCENTILE_SAT >=', 'sat2': '50TH_PERCENTILE_SAT <=', 'act1':'50TH_PERCENTILE_ACT >=', 'act2': '50TH_PERCENTILE_ACT <='
                 }

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='password',
                             db='info257_database',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3

def myconverter(o):
    if isinstance(o, datetime.date):
        return o.__str__()

def create_links_table():
    with connection.cursor() as cursor:
        #cursor.execute("DROP TABLE IF EXISTS `ADMISSION_STATS`")
        #cursor.execute("DROP TABLE IF EXISTS `CITY_STATS`")
        #cursor.execute("DROP TABLE IF EXISTS `PROFESSOR_STATS`")
        #cursor.execute("DROP TABLE IF EXISTS `PROGRAM_STATS`")
        #cursor.execute("DROP TABLE IF EXISTS `RANKING`")
        #cursor.execute("DROP TABLE IF EXISTS `SCHOOL_STATS`")
        cursor.execute("CREATE TABLE IF NOT EXISTS `ADMISSION_STATS` (`SCHOOL_NAME` varchar(50) NOT NULL,`YEAR` int(11) DEFAULT NULL,`ACCEPTANCE_RATE` float DEFAULT NULL,`25TH_PERCENTILE_SAT` float DEFAULT NULL,`50TH_PERCENTILE_SAT` float DEFAULT NULL,`75TH_PERCENTILE_SAT` float DEFAULT NULL,`25TH_PERCENTILE_ACT` float DEFAULT NULL,`50TH_PERCENTILE_ACT` float DEFAULT NULL,`75TH_PERCENTILE_ACT` float DEFAULT NULL,`SIZE` float DEFAULT NULL,PRIMARY KEY (`SCHOOL_NAME`))")
        cursor.execute("CREATE TABLE IF NOT EXISTS `CITY_STATS` (`CITY_NAME` varchar(50) NOT NULL,`STATE_NAME` varchar(10) DEFAULT NULL,`POPULATION` int(11) DEFAULT NULL,`AVERAGE_TEMP_(°F)` float DEFAULT NULL,`PRECIPITATION_(INCHES)` float DEFAULT NULL,`VIOLENT_CRIME_(PER_100,000_PEOPLE)` float DEFAULT NULL,`PROPERTY_CRIME_(PER_100,000_PEOPLE)` float DEFAULT NULL,`TOTAL_CRIME_(PER_100,000_PEOPLE)` float DEFAULT NULL,`FATALITY_(PER_100,000_PEOPLE)` float DEFAULT NULL,`MONTHLY_HOUSING_COSTS_($)` float DEFAULT NULL,PRIMARY KEY (`CITY_NAME`))")
        cursor.execute("CREATE TABLE IF NOT EXISTS `PROFESSOR_STATS` (`PROFESSOR_NAME` varchar(50) NOT NULL,`SCHOOL_NAME` varchar(50) DEFAULT NULL,`DEPARTMENT` varchar(50) DEFAULT NULL,`SPECIALTY` varchar(100) DEFAULT NULL,`RATINGS` float DEFAULT NULL,`TITLE` varchar(50) DEFAULT NULL,PRIMARY KEY (`PROFESSOR_NAME`))")
        cursor.execute("CREATE TABLE IF NOT EXISTS `PROGRAM_STATS` (`SCHOOL_NAME` varchar(50) NOT NULL,`DEPARTMENT` varchar(50) NOT NULL,`DEGREE` varchar(10) NOT NULL,`TUITION_($)` int(11) DEFAULT NULL,`AVERAGE_LENGTH_(YEAR)` int(11) DEFAULT NULL,`AVERAGE_STARTING_SALARY_($)` int(11) DEFAULT NULL,PRIMARY KEY (`SCHOOL_NAME`,`DEPARTMENT`,`DEGREE`))")
        cursor.execute("CREATE TABLE IF NOT EXISTS `RANKING` (`SOURCE` varchar(50) NOT NULL,`SCHOOL_NAME` varchar(50) NOT NULL,`WORLD_RANKING` int(11) DEFAULT NULL,`YEAR` int(11) DEFAULT NULL,PRIMARY KEY (`SOURCE`,`SCHOOL_NAME`))")
        cursor.execute("CREATE TABLE IF NOT EXISTS `SCHOOL_STATS` (`SCHOOL_NAME` varchar(50) NOT NULL,`AREA_SIZE_(ACRE)` float DEFAULT NULL,`CITY` varchar(50) DEFAULT NULL,`APPLICATION_FEE_($)` int(11) DEFAULT NULL,`EARLY_ACTION_DEADLINE` date DEFAULT NULL, `STATE` varchar(10) DEFAULT NULL,`REGULAR_DEADLINE` date DEFAULT NULL,PRIMARY KEY (`SCHOOL_NAME`))")
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
        school_name = ['school_name', '%' + request.args.get('school_name') + '%']
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
        act1 = ['act1', request.args.get('act1')]
        act2 = ['act2', request.args.get('act2')]
        states_list = request.args.getlist('states')
        if len(states_list)==1:
            states_list = "('" + str(states_list[0])+"')"
        else:
            states_list = tuple(states_list)
        states = ['states', states_list]
        conditions = [school_name, tuition1, tuition2, states, ar1, ar2, size1, size2, campus1, campus2, sat1, sat2,act1,act2]
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
        return json.dumps(schools, default = myconverter)

@app.route('/get_programs', methods = ['GET'])
def get_programs():
    with connection.cursor() as cursor:
        department_name = ['department_name', request.args.get('department_name')]
        degree = ['degree', request.args.get('degree')]
        tuition1 = ['tuition1', request.args.get('tuition1')]
        tuition2 = ['tuition2', request.args.get('tuition2')]
        salary1 = ['salary1', request.args.get('salary1')]
        salary2 = ['salary2', request.args.get('salary2')]
        school_name = ['school_name', '%' + request.args.get('school_name') + '%']
        #if condtion is not empty, then append sql
        conditions = [department_name, school_name, salary1, salary2, degree, tuition1, tuition2]
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
        school_name = ['school_name', '%' + request.args.get('school_name') + '%']
        source = request.args.getlist('source')
        rank1 = ['rank1', request.args.get('rank1')]
        rank2 = ['rank2', request.args.get('rank2')]
        #if condtion is not empty, then append sql
        if len(source)==1:
            source = "('" + str(source[0])+"')"
        else:
            source = tuple(source)
        sources = ['sources', source]
        conditions = [sources, school_name, rank1, rank2]
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

        return json.dumps(cities)

@app.route('/get_professors', methods = ['GET'])
def get_professors():
    with connection.cursor() as cursor:
        print('in api')
        school_name = ['school_name', '%' + request.args.get('school_name') + '%']
        department_name = ['department_name', request.args.get('department_name')]
        specialty = ['specialty', request.args.get('specialty')]
        states_list = request.args.getlist('states')
        if len(states_list)==1:
            states_list = "('" + str(states_list[0])+"')"
        else:
            states_list = tuple(states_list)
        states = ['states', states_list]

        source = request.args.getlist('source')
        #if condtion is not empty, then append sql
        if len(source)==1:
            source = "('" + str(source[0])+"')"
        else:
            source = tuple(source)
        conditions = [school_name, department_name, specialty, states]
        not_empty_conditions = []
        sql = "SELECT PROFESSOR_STATS.* FROM PROFESSOR_STATS INNER JOIN SCHOOL_STATS ON PROFESSOR_STATS.SCHOOL_NAME = SCHOOL_STATS.SCHOOL_NAME WHERE "
        for condition in conditions:
            if condition[1]:
                not_empty_conditions.append(condition)
        
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
        professors = list()
        for i in range(len(results)):
            professor = results[i]
            professors.append(professor)
        return json.dumps(professors)

@app.route('/search/advanced', methods = ['POST'])
def advanced_search():
    with connection.cursor() as cursor:
        interest = request.args.get('interest')
        school_name = ['school_name', '%' + request.args.get('school_name') + '%']
        department_name = ['department_name', request.args.get('department_name')]
        specialty = ['specialty', request.args.get('specialty')]
        source = request.args.getlist('source')
        if len(source)==1:
            source = "('" + str(source[0])+"')"
        else:
            source = tuple(source)
        sources = ['sources', source]
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
        rank1 = ['rank1', request.args.get('rank1')]
        rank2 = ['rank2', request.args.get('rank2')]
        department_name = ['department_name', request.args.get('department_name')]
        degree = ['degree', request.args.get('degree')]
        tuition1 = ['tuition1', request.args.get('tuition1')]
        tuition2 = ['tuition2', request.args.get('tuition2')]
        salary1 = ['salary1', request.args.get('salary1')]
        salary2 = ['salary2', request.args.get('salary2')]
        ar1 = ['ar1', request.args.get('ar1')]
        ar2 = ['ar2', request.args.get('ar2')]
        size1 = ['size1', request.args.get('size1')]
        size2 = ['size2', request.args.get('size2')]
        campus1 = ['campus1', request.args.get('campus1')]
        campus2 = ['campus2', request.args.get('campus2')]
        sat1 = ['sat1', request.args.get('sat1')]
        sat2 = ['sat2', request.args.get('sat2')]
        act1 = ['act1', request.args.get('act1')]
        act2 = ['act2', request.args.get('act2')]
        attributes = request.args.getlist('attributes')
        attribute_list = list(attributes)

        conditions = [salary1, salary2, rank1, rank2, degree, tuition1, tuition2,sources, school_name, rank1, rank2, 
        city_name, states, pop1, pop2, tem1, tem2, crime1, crime2, house1, house2,school_name, department_name, specialty,
        ar1, ar2, size1, size2, campus1, campus2, sat1, sat2,act1,act2]
        not_empty_conditions = []
        desired_attributes =  []
        alias_names = ['a','b','c','d']
        default_cols = "SCHOOL_NAME"
        dc = ['SCHOOL_NAME']
        if interest == "PROGRAM_STATS":
            default_cols += ',DEPARTMENT, DEGREE'
            dc.append('DEPARTMENT')
            dc.append('DEGREE')
        default_cols += ',CITY, STATE'
        dc.append('CITY')
        dc.append('STATE')

        for condition in conditions:
            if condition[1]:
                
                if condition[0] == 'degree' and interest == 'SCHOOL_STATS':
                    continue
                else:
                    desired_attributes.append(condition[0])
                    not_empty_conditions.append(condition)


        current_table_name = interest


        if interest == "PROGRAM_STATS":
            name = alias_names.pop()            
            interest = "(SELECT SCHOOL_STATS.*, DEPARTMENT, DEGREE, `AVERAGE_LENGTH_(YEAR)`, `AVERAGE_STARTING_SALARY_($)` FROM PROGRAM_STATS INNER JOIN SCHOOL_STATS ON PROGRAM_STATS.SCHOOL_NAME = SCHOOL_STATS.SCHOOL_NAME) as " + name 
            current_table_name = name
        sql_table = interest

        if any(x in ['POPULATION','`AVERAGE_TEMP_(°F)`','`VIOLENT_CRIME_(PER_100,000_PEOPLE)`','`MONTHLY_HOUSING_COSTS_($)`'] for x in attribute_list) or any(x in ['pop1','pop2', 'crime1','crime2','house1','house2','tem1','tem2'] for x in desired_attributes):
            name = alias_names.pop()
            sql_table = "(SELECT " + current_table_name + ".*, POPULATION, `AVERAGE_TEMP_(°F)`, `VIOLENT_CRIME_(PER_100,000_PEOPLE)`, `MONTHLY_HOUSING_COSTS_($)` FROM CITY_STATS INNER JOIN " + sql_table + " ON CITY_STATS.CITY_NAME = " + current_table_name + ".CITY) as " + name
            current_table_name = name

        admiss_attr = intersection(['ACCEPTANCE_RATE, 50TH_PERCENTILE_SAT, 50TH_PERCENTILE_ACT, SIZE'], attribute_list)
        
        if (len(admiss_attr) > 0 or len(intersection(desired_attributes,['sat1','sat2', 'act1','act2','size1','size2','ar1','ar2'])) > 0):
            name = alias_names.pop()
            sql_table = "(SELECT " + current_table_name + ".*, ACCEPTANCE_RATE, 50TH_PERCENTILE_SAT, 50TH_PERCENTILE_ACT, SIZE FROM " + sql_table + " INNER JOIN ADMISSION_STATS ON " + current_table_name + ".SCHOOL_NAME" + " = ADMISSION_STATS.SCHOOL_NAME ) as " + name
        attribute_list =  ", ".join(attribute_list)
        attribute_list = ", " + attribute_list
        print('attributes list', attribute_list)

        sql = "SELECT " + default_cols + attribute_list + ", EARLY_ACTION_DEADLINE, REGULAR_DEADLINE, `APPLICATION_FEE_($)` FROM " + sql_table + " WHERE " 

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
        res = list()
        for i in range(len(results)):
            r = results[i]
            res.append(r)
        print(res)
        final_results = [res, dc, attributes]
        return json.dumps(final_results, default = myconverter)


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
                if str(row_value) != 'nan':
                    if isinstance(row_value, np.int64):
                        value+= (int(row_value),)
                    elif isinstance(row_value, np.float64):
                        value+= (float(row_value),)
                    else:
                        value+= (row_value,)
                else:
                    value+= (None,)
        print(sql)
        cursor.execute(sql, value)
    connection.commit()
    return json.dumps("%s rows of " % (i+1)+ table+ " Data were imported!" )