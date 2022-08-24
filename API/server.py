from flask import Flask, jsonify, request
import mysql.connector

# python -m pip install mysql-connector-python

NOME_BANCO_DADOS = 'leitor_cartao'
NOME_TABLE = 'dados'
RESPOSTA_TABLE = 'respostas'
USERNAME = 'root'
PASSWORD = 'Germaneagle_12'
HOST = 'localhost'
ERROR_MESSAGE = 'Invalid ID (Non Integer or Database select failed)'

# CREATE TABLE dados (
# 	ID VARCHAR(100),
#     QUESTAO TINYINT,
#     LETRA TINYINT,
#     RAIO SMALLINT UNSIGNED,
#     X SMALLINT UNSIGNED,
#     Y SMALLINT UNSIGNED,
#     PRIMARY KEY (ID, QUESTAO, LETRA)
# );

# CREATE TABLE respostas (
# 	ID VARCHAR(100),
#     QUESTAO TINYINT,
#     LETRA TINYINT,
#     PRIMARY KEY (ID, QUESTAO)
# );


###### API ######

app = Flask(__name__)

@app.route('/')
def showAll():
  global db
  data = showAllId(db)
  return jsonifyId(data)

@app.route('/<id>', methods=['GET', 'POST'])
def selectById(id):
  global db
  
  if request.method=='GET':
    data = selectAllDataById(db, id)
    return jsonifyData(data, id)
  
  elif request.method=='POST':
    content = request.json
    rowsAffected = insertData(db, id, content['points'], content['raios'], content['questoes'], content['letras'])
    resposta = {'response': 'Sucesso', 'rowsAffected': rowsAffected}
    return jsonify(resposta)


@app.route('/respostas/<id>', methods=['GET', 'POST'])
def selectRespostasById(id):
  global db
  
  if request.method=='GET':
    data = selectRespostaById(db, id)
    return jsonifyRespostas(data, id)
  
  elif request.method=='POST':
    content = request.json
    rowsAffected = insertResposta(db, id, content['questoes'], content['letras'])
    resposta = {'response': 'Sucesso', 'rowsAffected': rowsAffected}
    return jsonify(resposta)


###### END API ######

###### DATABASE ######

def initializeDatabase(user, password, database, host='localhost'):
  return mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=database
  )
  

def selectRespostaById(db, id):
  try:
    int(id)
    cursor = db.cursor()
    sql = f"SELECT id, questao, letra FROM {RESPOSTA_TABLE} WHERE id={id}"
    cursor.execute(sql)
    return cursor.fetchall()
  
  except:
    return ERROR_MESSAGE


def selectAllData(db):
  cursor = db.cursor()
  sql = f"SELECT * FROM {NOME_TABLE}"
  cursor.execute(sql)
  return cursor.fetchall()


def showAllId(db):
  cursor = db.cursor()
  sql = f"SELECT DISTINCT id FROM {NOME_TABLE}"
  cursor.execute(sql)
  return cursor.fetchall()


def selectAllDataById(db, id):
  
  try:
    int(id) # verificar se é int, se não, 
    cursor = db.cursor()
    sql = f"SELECT id, x, y, raio, questao, letra FROM {NOME_TABLE} WHERE id={id}" # VUNERAVEL A ATAQUES SQL
    cursor.execute(sql)
    return cursor.fetchall()
  
  except:
    return ERROR_MESSAGE


def insertData(db, id, points, raios, questoes, letras):
  
  try: 
    int(id)
    cursor = db.cursor()
    
    for point, raio, questao, letra in zip(points, raios, questoes, letras):
      sql = f"INSERT INTO {NOME_TABLE}"+" (id, x, y, raio, questao, letra) VALUES (%s, %s, %s, %s, %s, %s)"
      val = (id, point[0], point[1], raio, questao, letra)
      cursor.execute(sql, val)
    newRows = cursor.rowcount
    db.commit()
    return newRows
  
  except:
    return 0
  
def insertResposta(db, id, questoes, letras):
  
  try: 
    int(id)
    cursor = db.cursor()
    
    for questao, letra in zip(questoes, letras):
      sql = f"INSERT INTO {RESPOSTA_TABLE}"+" (id, questao, letra) VALUES (%s, %s, %s)"
      val = (id, questao, letra)
      cursor.execute(sql, val)
    newRows = cursor.rowcount
    db.commit()
    return newRows
  
  except:
    return 0
  

def jsonifyRespostas(dados, id):
  result = {
  'id': id,
  'questao': [],
  'letra': [],
  }
  
  if dados == ERROR_MESSAGE:
    result['id'] = dados
    return jsonify(result)
  
  for id, questao, letra in dados:
    result['questao'].append(questao)
    result['letra'].append(letra)
  return jsonify(result)
  

def jsonifyData(data, id):
  result = {
    'id': id,
    'questao': [],
    'letras': [],
    'points': [],
    'raios': []
  }
  
  if data == ERROR_MESSAGE:
    result['id'] = data
    return jsonify(result)
  
  for (id, x, y, raio, questao, letra) in data:
    result['points'].append((x,y))
    result['questao'].append(questao)
    result['letras'].append(letra)
    result['raios'].append(raio)
  return jsonify(result)


def jsonifyId(data, text='Lista de IDs'):
  result = {
    text: []
  }
  
  for id in data:
    result[text].append(id)
  return jsonify(result)

###### END DATABASE ######

db = initializeDatabase(USERNAME, PASSWORD, NOME_BANCO_DADOS, HOST)

if __name__ == '__main__':
  app.run(debug=True)