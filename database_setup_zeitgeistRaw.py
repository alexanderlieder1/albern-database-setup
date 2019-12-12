# Quick creation of a PostgreSQL database locally:
# 1) Downloading PostgreSQL
# 2) Make a server using pgAdmin with name = local, host = localhost, port = 5432, maintenance db = postgres, username = postgres, pw = albernzeitgeist
# 3) Create a new database called zeitgeistRaw
# Now we can connect to this database and execute queries using psycopg2

# Steps to populate a relational database from JSON: https://codereview.stackexchange.com/questions/200422/store-nested-json-repsonses-in-relational-database

import psycopg2
import requests
import json

### Dummy tables to explain table structures
# PK is email
CREATE TABLE userDetails ( user_id SERIAL,
                     first_name TEXT,
                     last_name TEXT,
                     email TEXT );

# PK is session_id
# Adding meta data?! responses[0]['metadata']
CREATE TABLE sessionDetails ( session_id SERIAL,
                     session_token_id TEXT,
                     landed_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                     submitted_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                     email TEXT );

# Compound Key is session_token_id+question_id
CREATE TABLE skillTestResults ( session_token_id TEXT,
                     question_id TEXT,
                     user_answer TEXT );

# Compound Key is session_token_id+category
CREATE TABLE skillTestSelfEvaluation ( session_token_id TEXT,
                     category TEXT,
                     user_evaluation TEXT );

# Compound Key is session_token_id+optional_info_id
CREATE TABLE skillTestOptional ( session_token_id TEXT,
                     optional_info_question TEXT, # this field is missing, manual input needed
                     optional_info_id TEXT,
                     optional_info_answer TEXT );

# PK is question_id / this table needs to be build manually. Suggestion is
# to create 3 new test responses (beginner, intermediate, advanced) with
# the right answers. Then the table can be created using following category setup:
# Questions 4-7: ML
# Questions 9-12: Maths
# Questions 14-18: Analytics
# Questions 20-23: Programming
CREATE TABLE testQuestions ( question_id TEXT,
                     correct_answer TEXT,
                     category );

# Connecting to typeform API to get the Data Science Skill survey results
token = 'xxxxxxxxx' #substitutewith token

headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': 'Bearer %s' % token,
    'cache-control': 'no-cache'
}

formsResponse = requests.request(
    'GET',
    'https://api.typeform.com/forms/xxxxx/responses', #substitute xxxxx with formid
    data='',
    headers=headers
)

responses = json.loads(formsResponse.text).get('items', [])
print(responses[0])

### Extracting fields for all tables in database_setup (example using 1 response '[0]')
# Fields for userDetails table
first_name = responses[0]['answers'][0]['text']
last_name = responses[0]['answers'][1]['text']
email = responses[0]['answers'][2]['email']

# Fields for sessionDetails
session_token_id = responses[0]['token']
landed_timestamp = responses[0]['landed_at']
submitted_timestamp = responses[0]['submitted_at']
email = responses[0]['answers'][2]['email']

# Fields for skillTestResults
session_token_id = responses[0]['token']
#only using 'real' questions with multiple choice to assess skills
multiple_choice_questions = [4,5,6,7,9,10,11,12,14,15,16,17,18,20,21,22,23]
for i in multiple_choice_questions:
    question_id = responses[0]['answers'][i]['field']['id']
    user_answer = responses[0]['answers'][i]['choice']['label']
    print(question_id)
    print(user_answer)

# Fields for skillTestSelfEvaluation
session_token_id = responses[0]['token']
#only using 'picture' questions to get self_evaluation
self_evaluation_questions = [3,8,13,19]
self_evaluation_categories = ['ML','Maths','Analytics','Programming']
for i in self_evaluation_questions:
    category = self_evaluation_categories[self_evaluation_questions.index(i)]
    user_evaluation = responses[0]['answers'][i]['choice']['label']
    print(category)
    print(user_evaluation)

# Fields for skillTestOptional
session_token_id = responses[0]['token']
#only using 'optional' questions
optional_questions = [24,25,27,28,29,30,31,32,33,34,35,36]
# only get information, if user decided to fill out optional part of survey
if responses[0]['answers'][26]['boolean'] == True:
    for i in optional_questions:
        if responses[0]['answers'][i]['field']['type'] == 'picture_choice':
            optional_info_id = responses[0]['answers'][i]['field']['id']
            optional_info_answer = responses[0]['answers'][i]['choice']['label']
        elif responses[0]['answers'][i]['field']['type'] in ['short_text','dropdown']:
            optional_info_id = responses[0]['answers'][i]['field']['id']
            optional_info_answer = responses[0]['answers'][i]['text']
        elif responses[0]['answers'][i]['field']['type'] == 'multiple_choice':
            optional_info_id = responses[0]['answers'][i]['field']['id']
            optional_info_answer = responses[0]['answers'][i]['choices']['labels']
        elif responses[0]['answers'][i]['field']['type'] == 'yes_no':
            optional_info_id = responses[0]['answers'][i]['field']['id']
            optional_info_answer = responses[0]['answers'][i]['boolean']
        else:
            optional_info_id = responses[0]['answers'][i]['field']['id']
            optional_info_answer = responses[0]['answers'][i]['number']

        # print example results
        print(optional_info_id)
        print(optional_info_answer)
