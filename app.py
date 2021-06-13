import db
from flask import Flask, request, Response
import json
import traceback
from flask_cors import CORS
import mariadb
# import bjeorn


app = Flask(__name__)
CORS(app)


@app.get('/posts')
def get_posts():
  request = db.api_request(
      "SELECT title, content, id, user_id FROM blog_post")
  if(request == None):
    return Response('Error getting items from DB', mimetype='text/plain', status=500)

  else:
    items_json = json.dumps(request, default=str)
    return Response(items_json, mimetype='application/json', status=200)


@app.post('/posts')
def add_post():
  try:
    post_title = str(request.json['postTitle'])
    post_content = str(request.json['postContent'])
    user_id = int(request.json['userId'])

  except ValueError:
    traceback.print_exc()
    return Response("Error: One of the values is bad!", mimetype="text/plain", status=422)
  except:
    traceback.print_exc()
    return Response("Error: Unknown error with an input!", mimetype="text/plain", status=400)

  conn = db.openConnection()
  cursor = db.openCursor(conn)

  # if insert works it will be a positive number or 0, it cant be negative (int unsigned)
  new_id = -1
  try:
    cursor.execute(
        "INSERT INTO blog_post (title, content, user_id) VALUES (?, ?, ?)", [post_title, post_content, user_id])
    conn.commit()
    new_id = cursor.lastrowid

  except mariadb.InternalError:
    traceback.print_exc()
    return Response("Internal Server Error: Failed to create post", mimetype="text/plain", status=500)
  except mariadb.IntegrityError:
    traceback.print_exc()
    return Response("Error: Possible duplicate data or foreign key conflict!", mimetype="text/plain", status=409)

  except:
    traceback.print_exc()
    print("Error with POST!")

  db.closeAll(conn, cursor)

  # if newly added id == a negative number, fail
  if(new_id != -1):
    new_post_json = json.dumps(
        {
            "title": post_title,
            "content": post_content,
            "user_id": user_id,
            "id": new_id
        }, default=str)
    return Response(new_post_json, mimetype="application/json", status=201)
  else:
    return Response("Failed to create post", mimetype="text/plain", status=400)


app.run(debug=True)
# bjeorn.run()
