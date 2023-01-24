from flask import Flask, jsonify, json, request
from flask_cors import CORS, cross_origin
import psycopg2
import collections

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

conn = psycopg2.connect(database="demo",
                        host="database",
                        user="demo",
                        password="demo",
                        port="5432")

@app.route('/')
def hello():
    return 'Hello, World!'

def obj_dict(obj):
    return obj.__dict__

@app.post("/login")
def login() :
    if False == request.is_json:
      return {"error": "Request must be JSON"}, 415

    username = request.get_json()['username']
    password = request.get_json()['password']

    cursor = conn.cursor()

    # ' or 1=1 --
    try:
      req = "SELECT * FROM users WHERE username = '"+username+"' and password = '"+password+"'"
      print(req)
      cursor.execute(req)
    except :
       conn.rollback()
       cursor.close()
       return build401Unauthorize("unauthorized")

    records = cursor.fetchall()
    cursor.close()

    if not records :
      return build401Unauthorize("unauthorized")
    else :
      return build200Response("authenticated")
    


@app.get("/produits")
def produits() :
    args = request.args 
    nomRequest = args.get("nom")

    cursor = conn.cursor()
    req = "SELECT nom, description FROM produits"

    if nomRequest:
      req = "SELECT nom, description FROM produits where nom = '" + nomRequest +"'"

    try:
      print(req)
      cursor.execute(req)
    except :
       conn.rollback()
       cursor.close()
       return build401Unauthorize("unauthorized")

    records = cursor.fetchall()
    cursor.close()

    objects_list = []
    for row in records:
        d = collections.OrderedDict()
        d['nom'] = row[0]
        d['description'] = row[1]
        objects_list.append(d)

    j = json.dumps(objects_list)

    return build200Response(j)


def initDatabase() : 
    
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (username VARCHAR(100), password VARCHAR(100));")
    cursor.close()

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users;")
    records = cursor.fetchall()
    cursor.close()

    if not records :
      cursor = conn.cursor()
      cursor.execute("INSERT INTO users (username, password) VALUES('admin', 'azdsqdx65ax4azxa')")
      cursor.execute("INSERT INTO users (username, password) VALUES('user1', 'gcsdze165')")
      cursor.execute("INSERT INTO users (username, password) VALUES('user2', 'htr56465dqsx@')")
      conn.commit()
      cursor.close()
      print("empty users")
    else :
      print("exist")

    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS produits (nom VARCHAR(100), description VARCHAR(100));")
    cursor.close()

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produits;")
    records = cursor.fetchall()
    cursor.close()

    if not records :
      cursor = conn.cursor()
      cursor.execute("INSERT INTO produits (nom, description) VALUES('produit 1', 'Un premier produit')")
      cursor.execute("INSERT INTO produits (nom, description) VALUES('produit 2', 'Et un second produit')")
      cursor.execute("INSERT INTO produits (nom, description) VALUES('produit 3', 'Et de trois')")
      conn.commit()
      cursor.close()
      print("empty produits")
    else :
      print("exist")

    

initDatabase()

def build200Response(obj : any):
  # json.dumps(obj, default=obj_dict),
  return app.response_class(
      response=obj,
      status=200,
      mimetype='application/json',
      headers={"Access-Control-Allow-Origin":"*"})


def build401Unauthorize(obj : any):
  return app.response_class(
      response=json.dumps(obj, default=obj_dict),
      status=401,
      mimetype='application/json',
      headers={"Access-Control-Allow-Origin":"*"})


if __name__ == "__main__":
    app.run()