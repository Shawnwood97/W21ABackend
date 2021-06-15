import mariadb
from flask_cors import CORS
import traceback
import json
from flask import Flask, request, Response
import db
# import bjeorn


app = Flask(__name__)
CORS(app)


@app.get('/posts')
def get_posts():
  posts = db.run_query(
      "SELECT title, content, id, user_id FROM blog_post")
  if(posts == None):
    return Response('Error getting items from DB', mimetype='text/plain', status=500)
  else:
    posts_json = json.dumps(posts, default=str)
    return Response(posts_json, mimetype='application/json', status=200)


@app.post('/posts')
def add_post():
  try:
    post_title = str(request.json['postTitle'])
    post_content = str(request.json['postContent'])
    user_id = int(request.json['userId'])

  except ValueError:
    traceback.print_exc()
    return Response("Error: One or more of the values is bad!", mimetype="text/plain", status=422)
  except:
    traceback.print_exc()
    return Response("Error: Unknown error with an input!", mimetype="text/plain", status=400)

  # INSERT Query
  q_str = "INSERT INTO blog_post (title, content, user_id) VALUES (?,?,?)"
  # Starting point for valid params to pass to function
  v_params = []

  v_params.extend((post_title, post_content, user_id))

  # if insert works it will be a positive number or 0, it cant be negative (int unsigned)
  new_id = -1
  try:
    new_id = db.run_query(q_str, v_params)

  except mariadb.InternalError:
    traceback.print_exc()
    return Response("Internal Server Error: Failed to create post", mimetype="text/plain", status=500)
  except mariadb.IntegrityError:
    traceback.print_exc()
    return Response("Error: Possible duplicate data or foreign key conflict!", mimetype="text/plain", status=409)

  except:
    traceback.print_exc()
    print("Error with POST!")

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


@app.patch('/posts')
def edit_post():
  try:
    post_title = str(request.json.get('postTitle'))
    post_content = str(request.json.get('postContent'))
    post_id = int(request.json['postId'])

  except ValueError:
    traceback.print_exc()
    return Response("Error: Something wrong with a user input", mimetype="text/plain", status=422)
  except:
    traceback.print_exc()
    return Response("Error: Unknown error with input!", mimetype="text/plain", status=400)

  # start of an UPDATE Query
  q_str = "UPDATE blog_post SET"
  # Starting point for valid params to pass to function
  v_params = []

# this stops empty values from passing to the DB, but still shows success, gotta think of the proper way to do this as when more data gets added, it
# will get much harder to maintain if I just do a generic IF statement after both to see if all are empty or None.
  if(post_title != str(None) and post_title != ''):
    q_str += " title = ?,"
    v_params.append(post_title)
  if(post_content != str(None) and post_content != ''):
    q_str += " content = ?,"
    v_params.append(post_content)

  v_params.append(post_id)

  q_str = q_str[:-1]
  q_str += " WHERE id = ?"

  try:
    update = db.run_query(q_str, v_params)
    #! if here so that we don't run this if update != 0
    if(update != 0):
      #! is data comparison for only updating if changed better done using state on the front end, or using SQL comparision? I assume this depends
      #! if you already have the data on your front end? ie. Posts could be stored in the store since we get them on page load and referenced using
      #! js coniditionals, to stop the query from even being triggered, rather than comparing the data in SQL.

      updated_info = db.run_query(
          "SELECT id, title, content, user_id FROM blog_post WHERE id = ?", [post_id, ])
    else:
      traceback.print_exc()
      return Response("Failed to update", mimetype="text/plain", status=400)

  except mariadb.InternalError:
    # Basic 500 seems like an okay error here.
    traceback.print_exc()
    return Response("Internal Server Error: Failed to update post title", mimetype="text/plain", status=500)
  except mariadb.IntegrityError as e:
    # I think 409 fits well here, since it should be caused by a conflict like a duplicate, or foreign key issue, seems like a client issue, not a server issue?
    traceback.print_exc()
    print(e.msg)
    return Response("Error: Possible duplicate data or foreign key conflict!", mimetype="text/plain", status=409)

  except:
    traceback.print_exc()
    print("Error with PATCH!")

  # 1 row should still work here! Added that the result also needed data, unsure if I still need new_animal condition, but more explicit cant be that bad, rightttt?
  if(updated_info != None):
    updated_post_json = json.dumps(updated_info, default=str)
    print(updated_post_json)
    return Response(updated_post_json, mimetype="application/json", status=201)
  else:
    traceback.print_exc()
    return Response("Failed to update", mimetype="text/plain", status=400)


@app.delete('/posts')
def delete_post():
  try:
    post_id = int(request.json['postId'])
    user_id = int(request.json['userId'])

  except ValueError:
    traceback.print_exc()
    return Response("Error: ID Input was not a whole number", mimetype="text/plain", status=403)
  except:
    traceback.print_exc()
    return Response("Error: Unknown error with input!", mimetype="text/plain", status=400)

  deleted_item = 0
  try:

    deleted_item = db.run_query(
        "DELETE FROM blog_post WHERE id = ? AND user_id = ?", [post_id, user_id])

  except mariadb.InternalError:
    # Basic 500 seems like an okay error here,
    traceback.print_exc()
    return Response("Internal Server Error: Failed to delete animal", mimetype="text/plain", status=500)
  except mariadb.IntegrityError:

    traceback.print_exc()
    return Response("Error: Possible duplicate data or foreign key conflict!", mimetype="text/plain", status=409)

  except:
    traceback.print_exc()
    print("Error with DELETE!")

  if(deleted_item == 1):
    # having this as 204 prevented it from actually displaying "Post Deleted!" #! Assume this is because 204 = No Content?!
    return Response(f"{deleted_item} Post Deleted!", mimetype="text/plain", status=200)
  else:
    return Response("Failed to delete animal", mimetype="text/plain", status=400)


app.run(debug=True)
# bjeorn.run()
